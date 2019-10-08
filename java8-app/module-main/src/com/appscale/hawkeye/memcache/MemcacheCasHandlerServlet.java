package com.appscale.hawkeye.memcache;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.memcache.*;
import com.google.appengine.api.memcache.MemcacheService.IdentifiableValue;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Future;
import java.util.logging.Level;
import java.util.UUID;

public class MemcacheCasHandlerServlet extends HttpServlet {
    protected void doGet(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {
        MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
        String key = UUID.randomUUID().toString();
        syncCache.put(key, "1");
        IdentifiableValue casVal = syncCache.getIdentifiable(key);
        if(((String)casVal.getValue()).equals("1") == false) 
        {
            throw new ServletException("casVal was not expected value of [1], was: " + casVal.getValue());
        }
        boolean success = syncCache.putIfUntouched(key, casVal, "2");
        Map<String, Object> map = new HashMap<String, Object>();
        if(!success)
        {
            throw new ServletException("putIfUntouched returned false, should have returned true");
        }
        
        casVal = syncCache.getIdentifiable(key);
        syncCache.put(key, "1");
        success = syncCache.putIfUntouched(key, casVal, "3");
        if(success == true)
        {
            throw new ServletException("putIfUntouched returned true, should have returned false"); 
        }

        map.put("success", true);
        JSONUtils.serialize(map, response);
    }
}
