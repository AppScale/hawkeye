package com.appscale.hawkeye.warmup;


import javax.servlet.http.HttpServlet;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;


public class WarmUpServlet extends HttpServlet
{

    public void init() {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        System.out.println(datastore.getClass().getCanonicalName());
        Entity warmUpStatus = new Entity(Constants.WARMUP_KEY);

        warmUpStatus.setProperty("success", true);

        System.out.println("Executing put");
        datastore.put(warmUpStatus);
        System.out.println("Done executing put");
    }
}
