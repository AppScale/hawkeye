package com.appscale.hawkeye.taskqueue;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class AdminWorkerHandler extends HttpServlet {
    public void doPost(HttpServletRequest request, HttpServletResponse response) {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Entity entity = new Entity("Task", "admin");
        datastore.put(entity);
    }
}
