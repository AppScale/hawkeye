package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONSerializable;
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
        Entity project = new Entity("Project", projectName);
        project.setProperty("project_id", projectId);
        project.setProperty("name", projectName);
        project.setProperty("description", request.getParameter("description"));
        project.setProperty("license", request.getParameter("license"));
        project.setProperty("rating", Integer.parseInt(request.getParameter("rating")));
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
                Query.FilterPredicate filter = new Query.FilterPredicate("name",
                        Query.FilterOperator.EQUAL, name);
                q = new Query("Project").setFilter(filter);
            } else {
                q = new Query("Project");
            }
        } else {
            Query.FilterPredicate filter = new Query.FilterPredicate("project_id",
                    Query.FilterOperator.EQUAL, id);
            q = new Query("Project").setFilter(filter);
        }

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        PreparedQuery preparedQuery = datastore.prepare(q);
        List<JSONSerializable> projects = new ArrayList<JSONSerializable>();
        for (Entity result : preparedQuery.asIterable()) {
            Project project = new Project();
            project.setProjectId((String) result.getProperty("project_id"));
            project.setName((String) result.getProperty("name"));
            project.setDescription((String) result.getProperty("description"));
            project.setLicense((String) result.getProperty("license"));
            project.setRating((Long) result.getProperty("rating"));
            projects.add(project);
        }

        JSONUtils.serialize(projects, response);
    }

    @Override
    protected void doDelete(HttpServletRequest req,
                            HttpServletResponse resp) throws ServletException, IOException {

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query q = new Query("Project");
        PreparedQuery preparedQuery = datastore.prepare(q);
        for (Entity result : preparedQuery.asIterable()) {
            datastore.delete(result.getKey());
        }
    }
}
