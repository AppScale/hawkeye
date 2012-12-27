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

public class ProjectFieldHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String fieldNames = request.getParameter("fields");
        String rateLimit = request.getParameter("rate_limit");
        String[] fields = fieldNames.trim().split(",");
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query query = new Query("Project");
        for (String field : fields) {
            if ("rating".equals(field)) {
                query.addProjection(new PropertyProjection("rating", Integer.class));
            } else {
                query.addProjection(new PropertyProjection(field, String.class));
            }
        }

        if (rateLimit != null && !"".equals(rateLimit)) {
            query = query.setFilter(new Query.FilterPredicate("rating",
                    Query.FilterOperator.GREATER_THAN_OR_EQUAL, Long.parseLong(rateLimit)));
        }
        PreparedQuery preparedQuery = datastore.prepare(query);
        List<JSONSerializable> list = new ArrayList<JSONSerializable>();
        for (Entity result : preparedQuery.asIterable()) {
            Project project = new Project();
            project.setProjectId((String) result.getProperty("project_id"));
            project.setName((String) result.getProperty("name"));
            project.setDescription((String) result.getProperty("description"));
            project.setLicense((String) result.getProperty("license"));
            if (result.hasProperty("rating")) {
                project.setRating((Long) result.getProperty("rating"));
            } else {
                project.setRating(-1);
            }
            list.add(project);
        }
        JSONUtils.serialize(list, response);
    }
}
