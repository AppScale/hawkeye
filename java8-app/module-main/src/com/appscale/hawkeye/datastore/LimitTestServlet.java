package com.appscale.hawkeye.datastore;

import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.*;

public class LimitTestServlet extends HttpServlet {
    private String kind = "LimitTest";

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        PrintWriter out = response.getWriter();

        // Ensure that PreparedQuery limit is respected.
        int totalEntities = 25;
        int limit = 10;
        int chunkSize = 100;
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

        // Insert initial entities to query.
        for (int i = 0; i < totalEntities; i++) {
            Entity e = new Entity(kind);
            e.setProperty("test_property", i);
            datastore.put(null, e);
        }

        // Fetch entities with limit.
        Query query = new Query(kind);
        PreparedQuery pq = datastore.prepare(null, query);
        FetchOptions fetchOptions = FetchOptions.Builder.withChunkSize(chunkSize).limit(limit);

        // Place results in a list and check the length.
        List<Entity> entities = new ArrayList<>();
        entities.addAll(pq.asList(fetchOptions));
        if (entities.size() != limit) {
            response.setStatus(500);
            out.println("Fetched " + entities.size() + " entities. Expected " + limit + ".");
            return;
        }
        out.println("Fetched " + entities.size() + " entities.");

        // Get the results through an iterable.
        entities = new ArrayList<>();
        query = new Query(kind);
        pq = datastore.prepare(null, query);
        fetchOptions = FetchOptions.Builder.withChunkSize(chunkSize).limit(limit);
        for (Entity e : pq.asIterable(fetchOptions)) {
            entities.add(e);
        }

        if (entities.size() != limit) {
            response.setStatus(500);
            out.println("Fetched " + entities.size() + " entities. Expected " + limit + ".");
            return;
        }
        out.println("Fetched " + entities.size() + " entities.");
    }

    protected void doDelete(HttpServletRequest req,
                            HttpServletResponse resp) throws ServletException, IOException {

        // Remove all entities related to this test.
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query q = new Query(kind);
        PreparedQuery preparedQuery = datastore.prepare(q);
        for (Entity result : preparedQuery.asIterable()) {
            datastore.delete(result.getKey());
        }
    }
}
