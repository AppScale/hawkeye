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
        Query query = new Query(Project.class.getSimpleName());
        for (String field : fields) {
            if ("rating".equals(field)) {
                query.addProjection(new PropertyProjection(Project.RATING, Integer.class));
            } else {
                query.addProjection(new PropertyProjection(field, String.class));
            }
        }

        if (rateLimit != null && !"".equals(rateLimit)) {
            query = query.setFilter(new Query.FilterPredicate(Project.RATING,
                    Query.FilterOperator.GREATER_THAN_OR_EQUAL, Long.parseLong(rateLimit)));
        }
        PreparedQuery preparedQuery = datastore.prepare(query);
        List<JSONSerializable> list = new ArrayList<JSONSerializable>();
        for (Entity result : preparedQuery.asIterable()) {
            Project project = new Project();
            project.setProjectId((String) result.getProperty(Project.PROJECT_ID));
            project.setName((String) result.getProperty(Project.NAME));
            project.setDescription((String) result.getProperty(Project.DESCRIPTION));
            project.setLicense((String) result.getProperty(Project.LICENSE));
            if (result.hasProperty(Project.RATING)) {
                project.setRating((Long) result.getProperty(Project.RATING));
            } else {
                project.setRating(-1);
            }
            list.add(project);
        }
        JSONUtils.serialize(list, response);
    }
}
