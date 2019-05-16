package com.appscale.hawkeye.taskqueue;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.EntityNotFoundException;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;
import com.google.appengine.api.taskqueue.Queue;
import com.google.appengine.api.taskqueue.QueueFactory;
import com.google.appengine.api.taskqueue.TaskOptions;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class AdminTaskManager extends HttpServlet {
    private Key key = new KeyFactory.Builder("Task", "admin").getKey();

    public void doPost(HttpServletRequest request, HttpServletResponse response) {
        Queue queue = QueueFactory.getDefaultQueue();
        TaskOptions options = TaskOptions.Builder.withUrl("/java/taskqueue/admin_worker");
        queue.add(options);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        try {
            datastore.get(key);
        } catch (EntityNotFoundException e) {
            response.setStatus(404);
        }
    }

    public void doDelete(HttpServletRequest request, HttpServletResponse response) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        datastore.delete(key);
    }
}
