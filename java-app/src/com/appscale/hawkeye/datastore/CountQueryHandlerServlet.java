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
import java.util.HashSet;
import java.util.ArrayList;
import java.util.List;

public class CountQueryHandlerServlet extends HttpServlet {
    private String        EMPLOYEE_KIND = "EMPLOYEE";
    private int           successCode = 200;
    private int           failureCode = 500;
    

    public void doGet( HttpServletRequest req, HttpServletResponse resp ) throws IOException
    {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        List<Key> keyList1 = null;
        List<Key> keyList2 = null;
        try
        {
            datastore = DatastoreServiceFactory.getDatastoreService();
            keyList1 = setUpData1(datastore);
            Query q1 = new Query("Employee");
            PreparedQuery pq1 = datastore.prepare(q1);
            int count1 = pq1.countEntities(FetchOptions.Builder.withLimit(1000));
            if(count1 != 2)
            {
                throw new Exception("Count was not expected value of 2, it was [" + count1 + "]");
            }
        
            keyList2 = setUpData2(datastore);
            Query q2 = new Query("Employee");
            PreparedQuery pq2 = datastore.prepare(q2);
            int count2 = pq2.countEntities(FetchOptions.Builder.withLimit(1000));
            if(count2 != 3)
            {
                throw new Exception("Count was not expected value of 3, it was [" + count2 + "]");
            }
        }
        catch(Exception e)
        {
            System.out.println("Caught exception " + e.getMessage());
            e.printStackTrace();
            resp.sendError(failureCode, e.getMessage());
            return;
        } 
        finally
        {
           
            if(keyList1 != null) cleanUpData(datastore, keyList1);
            if(keyList2 != null) cleanUpData(datastore, keyList2);
        }

        resp.setStatus(successCode);
    }

    private List<Key> setUpData1( DatastoreService datastore )
    {
        List<Key> keyList = new ArrayList<Key>();

        Entity employee1 = new Entity("Employee");
        employee1.setProperty("firstName", "Navraj");
        datastore.put(employee1);
        keyList.add(employee1.getKey());

        Entity employee2 = new Entity("Employee");
        employee2.setProperty("firstName", "Tyler");
        datastore.put(employee2);
        keyList.add(employee2.getKey());
     
        return keyList;
    }

    private List<Key> setUpData2( DatastoreService datastore )
    {
        List<Key> keyList = new ArrayList<Key>();

        Entity employee = new Entity("Employee");
        employee.setProperty("firstName", "Chris");
        datastore.put(employee); 
        keyList.add(employee.getKey());
        
        return keyList;
    }

    private void cleanUpData(DatastoreService datastore, List<Key> keyList)
    {
        datastore.delete(keyList);
    }
}
