package com.appscale.hawkeye.blobstore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.blobstore.*;
import com.google.appengine.api.datastore.*;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class BlobQueryHandlerServlet extends HttpServlet {

    private BlobstoreService blobstoreService = BlobstoreServiceFactory.getBlobstoreService();

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        String key = request.getParameter("key");
        String fetchData = request.getParameter("data");
        if ("true".equals(fetchData)) {
            BlobKey blobKey = new BlobKey(key);
            long start = Long.parseLong(request.getParameter("start"));
            long end = Long.parseLong(request.getParameter("end"));
            try {
                byte[] data = blobstoreService.fetchData(blobKey, start, end);
                response.getOutputStream().write(data);
            } catch (IllegalArgumentException e) {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        } else {
            String fileName = request.getParameter("file");
            String size = request.getParameter("size");
            if (fileName != null && !"".equals(fileName)) {
                Query query = new Query("__BlobInfo__");
                query.setFilter(new Query.FilterPredicate("filename",
                        Query.FilterOperator.EQUAL, fileName));
                sendBlobInfo(query, response, false);
            } else if (size != null && !"".equals(size)) {
                long sizeValue = Long.parseLong(size);
                Query query = new Query("__BlobInfo__");
                query.setFilter(new Query.FilterPredicate("size",
                        Query.FilterOperator.GREATER_THAN, sizeValue));
                sendBlobInfo(query, response, true);
            } else {
                BlobInfoFactory factory = new BlobInfoFactory();
                BlobKey blobKey = new BlobKey(key);
                BlobInfo blobInfo = factory.loadBlobInfo(blobKey);
                if (blobInfo != null) {
                    Map<String,Object> map = new HashMap<String, Object>();
                    map.put("filename", blobInfo.getFilename());
                    map.put("size", blobInfo.getSize());
                    JSONUtils.serialize(map, response);
                } else {
                    response.setStatus(404);
                }
            }
        }
    }

    protected void doDelete(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String key = request.getParameter("key");
        BlobKey blobKey = new BlobKey(key);
        blobstoreService.delete(blobKey);
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", true);
        JSONUtils.serialize(map, response);
    }

    private void sendBlobInfo(Query query, HttpServletResponse response,
                              boolean list) throws IOException {
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        PreparedQuery pq = datastore.prepare(query);
        List<Entity> entities = pq.asList(FetchOptions.Builder.withLimit(1));
        if (list) {
            JSONUtils.serialize(entities, response);
        } else if (entities.size() > 0) {
            JSONUtils.serialize(entities.get(0), response);
        }
    }

}
