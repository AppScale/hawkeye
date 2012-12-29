package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONSerializable;
import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ProjectKeyHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String projectId = request.getParameter("project_id");
        String ancestor = request.getParameter("ancestor");
        String comparator = request.getParameter("comparator");

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query.FilterPredicate filter = new Query.FilterPredicate(Project.PROJECT_ID,
                Query.FilterOperator.EQUAL, projectId);
        Query projectQuery = new Query(Project.class.getSimpleName()).setFilter(filter);
        PreparedQuery preparedQuery = datastore.prepare(projectQuery);
        Key projectKey = preparedQuery.asSingleEntity().getKey();

        Query q = new Query();
        if ("true".equals(ancestor)) {
            q = q.setAncestor(projectKey);
        }

        if ("ge".equals(comparator)) {
            q = q.setFilter(new Query.FilterPredicate(Entity.KEY_RESERVED_PROPERTY,
                    Query.FilterOperator.GREATER_THAN_OR_EQUAL, projectKey));
        } else if ("gt".equals(comparator)) {
            q = q.setFilter(new Query.FilterPredicate(Entity.KEY_RESERVED_PROPERTY,
                    Query.FilterOperator.GREATER_THAN, projectKey));
        } else {
            throw new RuntimeException("Unsupported comparator");
        }

        preparedQuery = datastore.prepare(q);
        List<Entity> results = new ArrayList<Entity>();
        for (Entity entity : preparedQuery.asIterable()) {
            if (Project.class.getSimpleName().equals(entity.getKind()) ||
                    Module.class.getSimpleName().equals(entity.getKind())) {
                results.add(entity);
            }
        }
        JSONUtils.serialize(results, response);
    }
}
