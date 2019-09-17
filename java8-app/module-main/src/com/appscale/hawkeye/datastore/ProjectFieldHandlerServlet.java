package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class ProjectFieldHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String fieldNames = request.getParameter("fields");
        String rateLimit = request.getParameter("rate_limit");
        String[] fields = fieldNames.trim().split(",");
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query query = new Query(Constants.Project.class.getSimpleName());
        for (String field : fields) {
            if ("rating".equals(field)) {
                query.addProjection(new PropertyProjection(Constants.Project.RATING,
                        Integer.class));
            } else {
                query.addProjection(new PropertyProjection(field, String.class));
            }
        }

        if (rateLimit != null && !"".equals(rateLimit)) {
            query = query.setFilter(new Query.FilterPredicate(Constants.Project.RATING,
                    Query.FilterOperator.GREATER_THAN_OR_EQUAL, Long.parseLong(rateLimit)));
        }
        PreparedQuery preparedQuery = datastore.prepare(query);
        JSONUtils.serialize(preparedQuery.asIterable(), response);
    }
}
