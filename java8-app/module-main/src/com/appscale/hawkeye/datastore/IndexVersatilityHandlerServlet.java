package com.appscale.hawkeye.datastore;

import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.FetchOptions;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.Query;
import com.google.appengine.api.datastore.Query.Filter;
import com.google.appengine.api.datastore.Query.FilterPredicate;
import com.google.appengine.api.datastore.Query.FilterOperator;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class IndexVersatilityHandlerServlet extends HttpServlet {
    private String companyKind = "Company";
    private String employeeKind = "Employee";
    private int successCode = 200;
    private int failCode = 500;

    /* This test assumes that the following index does not exist:
       <datastore-index kind="Employee" ancestor="true" source="manual">
           <property name="value" direction="asc"/>
       </datastore-index>

       The datastore should use the following descending index instead:
       <datastore-index kind="Employee" ancestor="true" source="manual">
           <property name="value" direction="desc"/>
       </datastore-index> */
    public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        List<Key> keyList = new ArrayList<>();
        try {
            Entity company = new Entity(companyKind);
            company.setProperty("Name", "AppScale");
            Key companyKey = company.getKey();
            keyList.add(companyKey);
            datastore.put(company);

            int[] values = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
            for (int value : values) {
                Entity employee = new Entity(employeeKind, companyKey);
                employee.setProperty("value", value);
                datastore.put(employee);
                keyList.add(employee.getKey());
            }

            Filter filter = new FilterPredicate("value", FilterOperator.GREATER_THAN, 4);
            Query query = new Query(employeeKind).setAncestor(companyKey).setFilter(filter);
            FetchOptions options = FetchOptions.Builder.withDefaults();
            List<Entity> results = datastore.prepare(query).asList(options);
            if (results.size() != 5) {
                String error = "Retrieved " + results.size() + " results.";
                resp.sendError(failCode, error);
            }
        }
        finally { datastore.delete(keyList); }

        resp.setStatus(successCode);
    }
}
