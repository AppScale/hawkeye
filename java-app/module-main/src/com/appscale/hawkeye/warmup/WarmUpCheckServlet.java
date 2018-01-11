package com.appscale.hawkeye.warmup;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.Key;

public class WarmUpCheckServlet extends HttpServlet {
    private String WARMUP_STATUS_KIND = "WARMUP_STATUS";
    private int successCode = 200;
    private int failureCode = 500;


    public void doGet(HttpServletRequest req,
                      HttpServletResponse resp ) throws ServletException, IOException {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        List<Key> keyList = null;
        boolean warmUpSuccess = false;
        try {
            datastore = DatastoreServiceFactory.getDatastoreService();
            Query q = new Query("WarmupStatus");
            PreparedQuery pq = datastore.prepare(q);
            FetchOptions fetchOptions = FetchOptions.Builder.withDefaults();

            List<Entity> entities = new ArrayList<>();
            entities.addAll(pq.asList(fetchOptions));
            keyList = new ArrayList<>();
            for (Entity e : entities) {
                keyList.add(e.getKey());
            }

            warmUpSuccess = testAllSuccess(entities);
        } catch (Exception e) {
            System.out.println("Caught exception " + e.getMessage());
            e.printStackTrace();
            resp.sendError(failureCode, e.getMessage());
            return;
        } finally {
            if (keyList != null) cleanUpData(datastore, keyList);
        }

        Map<String,Object> successResponse = new HashMap<String, Object>();
        successResponse.put("success", warmUpSuccess);
        JSONUtils.serialize(successResponse, resp);
    }

    public boolean testAllSuccess(List<Entity> entities) {
        for (Entity e : entities) {
            if (!(boolean)e.getProperty("success")) {
                return false;
            }
        }
        return true;
    }

    private void cleanUpData(DatastoreService datastore, List<Key> keyList)
    {
        datastore.delete(keyList);
    }

}
