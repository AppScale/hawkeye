package com.appscale.hawkeye.taskqueue;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.EntityNotFoundException;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class TransactionalTaskWorkerServlet extends HttpServlet {
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        String key = request.getParameter("key");

        Key taskKey = KeyFactory.createKey("TaskEntity", key);
        Entity task;
        try {
            task = datastore.get(taskKey);
        } catch (EntityNotFoundException e) {
            task = new Entity("TaskEntity", key);
        }
        task.setProperty("value", "TQ_UPDATE");
        datastore.put(task);
    }
}
