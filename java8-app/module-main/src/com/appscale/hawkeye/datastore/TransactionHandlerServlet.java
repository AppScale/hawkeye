package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class TransactionHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String key = request.getParameter("key");
        int amount = Integer.parseInt(request.getParameter("amount"));
        String crossGroup = request.getParameter("xg");

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Map<String,Object> map = new HashMap<String, Object>();
        Transaction txn = null;

        if ("true".equals(crossGroup)) {
            try {
                TransactionOptions options = TransactionOptions.Builder.withXG(true);
                txn = datastore.beginTransaction(options);
                incrementCounters(key, amount);
                txn.commit();
                map.put("success", true);
            } catch (Exception e) {
                if (txn != null) {
                    txn.rollback();
                }
                map.put("success", false);
            }
            map.put("counter", getCounterByKey(key));
            map.put("backup", getCounterByKey(key + "_backup"));
        } else {
            try {
                txn = datastore.beginTransaction();
                incrementCounter(key, amount);
                txn.commit();
                map.put("success", true);
            } catch (Exception e) {
                if (txn != null) {
                    txn.rollback();
                }
                map.put("success", false);
            }
            map.put("counter", getCounterByKey(key));
        }
        JSONUtils.serialize(map, response);
    }

    @Override
    protected void doDelete(HttpServletRequest request,
                            HttpServletResponse response) throws ServletException, IOException {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query q = new Query(Constants.Counter.class.getSimpleName());
        PreparedQuery preparedQuery = datastore.prepare(q);
        for (Entity result : preparedQuery.asIterable()) {
            datastore.delete(result.getKey());
        }
    }

    private void incrementCounter(String key, int amount) {
        long counter = getCounterByKey(key);
        if (counter == -1) {
            counter = 0;
        }

        for (int i = 0; i < amount; i++) {
            counter++;
            if (counter == 5) {
                throw new RuntimeException("Mock Exception");
            }
            save(key, counter);
        }
    }

    private void incrementCounters(String key, int amount) {
        String backupKey = key + "_backup";
        long counter1 = getCounterByKey(key);
        long counter2 = getCounterByKey(backupKey);
        if (counter1 == -1) {
            counter1 = 0;
            counter2 = 0;
        }

        for (int i = 0; i < amount; i++) {
            counter1++;
            counter2++;
            if (counter1 == 5) {
                throw new RuntimeException("Mock Exception");
            }

            save(key, counter1);
            save(backupKey, counter2);
        }
    }

    private void save(String key, long counter) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Entity entity = new Entity(Constants.Counter.class.getSimpleName(), key);
        entity.setProperty(Constants.Counter.COUNTER, counter);
        entity.setProperty(Constants.TYPE, Constants.Counter.TYPE_VALUE);
        datastore.put(entity);
    }

    private long getCounterByKey(String key) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        try {
            Entity entity = datastore.get(KeyFactory.createKey(
                    Constants.Counter.class.getSimpleName(), key));
            return ((Long) entity.getProperty(Constants.Counter.COUNTER));
        } catch (EntityNotFoundException e) {
            return -1;
        }
    }
}
