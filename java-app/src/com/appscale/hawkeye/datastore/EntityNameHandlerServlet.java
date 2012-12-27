package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class EntityNameHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        String projectName = request.getParameter("project_name");
        String moduleName = request.getParameter("module_name");
        if (projectName != null && !"".equals(projectName)) {
            DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
            Query query;
            if (moduleName != null && !"".equals(moduleName)) {
                query = new Query("Project").setFilter(new Query.FilterPredicate("name",
                        Query.FilterOperator.EQUAL, projectName));
                PreparedQuery preparedQuery = datastore.prepare(query);
                query = new Query("Module").setFilter(
                        new Query.FilterPredicate(Entity.KEY_RESERVED_PROPERTY,
                        Query.FilterOperator.EQUAL, KeyFactory.createKey(
                                preparedQuery.asSingleEntity().getKey(), "Module", moduleName)));
            } else {
                query = new Query("Project").setFilter(new Query.FilterPredicate(
                        Entity.KEY_RESERVED_PROPERTY,
                        Query.FilterOperator.EQUAL, KeyFactory.createKey("Project", projectName)));
            }

            PreparedQuery preparedQuery = datastore.prepare(query);
            JSONUtils.serialize(preparedQuery.asSingleEntity(), response);
        } else {
            throw new RuntimeException("Missing parameters");
        }
    }
}
