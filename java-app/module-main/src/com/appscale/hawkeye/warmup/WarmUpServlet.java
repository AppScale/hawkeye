package com.appscale.hawkeye.warmup;


import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;


public class WarmUpServlet extends HttpServlet
{

    public void doGet(HttpServletRequest req,
                      HttpServletResponse resp ) throws ServletException, IOException {

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        System.out.println(datastore.getClass().getCanonicalName());
        Entity warmUpStatus = new Entity("WarmUpStatus");

        warmUpStatus.setProperty("success", true);

        System.out.println("Executing put");
        datastore.put(warmUpStatus);
        System.out.println("Done executing put");
    }
}
