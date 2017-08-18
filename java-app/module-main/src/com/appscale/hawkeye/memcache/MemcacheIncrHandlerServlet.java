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

public class MemcacheIncrHandlerServlet extends HttpServlet {

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {
        String key = request.getParameter("key");
        String delta = request.getParameter("delta");
        String async = request.getParameter("async");
        String initVal = request.getParameter("initial"); 
        Long postIncrVal = -1000l;
        if("true".equals(async))
        {
            AsyncMemcacheService asyncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            Future<Long> future;
            if(initVal == null)
            {
                future = asyncCache.increment(key, Long.valueOf(delta).longValue());
                try
                {
                    postIncrVal = future.get();
                }
                catch(Exception e)
                {
                    throw new ServletException("Error accessing async memcache service", e);
                }
            }
            else if(initVal != null)
            {
                future = asyncCache.increment(key, Long.valueOf(delta).longValue(), Long.valueOf(initVal).longValue());
                try
                {
                    postIncrVal = future.get();
                }
                catch(Exception e)
                {
                    throw new ServletException("Error accessing async memcache service", e);
                }
            }
        }
        else
        { 
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            if(initVal == null)
            {
                postIncrVal = syncCache.increment(key, Long.valueOf(delta).longValue());
            }
            else if(initVal != null)
            {
                postIncrVal = syncCache.increment(key, Long.valueOf(delta).longValue(), Long.valueOf(initVal).longValue());
            }
        }
        Map<String, Object> map = new HashMap<String, Object>();
        map.put("success", true);
        map.put("value", postIncrVal.longValue());
        JSONUtils.serialize(map, response);    
    }

    protected void doGet(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {
        String key = request.getParameter("key");
        String value = request.getParameter("value");
        String async = request.getParameter("async");
        Boolean success = false;
        if("true".equals(async))
        {
            AsyncMemcacheService asyncCache = MemcacheServiceFactory.getAsyncMemcacheService();
            Future<Boolean> future;
            future = asyncCache.put(key, Long.valueOf(value).longValue(), Expiration.byDeltaSeconds(3600), MemcacheService.SetPolicy.ADD_ONLY_IF_NOT_PRESENT);
            try
            {
                success = future.get();
            }
            catch(Exception e)
            {
                throw new ServletException("Error accessing async memcache service", e);
            }
        }
        else
        {
            MemcacheService syncCache = MemcacheServiceFactory.getMemcacheService();
            success = syncCache.put(key, Long.valueOf(value).longValue(), Expiration.byDeltaSeconds(3600), MemcacheService.SetPolicy.ADD_ONLY_IF_NOT_PRESENT);
        }
        Map<String, Object> map = new HashMap<String, Object>();
        map.put("success", success);
        JSONUtils.serialize(map, response);
    }
}
