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
                query = new Query(Constants.Project.class.getSimpleName()).
                        setFilter(new Query.FilterPredicate(
                                Constants.Project.NAME,
                                Query.FilterOperator.EQUAL,
                                projectName));
                PreparedQuery preparedQuery = datastore.prepare(query);
                Key projectKey = preparedQuery.asSingleEntity().getKey();
                Key moduleKey = KeyFactory.createKey(projectKey,
                        Constants.Module.class.getSimpleName(), moduleName);
                query = new Query(Constants.Module.class.getSimpleName()).
                        setFilter(new Query.FilterPredicate(
                                Entity.KEY_RESERVED_PROPERTY,
                                Query.FilterOperator.EQUAL,
                                moduleKey));
            } else {
                Key projectKey = KeyFactory.createKey(
                        Constants.Project.class.getSimpleName(), projectName);
                query = new Query(Constants.Project.class.getSimpleName()).
                        setFilter(new Query.FilterPredicate(
                                Entity.KEY_RESERVED_PROPERTY,
                                Query.FilterOperator.EQUAL,
                                projectKey));
            }

            PreparedQuery preparedQuery = datastore.prepare(query);
            JSONUtils.serialize(preparedQuery.asSingleEntity(), response);
        } else {
            throw new RuntimeException("Missing parameters");
        }
    }
}
