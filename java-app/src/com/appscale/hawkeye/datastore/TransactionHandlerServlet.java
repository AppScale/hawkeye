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
            map.put("counter", getCounterByKey(key).getCounter());
            map.put("backup", getCounterByKey(key + "_backup").getCounter());
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
            map.put("counter", getCounterByKey(key).getCounter());
        }
        JSONUtils.serialize(map, response);
    }

    @Override
    protected void doDelete(HttpServletRequest request,
                            HttpServletResponse response) throws ServletException, IOException {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query q = new Query(Counter.class.getSimpleName());
        PreparedQuery preparedQuery = datastore.prepare(q);
        for (Entity result : preparedQuery.asIterable()) {
            datastore.delete(result.getKey());
        }
    }

    private void incrementCounter(String key, int amount) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Counter counter = getCounterByKey(key);
        if (counter == null) {
            counter = new Counter();
            counter.setCounter(0);
        }

        for (int i = 0; i < amount; i++) {
            counter.increment();
            if (counter.getCounter() == 5) {
                throw new RuntimeException("Mock Exception");
            }
            Entity entity = new Entity(Counter.class.getSimpleName(), key);
            entity.setProperty("counter", counter.getCounter());
            datastore.put(entity);
        }
    }

    private void incrementCounters(String key, int amount) {
        String backupKey = key + "_backup";
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Counter counter1 = getCounterByKey(key);
        Counter counter2 = getCounterByKey(backupKey);
        if (counter1 == null) {
            counter1 = new Counter();
            counter2 = new Counter();
        }

        for (int i = 0; i < amount; i++) {
            counter1.increment();
            counter2.increment();
            if (counter1.getCounter() == 5) {
                throw new RuntimeException("Mock Exception");
            }
            Entity entity = new Entity(Counter.class.getSimpleName(), key);
            entity.setProperty("counter", counter1.getCounter());
            datastore.put(entity);

            entity = new Entity(Counter.class.getSimpleName(), backupKey);
            entity.setProperty("counter", counter2.getCounter());
            datastore.put(entity);
        }
    }

    private Counter getCounterByKey(String key) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        try {
            Entity entity = datastore.get(KeyFactory.createKey(Counter.class.getSimpleName(), key));
            Counter counter = new Counter();
            counter.setCounter((Long) entity.getProperty("counter"));
            return counter;
        } catch (EntityNotFoundException e) {
            return null;
        }
    }
}
