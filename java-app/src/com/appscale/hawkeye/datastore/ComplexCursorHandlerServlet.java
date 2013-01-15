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

public class ComplexCursorHandlerServlet extends HttpServlet {
    private String        EMPLOYEE_KIND = "Employee";
    private int           numEmployees  = 4;
    private HashSet<Long> seenEmployees = new HashSet<Long>();
    private int           successCode   = 200;
    private int           failCode      = 500;

    public void doGet( HttpServletRequest req, HttpServletResponse resp ) throws IOException
    {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        List<Key> keyList = null;
        try
        {
            //list is used for cleanup
            keyList = setUpData(datastore);

            Query query = new Query(EMPLOYEE_KIND);

            /*
             * Set up a query, limit it to 1 result and get the first
             * set of results. 
             */
            PreparedQuery preparedQuery = datastore.prepare(query);
            FetchOptions options = FetchOptions.Builder.withLimit(1);
            QueryResultList<Entity> resultList = preparedQuery.asQueryResultList(options);
            int counter = 0;

           /*
            * Check result kind, get the cursor and grab the next set
            * of results. 
            */
            while (resultList.size() > 0)
            {
                counter++;
                Map<String, Object> map = new HashMap<String, Object>();
                String cursorString = null;
                                          
                String resultKind = resultList.get(0).getKind();
                if(!resultKind.equals(EMPLOYEE_KIND))
                {
                    throw new Exception("Result was not the expected kind [" + EMPLOYEE_KIND + "], it was [" + resultKind + "]");
                }
                Long id = resultList.get(0).getKey().getId();
                if(seenEmployees.contains(id))
                {                     
                    throw new Exception("Saw the same entity twice");
                }
                seenEmployees.add(id);
                cursorString = resultList.getCursor().toWebSafeString();
                options.startCursor(Cursor.fromWebSafeString(cursorString));
                resultList = preparedQuery.asQueryResultList(options);
            }
            
            if(counter != numEmployees)
            {
                throw new Exception("Fetched " + counter + " employees instead of " + numEmployees);
            }
        }
        catch (Exception e)
        {
            System.out.println("Caught exception " + e.getMessage());
            e.printStackTrace();
            resp.sendError(failCode, e.getMessage());
            return;
        }
        finally
        {
            cleanUpData(datastore, keyList);
        }

        resp.setStatus(successCode);
    }

    private List<Key> setUpData( DatastoreService datastore )
    {
        List<Key> keyList = new ArrayList<Key>();
        
        Entity company = new Entity("Company");
        company.setProperty("Name", "AppScale");
        datastore.put(company);
        keyList.add(company.getKey());

        Entity employee1 = new Entity(EMPLOYEE_KIND, company.getKey());
        Entity employee2 = new Entity(EMPLOYEE_KIND, company.getKey());
        Entity employee3 = new Entity(EMPLOYEE_KIND, company.getKey());
        Entity employee4 = new Entity(EMPLOYEE_KIND, company.getKey());
        datastore.put(employee1);
        datastore.put(employee2);
        datastore.put(employee3);
        datastore.put(employee4);
        keyList.add(employee1.getKey());
        keyList.add(employee2.getKey());
        keyList.add(employee3.getKey());
        keyList.add(employee4.getKey());

        Entity phoneNum1 = new Entity("PhoneNumber", employee1.getKey());
        Entity phoneNum2 = new Entity("PhoneNumber", employee2.getKey());
        Entity phoneNum3 = new Entity("PhoneNumber", employee3.getKey());
        Entity phoneNum4 = new Entity("PhoneNumber", employee4.getKey());
        phoneNum1.setProperty("work", "1111111111");
        phoneNum2.setProperty("work", "2222222222");
        phoneNum3.setProperty("work", "3333333333");
        phoneNum4.setProperty("work", "4444444444");
        datastore.put(phoneNum1);
        datastore.put(phoneNum2);
        datastore.put(phoneNum3);
        datastore.put(phoneNum4);
        keyList.add(phoneNum1.getKey());
        keyList.add(phoneNum2.getKey());
        keyList.add(phoneNum3.getKey());
        keyList.add(phoneNum4.getKey());
        return keyList;
    }
    
    private void cleanUpData(DatastoreService datastore, List<Key> keyList)
    {
        datastore.delete(keyList);
    }
}
