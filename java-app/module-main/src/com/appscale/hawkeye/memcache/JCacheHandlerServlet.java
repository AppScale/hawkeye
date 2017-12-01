package com.appscale.hawkeye.memcache;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.memcache.MemcacheService;
import com.google.appengine.api.memcache.jsr107cache.GCacheFactory;
import net.sf.jsr107cache.Cache;
import net.sf.jsr107cache.CacheException;
import net.sf.jsr107cache.CacheFactory;
import net.sf.jsr107cache.CacheManager;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;

public class JCacheHandlerServlet extends HttpServlet {

    private static final CacheManager cacheManager = CacheManager.getInstance();

    private static final String SIMPLE_CACHE = "simple";
    private static final String EXPIRING_CACHE = "expiring";
    private static final String NO_UPDATE_CACHE = "noupdate";

    @Override
    public void init() throws ServletException {
        super.init();
        try {
            CacheFactory factory = cacheManager.getCacheFactory();
            Cache simpleCache = factory.createCache(Collections.emptyMap());
            cacheManager.registerCache(SIMPLE_CACHE, simpleCache);

            Map props1 = new HashMap();
            props1.put(GCacheFactory.EXPIRATION_DELTA, 6);
            Cache expiringCache = factory.createCache(props1);
            cacheManager.registerCache(EXPIRING_CACHE, expiringCache);

            Map props2 = new HashMap();
            props2.put(MemcacheService.SetPolicy.ADD_ONLY_IF_NOT_PRESENT, true);
            Cache noUpdateCache = factory.createCache(props2);
            cacheManager.registerCache(NO_UPDATE_CACHE, noUpdateCache);

        } catch (CacheException e) {
            throw new ServletException("Error while initializing JCache", e);
        }

    }

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String cacheName = request.getParameter("cache");
        String key = request.getParameter("key");
        String value = request.getParameter("value");
        Cache cache = cacheManager.getCache(cacheName);
        cache.put(key, value);
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", true);
        JSONUtils.serialize(map, response);
    }

    protected void doGet(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String cacheName = request.getParameter("cache");
        String key = request.getParameter("key");
        Cache cache = cacheManager.getCache(cacheName);
        Object result = cache.get(key);
        if (result != null) {
            Map<String,Object> map = new HashMap<String, Object>();
            map.put(key, result.toString());
            JSONUtils.serialize(map, response);
        } else {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
        }
    }

    protected void doDelete(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String cacheName = request.getParameter("cache");
        String key = request.getParameter("key");
        Cache cache = cacheManager.getCache(cacheName);
        Object result = cache.remove(key);
        if (result != null) {
            Map<String,Object> map = new HashMap<String, Object>();
            map.put(key, result.toString());
            JSONUtils.serialize(map, response);
        } else {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
        }
    }
}
