package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.*;

public class ProjectHandlerServlet extends HttpServlet {

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String projectId = UUID.randomUUID().toString();
        String projectName = request.getParameter("name");
        Entity project = new Entity(Constants.Project.class.getSimpleName(), projectName);
        project.setProperty(Constants.Project.PROJECT_ID, projectId);
        project.setProperty(Constants.Project.NAME, projectName);
        project.setProperty(Constants.Project.DESCRIPTION, request.getParameter("description"));
        project.setProperty(Constants.Project.LICENSE, request.getParameter("license"));
        project.setProperty(Constants.Project.RATING, Integer.parseInt(
                request.getParameter("rating")));
        project.setProperty(Constants.TYPE, Constants.Project.TYPE_VALUE);
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        datastore.put(project);
        response.setStatus(201);
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", true);
        map.put("project_id", projectId);
        JSONUtils.serialize(map, response);
    }

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        String id = request.getParameter("id");
        String name = request.getParameter("name");
        Query q;
        if (id == null || "".equals(id.trim())) {
            if (name != null && name.length() > 0) {
                Query.FilterPredicate filter = new Query.FilterPredicate(Constants.Project.NAME,
                        Query.FilterOperator.EQUAL, name);
                q = new Query(Constants.Project.class.getSimpleName()).setFilter(filter);
            } else {
                q = new Query(Constants.Project.class.getSimpleName());
            }
        } else {
            Query.FilterPredicate filter = new Query.FilterPredicate(Constants.Project.PROJECT_ID,
                    Query.FilterOperator.EQUAL, id);
            q = new Query(Constants.Project.class.getSimpleName()).setFilter(filter);
        }

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        PreparedQuery preparedQuery = datastore.prepare(q);
        JSONUtils.serialize(preparedQuery.asIterable(), response);
    }

    @Override
    protected void doDelete(HttpServletRequest req,
                            HttpServletResponse resp) throws ServletException, IOException {

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query q = new Query(Constants.Project.class.getSimpleName());
        PreparedQuery preparedQuery = datastore.prepare(q);
        for (Entity result : preparedQuery.asIterable()) {
            datastore.delete(result.getKey());
        }
    }
}
