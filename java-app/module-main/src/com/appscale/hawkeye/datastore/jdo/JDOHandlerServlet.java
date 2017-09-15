package com.appscale.hawkeye.datastore.jdo;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;

import javax.jdo.JDOObjectNotFoundException;
import javax.jdo.PersistenceManager;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;


public class JDOHandlerServlet extends HttpServlet {

    protected void doPut(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String name = request.getParameter("name");
        int rating = Integer.parseInt(request.getParameter("rating"));
        String projectId = UUID.randomUUID().toString();
        Key key = KeyFactory.createKey(Project.class.getSimpleName(), projectId);
        Project project = new Project(key, name, rating);
        PersistenceManager pm = PMF.get().getPersistenceManager();
        try {
            pm.makePersistent(project);
            response.setStatus(HttpServletResponse.SC_CREATED);
            Map<String,Object> map = new HashMap<String, Object>();
            map.put("success", true);
            map.put("project_id", projectId);
            JSONUtils.serialize(map, response);
        } finally {
            pm.close();
        }
    }

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String projectId = request.getParameter("project_id");
        int rating = Integer.parseInt(request.getParameter("rating"));
        Key key = KeyFactory.createKey(Project.class.getSimpleName(), projectId);
        PersistenceManager pm = PMF.get().getPersistenceManager();
        try {
            Project project = pm.getObjectById(Project.class, key);
            if (project != null) {
                project.setRating(rating);
                Map<String,Object> map = new HashMap<String, Object>();
                map.put("project_id", projectId);
                map.put("name", project.getName());
                map.put("rating", project.getRating());
                JSONUtils.serialize(map, response);
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        } catch (JDOObjectNotFoundException e) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
        } finally {
            pm.close();
        }
    }

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String projectId = request.getParameter("project_id");
        Key key = KeyFactory.createKey(Project.class.getSimpleName(), projectId);
        PersistenceManager pm = PMF.get().getPersistenceManager();
        try {
            Project project = pm.getObjectById(Project.class, key);
            if (project != null) {
                Map<String,Object> map = new HashMap<String, Object>();
                map.put("project_id", projectId);
                map.put("name", project.getName());
                map.put("rating", project.getRating());
                JSONUtils.serialize(map, response);
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        } catch (JDOObjectNotFoundException e) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
        } finally {
            pm.close();
        }
    }

    @Override
    protected void doDelete(HttpServletRequest request,
                            HttpServletResponse response) throws ServletException, IOException {

        String projectId = request.getParameter("project_id");
        Key key = KeyFactory.createKey(Project.class.getSimpleName(), projectId);
        PersistenceManager pm = PMF.get().getPersistenceManager();
        try {
            Project project = pm.getObjectById(Project.class, key);
            if (project != null) {
                pm.deletePersistent(project);
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        } catch (JDOObjectNotFoundException e) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);

        } finally {
            pm.close();
        }
    }
}
