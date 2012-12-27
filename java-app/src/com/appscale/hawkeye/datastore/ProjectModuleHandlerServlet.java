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

public class ProjectModuleHandlerServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String projectId = request.getParameter("project_id");
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query.FilterPredicate filter = new Query.FilterPredicate("projectId",
                Query.FilterOperator.EQUAL, projectId);
        Query q = new Query("Project").setFilter(filter);
        PreparedQuery preparedQuery = datastore.prepare(q);
        Entity project = preparedQuery.asSingleEntity();

        q = new Query("Module").setAncestor(project.getKey());
        preparedQuery = datastore.prepare(q);
        List<JSONSerializable> modules = new ArrayList<JSONSerializable>();
        for (Entity result : preparedQuery.asIterable()) {
            Module module = new Module();
            module.setModuleId((String) result.getProperty("moduleId"));
            module.setName((String) result.getProperty("name"));
            module.setDescription((String) result.getProperty("description"));
            modules.add(module);
        }

        JSONUtils.serialize(modules, response);
    }
}
