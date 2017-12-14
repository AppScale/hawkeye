package com.appscale.hawkeye.memcache;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.memcache.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Future;
import java.util.logging.Level;


public class MemcacheHandlerServlet extends HttpServlet {

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String key = request.getParameter("key");
        String value = request.getParameter("value");
        String update = request.getParameter("update");
        String timeoutString = request.getParameter("timeout");
        String async = request.getParameter("async");

        int timeout = 3600;
        if (timeoutString != null && !"".equals(timeoutString)) {
            timeout = Integer.parseInt(timeoutString);
        }

        boolean success;
        if ("true".equals(async)) {
            AsyncMemcacheService asyncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            Future<Boolean> future;
            if ("true".equals(update)) {
                future = asyncCache.put(key, value, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.SET_ALWAYS);
            } else {
                future = asyncCache.put(key, value, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.ADD_ONLY_IF_NOT_PRESENT);
            }
            try {
                success = future.get();
            } catch (Exception e) {
                throw new ServletException("Error while accessing async memcache service", e);
            }
        } else {
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            if ("true".equals(update)) {
                success = syncCache.put(key, value, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.SET_ALWAYS);
            } else {
                success = syncCache.put(key, value, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.ADD_ONLY_IF_NOT_PRESENT);
            }
        }

        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", success);
        JSONUtils.serialize(map, response);
    }

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String key = request.getParameter("key");
        String async = request.getParameter("async");

        Object value;
        if ("true".equals(async)) {
            AsyncMemcacheService asyncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            asyncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            Future<Object> futureValue = asyncCache.get(key);
            try {
                value = futureValue.get();
            } catch (Exception e) {
                throw new ServletException("Error while accessing async memcache service", e);
            }
        } else {
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            syncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            value = syncCache.get(key);
        }

        if (value != null) {
            Map<String,Object> map = new HashMap<String, Object>();
            map.put("value", value.toString());
            JSONUtils.serialize(map, response);
        } else {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
        }
    }

    protected void doDelete(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String key = request.getParameter("key");
        String async = request.getParameter("async");
        boolean success;
        if ("true".equals(async)) {
            AsyncMemcacheService asyncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            asyncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            Future<Boolean> futureValue = asyncCache.delete(key);
            try {
                success = futureValue.get();
            } catch (Exception e) {
                throw new ServletException("Error while accessing async memcache service", e);
            }
        } else {
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            syncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            success = syncCache.delete(key);
        }

        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", success);
        JSONUtils.serialize(map, response);
    }
}
