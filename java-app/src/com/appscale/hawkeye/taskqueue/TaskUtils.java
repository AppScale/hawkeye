package com.appscale.hawkeye.taskqueue;

import com.google.appengine.api.datastore.*;

public class TaskUtils {

    private static final String TASK_COUNTER = "TaskCounter";
    private static final String COUNT = "count";

    public synchronized static long getCountByKey(String keyString) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Key key = KeyFactory.createKey(TASK_COUNTER, keyString);
        try {
            Entity entity = datastore.get(key);
            return (Long) entity.getProperty(COUNT);
        } catch (EntityNotFoundException e) {
            return -1;
        }
    }

    public synchronized static void process(String keyString) {
        long counter = getCountByKey(keyString);
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Entity entity = new Entity(TASK_COUNTER, keyString);
        if (counter == -1) {
            entity.setProperty(COUNT, 1);
        } else {
            entity.setProperty(COUNT, counter + 1);
        }
        datastore.put(entity);
    }

    public static void deleteCounters() {
        Query query = new Query(TASK_COUNTER);
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        PreparedQuery preparedQuery = datastore.prepare(query);
        for (Entity entity : preparedQuery.asIterable()) {
            datastore.delete(entity.getKey());
        }
    }
}
