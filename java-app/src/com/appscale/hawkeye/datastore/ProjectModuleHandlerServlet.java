package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class ProjectModuleHandlerServlet extends HttpServlet {

    @Override
    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String projectId = request.getParameter("project_id");
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query.FilterPredicate filter = new Query.FilterPredicate(Constants.Project.PROJECT_ID,
                Query.FilterOperator.EQUAL, projectId);
        Query q = new Query(Constants.Project.class.getSimpleName()).setFilter(filter);
        PreparedQuery preparedQuery = datastore.prepare(q);
        Entity project = preparedQuery.asSingleEntity();

        q = new Query(Constants.Module.class.getSimpleName()).setAncestor(project.getKey());
        preparedQuery = datastore.prepare(q);
        JSONUtils.serialize(preparedQuery.asIterable(), response);
    }
}
