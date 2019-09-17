package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.DatastoreService;
import com.google.appengine.api.datastore.DatastoreServiceFactory;
import com.google.appengine.api.datastore.PreparedQuery;
import com.google.appengine.api.datastore.Query;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class ProjectFilterHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String license = request.getParameter("license");
        String rateLimit = request.getParameter("rate_limit");
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        List<Query.Filter> filters = new ArrayList<Query.Filter>();
        filters.add(new Query.FilterPredicate(Constants.Project.LICENSE,
                Query.FilterOperator.EQUAL, license));
        filters.add(new Query.FilterPredicate(Constants.Project.RATING,
                Query.FilterOperator.GREATER_THAN_OR_EQUAL, Long.parseLong(rateLimit)));
        Query query = new Query(Constants.Project.class.getSimpleName()).setFilter(
                new Query.CompositeFilter(Query.CompositeFilterOperator.AND, filters));
        PreparedQuery preparedQuery = datastore.prepare(query);
        JSONUtils.serialize(preparedQuery.asIterable(), response);
    }
}
