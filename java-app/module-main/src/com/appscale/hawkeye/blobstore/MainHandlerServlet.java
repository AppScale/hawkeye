package com.appscale.hawkeye.blobstore;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.blobstore.BlobstoreService;
import com.google.appengine.api.blobstore.BlobstoreServiceFactory;
import com.google.appengine.api.blobstore.UploadOptions;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class MainHandlerServlet extends HttpServlet {

    private BlobstoreService blobstoreService = BlobstoreServiceFactory.getBlobstoreService();

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        Map<String,Object> map = new HashMap<String, Object>();
        String url = blobstoreService.createUploadUrl("/java/blobstore/upload");
        map.put("url", url);
        JSONUtils.serialize(map, response);
    }
}
