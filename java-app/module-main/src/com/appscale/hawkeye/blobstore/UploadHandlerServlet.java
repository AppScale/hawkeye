package com.appscale.hawkeye.blobstore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.blobstore.BlobKey;
import com.google.appengine.api.blobstore.BlobstoreService;
import com.google.appengine.api.blobstore.BlobstoreServiceFactory;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class UploadHandlerServlet extends HttpServlet {

    private BlobstoreService blobstoreService = BlobstoreServiceFactory.getBlobstoreService();

    protected void doPost(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        Map<String, List<BlobKey>> blobs = blobstoreService.getUploads(request);
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("key", blobs.get("file").get(0).getKeyString());
        JSONUtils.serialize(map, response);
    }
}
