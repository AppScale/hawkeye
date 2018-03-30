package com.appscale.hawkeye.warmup;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

public class WarmUpCheckServlet extends HttpServlet {
    public void doGet(HttpServletRequest req,
                      HttpServletResponse resp ) throws ServletException, IOException {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        boolean warmUpSuccess;
        try {
            datastore.get(Constants.WARMUP_KEY);
            warmUpSuccess = true;
        } catch (EntityNotFoundException e) {
            warmUpSuccess = false;
        } finally {
            datastore.delete(Constants.WARMUP_KEY);
        }

        Map<String,Object> successResponse = new HashMap<String, Object>();
        successResponse.put("success", warmUpSuccess);
        JSONUtils.serialize(successResponse, resp);
    }
}
