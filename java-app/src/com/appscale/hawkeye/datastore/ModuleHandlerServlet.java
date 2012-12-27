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

public class ModuleHandlerServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        String id = request.getParameter("id");
        Query q;
        if (id == null || "".equals(id.trim())) {
            q = new Query("Module");
        } else {
            Query.FilterPredicate filter = new Query.FilterPredicate("module_id",
                    Query.FilterOperator.EQUAL, id);
            q = new Query("Module").setFilter(filter);
        }

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        PreparedQuery preparedQuery = datastore.prepare(q);
        List<JSONSerializable> modules = new ArrayList<JSONSerializable>();
        for (Entity result : preparedQuery.asIterable()) {
            Module module = new Module();
            module.setModuleId((String) result.getProperty("module_id"));
            module.setName((String) result.getProperty("name"));
            module.setDescription((String) result.getProperty("description"));
            modules.add(module);
        }

        JSONUtils.serialize(modules, response);
    }

    @Override
    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {
        String projectId = request.getParameter("project_id");
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query.FilterPredicate filter = new Query.FilterPredicate("project_id",
                Query.FilterOperator.EQUAL, projectId);
        Query q = new Query("Project").setFilter(filter);
        PreparedQuery preparedQuery = datastore.prepare(q);
        Entity project = preparedQuery.asSingleEntity();

        String moduleId = UUID.randomUUID().toString();
        String moduleName = request.getParameter("name");
        Entity module = new Entity("Module", moduleName, project.getKey());
        module.setProperty("module_id", moduleId);
        module.setProperty("name", moduleName);
        module.setProperty("description", request.getParameter("description"));
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
        Query q = new Query("Module");
        PreparedQuery preparedQuery = datastore.prepare(q);
        for (Entity result : preparedQuery.asIterable()) {
            datastore.delete(result.getKey());
        }
    }
}
