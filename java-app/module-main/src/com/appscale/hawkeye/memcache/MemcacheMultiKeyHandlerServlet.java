package com.appscale.hawkeye.memcache;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.memcache.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.Future;
import java.util.logging.Level;

public class MemcacheMultiKeyHandlerServlet extends HttpServlet {

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String keys = request.getParameter("keys");
        String values = request.getParameter("values");
        String update = request.getParameter("update");
        String timeoutString = request.getParameter("timeout");
        String async = request.getParameter("async");

        String[] keyArray = keys.split(",");
        String[] valueArray = values.split(",");
        Map<String,String> mapping = new HashMap<String, String>();
        for (int i = 0; i < keyArray.length; i++) {
            mapping.put(keyArray[i], valueArray[i]);
        }

        int timeout = 3600;
        if (timeoutString != null && !"".equals(timeoutString)) {
            timeout = Integer.parseInt(timeoutString);
        }

        Set<String> result;
        if ("true".equals(async)) {
            AsyncMemcacheService syncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            Future<Set<String>> future;
            if ("true".equals(update)) {
                future = syncCache.putAll(mapping, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.SET_ALWAYS);
            } else {
                future = syncCache.putAll(mapping, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.ADD_ONLY_IF_NOT_PRESENT);
            }
            try {
                result = future.get();
            } catch (Exception e) {
                throw new ServletException("Error while accessing async memcache service", e);
            }
        } else {
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            if ("true".equals(update)) {
                result = syncCache.putAll(mapping, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.SET_ALWAYS);
            } else {
                result = syncCache.putAll(mapping, Expiration.byDeltaSeconds(timeout),
                        MemcacheService.SetPolicy.ADD_ONLY_IF_NOT_PRESENT);
            }
        }

        boolean success = result.size() == keyArray.length;
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", success);
        JSONUtils.serialize(map, response);
    }

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String keys = request.getParameter("keys");
        String async = request.getParameter("async");

        Map<String,Object> values;
        if ("true".equals(async)) {
            AsyncMemcacheService asyncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            asyncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            Future<Map<String,Object>> futureValue = asyncCache.getAll(
                    Arrays.asList(keys.split(",")));
            try {
                values = futureValue.get();
            } catch (Exception e) {
                throw new ServletException("Error while accessing async memcache service", e);
            }
        } else {
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            syncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            values = syncCache.getAll(Arrays.asList(keys.split(",")));
        }

        JSONUtils.serialize(values, response);
    }

    protected void doDelete(HttpServletRequest request,
                            HttpServletResponse response) throws ServletException, IOException {

        String keys = request.getParameter("keys");
        String async = request.getParameter("async");
        Set<String> result;
        if ("true".equals(async)) {
            AsyncMemcacheService asyncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            asyncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            Future<Set<String>> futureValue = asyncCache.deleteAll(Arrays.asList(keys.split(",")));
            try {
                result = futureValue.get();
            } catch (Exception e) {
                throw new ServletException("Error while accessing async memcache service", e);
            }
        } else {
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            syncCache.setErrorHandler(ErrorHandlers.getConsistentLogAndContinue(Level.INFO));
            result = syncCache.deleteAll(Arrays.asList(keys.split(",")));
        }

        boolean success = result.size() == keys.split(",").length;
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", success);
        JSONUtils.serialize(map, response);
    }
}
