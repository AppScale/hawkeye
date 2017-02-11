package com.appscale.hawkeye.taskqueue;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.EntityNotFoundException;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;
import com.google.appengine.api.datastore.Transaction;
import com.google.appengine.api.taskqueue.Queue;
import com.google.appengine.api.taskqueue.QueueFactory;
import com.google.appengine.api.taskqueue.TaskOptions;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class TransactionalTaskHandlerServlet extends HttpServlet {
    private static final DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String key = request.getParameter("key");
        Map<String,Object> responseMap = new HashMap<>();

        Key taskKey = KeyFactory.createKey("TaskEntity", key);
        try {
            Entity task = datastore.get(taskKey);
            responseMap.put("value", task.getProperty("value"));
        } catch (EntityNotFoundException e) {
            responseMap.put("value", "None");
        }

        JSONUtils.serialize(responseMap, response);
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String key = request.getParameter("key");

        Boolean raiseException;
        try {
            raiseException = request.getParameter("raise_exception").toLowerCase().equals("true");
        } catch (NullPointerException e) {
            raiseException = false;
        }

        Queue queue = QueueFactory.getDefaultQueue();
        Map<String,Object> responseMap = new HashMap<>();

        Transaction txn = datastore.beginTransaction();
        queue.add(TaskOptions.Builder.withUrl("/java/taskqueue/transworker").param("key", key));

        Entity task = new Entity("TaskEntity", key);
        task.setProperty("value", "TXN_UPDATE");
        datastore.put(task);

        if (raiseException) {
            responseMap.put("value", "None");
            JSONUtils.serialize(responseMap, response);
            return;
        }

        txn.commit();

        // Fetch the value that was just put in the transaction.
        Key taskKey = KeyFactory.createKey("TaskEntity", key);
        try {
            Entity sameTask = datastore.get(taskKey);
            responseMap.put("value", sameTask.getProperty("value"));
        } catch (EntityNotFoundException e) {
            responseMap.put("value", "None");
        }

        JSONUtils.serialize(responseMap, response);
    }
}
