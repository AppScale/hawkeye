package com.appscale.hawkeye.datastore;

import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.*;

public class ProjectionQueryServlet extends HttpServlet {
    private String kind = "ProjectionQuery";
    private String compositeKind = "Project";
    private int totalEntities = 10;

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        PrintWriter out = response.getWriter();

        // Ensure that projection queries work.
        String projection = "first_property";
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

        // Fetch entities with limit.
        Query query = new Query(kind);
        query.addProjection(new PropertyProjection(projection, String.class));
        PreparedQuery pq = datastore.prepare(null, query);
        FetchOptions fetchOptions = FetchOptions.Builder.withDefaults();

        // Place results in a list and check the length.
        List<Entity> entities = new ArrayList<>();
        entities.addAll(pq.asList(fetchOptions));
        if (entities.size() != totalEntities) {
            response.setStatus(500);
            out.println("Fetched " + entities.size() + " entities with kind query. " +
                    "Expected " + totalEntities + ".");
            return;
        }

        // Ensure that each entity has only one property.
        for (Entity e : entities) {
            if (e.getProperties().size() != 1) {
                response.setStatus(500);
                out.println("Encountered " + e.getProperties().size() + " properties with kind query. Expected 1.");
                return;
            }
        }
        out.println("Fetched " + entities.size() + " entities with kind query.");

        // Test single-property projection query.
        query.setFilter(new Query.FilterPredicate("first_property", Query.FilterOperator.GREATER_THAN_OR_EQUAL, "0"));
        pq = datastore.prepare(null, query);
        entities = new ArrayList<>();
        entities.addAll(pq.asList(fetchOptions));
        if (entities.size() != totalEntities) {
            response.setStatus(500);
            out.println("Fetched " + entities.size() + " entities with single-property query. " +
                    "Expected " + totalEntities + ".");
            return;
        }

        // Ensure that each entity has only one property.
        for (Entity e : entities) {
            if (e.getProperties().size() != 1) {
                response.setStatus(500);
                out.println("Encountered " + e.getProperties().size() + " properties with single-property query. " +
                        "Expected 1.");
                return;
            }
        }
        out.println("Fetched " + entities.size() + " entities with single-property query.");

        // Projection queries can't be performed with equality filters, so zigzag merge queries don't need to be tested.

        // Test composite projection queries.
        query = new Query(compositeKind).addProjection(new PropertyProjection("project_id", String.class));
        Query.Filter firstFilter = new Query.FilterPredicate(
                "project_id", Query.FilterOperator.GREATER_THAN_OR_EQUAL, "0");
        Query.Filter secondFilter = new Query.FilterPredicate("name", Query.FilterOperator.EQUAL, "0");
        Query.CompositeFilter compositeFilter = Query.CompositeFilterOperator.and(firstFilter, secondFilter);
        query.setFilter(compositeFilter);
        pq = datastore.prepare(null, query);
        entities = new ArrayList<>();
        entities.addAll(pq.asList(fetchOptions));
        if (entities.size() != 1) {
            response.setStatus(500);
            out.println("Fetched " + entities.size() + " entities with composite query. Expected 1.");
            return;
        }

        // Ensure that each entity has only one property.
        for (Entity e : entities) {
            if (e.getProperties().size() != 1) {
                response.setStatus(500);
                out.println("Encountered " + e.getProperties().size() + " properties with composite query. " +
                        "Expected 1.");
                return;
            }
        }
        out.println("Fetched " + entities.size() + " entities with composite query.");
    }

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {
        PrintWriter out = response.getWriter();

        // Insert initial entities to query.
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        for (int i = 0; i < totalEntities; i++) {
            Entity e = new Entity(kind);
            String value = Integer.toString(i);
            e.setProperty("first_property", value);
            e.setProperty("second_property", value);
            datastore.put(null, e);
        }
        out.println("Inserted " + totalEntities + " " + kind + " entities.");

        // Insert entities for composite query.
        for (int i = 0; i < totalEntities; i++) {
            Entity e = new Entity(compositeKind);
            String value = Integer.toString(i);
            e.setProperty("name", value);
            e.setProperty("project_id", value);
            datastore.put(null, e);
        }
        out.println("Inserted " + totalEntities + " " + compositeKind + " entities.");
    }

    protected void doDelete(HttpServletRequest request,
                            HttpServletResponse response) throws ServletException, IOException {
        PrintWriter out = response.getWriter();

        // Remove all entities related to this test.
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query query = new Query(kind);
        PreparedQuery pq = datastore.prepare(query);
        for (Entity result : pq.asIterable()) {
            datastore.delete(result.getKey());
        }
        out.println("Deleted all " + kind + " entities.");

        query = new Query(compositeKind);
        pq = datastore.prepare(query);
        for (Entity result : pq.asIterable()) {
            datastore.delete(result.getKey());
        }
        out.println("Deleted all " + compositeKind + " entities.");
    }
}
