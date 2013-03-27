package com.appscale.hawkeye.xmpp;

import com.google.appengine.api.xmpp.*;
import com.google.appengine.api.datastore.*;

import com.appscale.hawkeye.JSONUtils;
import java.util.HashMap;
import java.util.Map;
import java.util.logging.Logger;
import java.io.IOException;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class XmppHandlerServlet extends HttpServlet
{
 
    private static final Logger logger = Logger.getLogger(XmppHandlerServlet.class.getName());
    private String MESSAGE = "pew pew from hawkeye";
    private String NON_EXISTENT = "non-existent";
    private String MESSAGE_SENT = "message sent!";
    private String MESSAGE_RECEIVED = "message received!";
    private String TEST_KEYNAME = "test";
    private String TEST_ENTITYNAME = "test";
    private String ENTITY_PROPERTY = "state";

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException 
    {
        XMPPService xmpp = XMPPServiceFactory.getXMPPService();
        JID jid = new JID(getUserName());
        Message msg = new MessageBuilder()
           .withRecipientJids(jid)
           .withBody(MESSAGE)
           .build();
        SendResponse status = xmpp.sendMessage(msg);
        boolean messageSent = (status.getStatusMap().get(jid) == SendResponse.Status.SUCCESS);
        
        if(messageSent)
        {
            Entity entity = new Entity(TEST_ENTITYNAME, TEST_KEYNAME);
            entity.setProperty(ENTITY_PROPERTY, MESSAGE_SENT);
            DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
            datastore.put(entity);
            Map<String,Object> map = new HashMap<String, Object>();
            map.put("status", true);
            map.put("state", MESSAGE_SENT);
            JSONUtils.serialize(map, response);
        }
        else
        {
            Map<String,Object> map = new HashMap<String, Object>();
            map.put("status", false);
            map.put("state", NON_EXISTENT);
            JSONUtils.serialize(map, response);
        }
    }

    protected void doGet(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException 
    {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Key key = KeyFactory.createKey(TEST_ENTITYNAME, TEST_KEYNAME); 
        Entity entity;
        try
        {
            entity = datastore.get(key);
        }    
        catch(EntityNotFoundException e)
        {
            logger.warning("Entity wasn't found");
            Map<String,Object> map = new HashMap<String, Object>();
            map.put("status", true);
            map.put("state", NON_EXISTENT);
            JSONUtils.serialize(map, response);
            return;
        }

        String state = (String)entity.getProperty(ENTITY_PROPERTY);
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("status", true);
        map.put("state", state);
        JSONUtils.serialize(map, response);
    }

    protected void doDelete(HttpServletRequest request,
                            HttpServletResponse response) throws ServletException, IOException 
    {
        Key key = KeyFactory.createKey(TEST_ENTITYNAME, TEST_KEYNAME); 
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        datastore.delete(key);   
    }

    private String getUserName()
    {
        Map<String, String> env = System.getenv();
        String appId = System.getProperty("APPLICATION_ID");
        String loginServer = System.getProperty("LOGIN_SERVER");
        return appId + "@" + loginServer;
    }
}
