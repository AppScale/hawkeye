package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class ProjectRatingHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        int rating = Integer.parseInt(request.getParameter("rating"));
        String comparator = request.getParameter("comparator");
        String limit = request.getParameter("limit");
        String desc = request.getParameter("desc");

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query query = new Query("Project");
        if (comparator == null || "".equals(comparator) || "eq".equals(comparator)) {
            query = query.setFilter(new Query.FilterPredicate(
                    "rating", Query.FilterOperator.EQUAL, rating));
        } else if ("gt".equals(comparator)) {
            query = query.setFilter(new Query.FilterPredicate(
                    "rating", Query.FilterOperator.GREATER_THAN, rating));
        } else if ("ge".equals(comparator)) {
            query = query.setFilter(new Query.FilterPredicate(
                    "rating", Query.FilterOperator.GREATER_THAN_OR_EQUAL, rating));
        } else if ("lt".equals(comparator)) {
            query = query.setFilter(new Query.FilterPredicate(
                    "rating", Query.FilterOperator.LESS_THAN, rating));
        } else if ("le".equals(comparator)) {
            query = query.setFilter(new Query.FilterPredicate(
                    "rating", Query.FilterOperator.LESS_THAN_OR_EQUAL, rating));
        } else if ("ne".equals(comparator)) {
            query = query.setFilter(new Query.FilterPredicate(
                    "rating", Query.FilterOperator.NOT_EQUAL, rating));
        } else {
            throw new RuntimeException("Unsupported comparator");
        }

        if ("true".equals(desc)) {
            query = query.addSort("rating", Query.SortDirection.DESCENDING);
        } else {
            query = query.addSort("rating", Query.SortDirection.ASCENDING);
        }

        PreparedQuery preparedQuery = datastore.prepare(query);
        Iterable<Entity> iterable;
        if (limit != null && !"".equals(limit)) {
            iterable = preparedQuery.asIterable(
                    FetchOptions.Builder.withLimit(Integer.parseInt(limit)));
        } else {
            iterable = preparedQuery.asIterable();
        }

        JSONUtils.serialize(iterable, response);
    }
}
