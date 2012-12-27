package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class ProjectBrowserHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String cursorString = request.getParameter("cursor");
        Cursor startCursor = null;
        if (cursorString != null && !"".equals(cursorString)) {
            startCursor = Cursor.fromWebSafeString(cursorString);
        }
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query query = new Query("Project");
        PreparedQuery preparedQuery = datastore.prepare(query);
        FetchOptions options = FetchOptions.Builder.withLimit(1);
        if (startCursor != null) {
            options.startCursor(startCursor);
        }
        QueryResultList<Entity> resultList = preparedQuery.asQueryResultList(options);
        Map<String,Object> map = new HashMap<String, Object>();
        if (resultList.size() > 0) {
            map.put("project", resultList.get(0).getProperty("name"));
            map.put("next", resultList.getCursor().toWebSafeString());
        } else {
            map.put("project", null);
            map.put("next", null);
        }
        JSONUtils.serialize(map, response);
    }
}
