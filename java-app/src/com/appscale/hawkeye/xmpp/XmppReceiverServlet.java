package com.appscale.hawkeye.xmpp;

import java.io.IOException;
import javax.servlet.http.*;
import com.google.appengine.api.xmpp.JID;
import com.google.appengine.api.xmpp.Message;
import com.google.appengine.api.xmpp.XMPPService;
import com.google.appengine.api.xmpp.XMPPServiceFactory;
import com.google.appengine.api.datastore.*;
import java.util.logging.Logger;
import java.util.*;
import java.io.*;
import javax.servlet.ServletInputStream;

public class XmppReceiverServlet extends HttpServlet
{
    private static final Logger logger = Logger.getLogger(XmppReceiverServlet.class.getName());
    private String MESSAGE = "pew pew from hawkeye";
    private String MESSAGE_RECEIVED = "message received!";
    private String TEST_KEYNAME = "test";
    private String TEST_ENTITYNAME = "test";
    private String ENTITY_PROPERTY = "state";

    public void doPost(HttpServletRequest req, HttpServletResponse res) throws IOException 
    {
        XMPPService xmpp = XMPPServiceFactory.getXMPPService();
        Message message = xmpp.parseMessage(req);

        JID fromJid = message.getFromJid();
        String body = message.getBody();
        if(!body.equals(MESSAGE))
        {
            logger.warning("Got unexpected message: " + body);
            return;
        }    
        
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Entity entity = new Entity(TEST_ENTITYNAME, TEST_KEYNAME);
        entity.setProperty(ENTITY_PROPERTY, MESSAGE_RECEIVED);
        datastore.put(entity);
    }
}
