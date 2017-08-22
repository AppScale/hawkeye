package com.appscale.hawkeye.envvar;

import com.appscale.hawkeye.JSONUtils;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.EntityNotFoundException;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class GetEntityHandlerServlet extends HttpServlet {

    private DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        Map<String,Object> map = new HashMap<String, Object>();
        if (request.getRequestURL().indexOf("entity") != -1) {
            try {
                Entity entity = datastore.get(KeyFactory.createKey("Entity", request.getParameter("id")));
                map.put("entity", this.renderEntity(entity));
            }
            catch (EntityNotFoundException e) {
                map.put("entity", null);
            }
        }
        else {
            String[] ids = request.getParameterValues("id");
            List<Key> keys = new ArrayList<Key>();
            for (String id : ids)
                keys.add(KeyFactory.createKey("Entity", id));
            Map<Key,Entity> entities = datastore.get(keys);
            List<Map<String,Object>> rendered = new ArrayList<Map<String,Object>>();
            for (Entity entity : entities.values())
                rendered.add(this.renderEntity(entity));
            map.put("entities", rendered);
        }
        JSONUtils.serialize(map, response);
    }

    private Map<String,Object> renderEntity(Entity entity) {
        Map<String,Object> fields_map = new HashMap<String, Object>();
        fields_map.put("id", entity.getKey().getName());
        fields_map.put("created_at_module", entity.getProperty("created_at_module"));
        fields_map.put("created_at_version", entity.getProperty("created_at_version"));
        fields_map.put("new_field", entity.getProperty("new_field"));
        return fields_map;
    }
}
