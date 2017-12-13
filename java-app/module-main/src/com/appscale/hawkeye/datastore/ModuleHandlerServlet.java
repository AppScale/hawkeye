package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.*;

public class ModuleHandlerServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        String id = request.getParameter("id");
        Query q;
        if (id == null || "".equals(id.trim())) {
            q = new Query(Constants.Module.class.getSimpleName());
        } else {
            Query.FilterPredicate filter = new Query.FilterPredicate(Constants.Module.MODULE_ID,
                    Query.FilterOperator.EQUAL, id);
            q = new Query(Constants.Module.class.getSimpleName()).setFilter(filter);
        }

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        PreparedQuery preparedQuery = datastore.prepare(q);
        JSONUtils.serialize(preparedQuery.asIterable(), response);
    }

    @Override
    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {
        String projectId = request.getParameter("project_id");
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query.FilterPredicate filter = new Query.FilterPredicate(Constants.Project.PROJECT_ID,
                Query.FilterOperator.EQUAL, projectId);
        Query q = new Query(Constants.Project.class.getSimpleName()).setFilter(filter);
        PreparedQuery preparedQuery = datastore.prepare(q);
        Entity project = preparedQuery.asSingleEntity();

        String moduleId = UUID.randomUUID().toString();
        String moduleName = request.getParameter("name");
        Entity module = new Entity(Constants.Module.class.getSimpleName(),
                moduleName, project.getKey());
        module.setProperty(Constants.Module.MODULE_ID, moduleId);
        module.setProperty(Constants.Module.NAME, moduleName);
        module.setProperty(Constants.Module.DESCRIPTION, request.getParameter("description"));
        module.setProperty(Constants.TYPE, Constants.Module.TYPE_VALUE);
        datastore.put(module);
        response.setStatus(201);
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", true);
        map.put("module_id", moduleId);
        JSONUtils.serialize(map, response);
    }

    @Override
    protected void doDelete(HttpServletRequest request,
                            HttpServletResponse response) throws ServletException, IOException {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query q = new Query(Constants.Module.class.getSimpleName());
        PreparedQuery preparedQuery = datastore.prepare(q);
        for (Entity result : preparedQuery.asIterable()) {
            datastore.delete(result.getKey());
        }
    }
}
