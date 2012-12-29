package com.appscale.hawkeye.images;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.datastore.*;
import com.google.appengine.api.images.Image;
import com.google.appengine.api.images.ImagesService;
import com.google.appengine.api.images.ImagesServiceFactory;
import com.google.appengine.api.images.Transform;
import org.apache.commons.fileupload.FileItemIterator;
import org.apache.commons.fileupload.FileItemStream;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.servlet.ServletFileUpload;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class ProjectLogoHandlerServlet extends HttpServlet {

    public static final String PROJECT_LOGO = "ProjectLogo";
    public static final String PROJECT_LOGO_ID = "project_logo_id";
    public static final String PICTURE = "picture";

    private ImagesService imagesService = ImagesServiceFactory.getImagesService();

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String projectId = UUID.randomUUID().toString();
        ServletFileUpload fileUpload = new ServletFileUpload();
        try {
            FileItemIterator iterator = fileUpload.getItemIterator(request);
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            while (iterator.hasNext()) {
                FileItemStream item = iterator.next();
                if (!item.isFormField() && "file".equals(item.getFieldName())) {
                    InputStream in = item.openStream();
                    int len;
                    byte[] buffer = new byte[8192];
                    while ((len = in.read(buffer, 0, buffer.length)) != -1) {
                        out.write(buffer, 0, len);
                    }
                    break;
                }
            }

            Image image = ImagesServiceFactory.makeImage(out.toByteArray());
            Transform resize = ImagesServiceFactory.makeResize(100, 50);
            Image newImage = imagesService.applyTransform(resize, image);

            Entity projectLogo = new Entity(PROJECT_LOGO);
            projectLogo.setProperty(PROJECT_LOGO_ID, projectId);
            projectLogo.setProperty(PICTURE, new Blob(newImage.getImageData()));
            DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
            datastore.put(projectLogo);

            response.setStatus(HttpServletResponse.SC_CREATED);
            Map<String,Object> map = new HashMap<String, Object>();
            map.put("success", true);
            map.put("project_id", projectId);
            JSONUtils.serialize(map, response);
        } catch (FileUploadException e) {
            throw new ServletException("Error accessing file upload data", e);
        }
    }

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String projectId = request.getParameter("project_id");
        String metadata = request.getParameter("metadata");
        String resize = request.getParameter("resize");
        String rotate = request.getParameter("rotate");

        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        Query.FilterPredicate filter = new Query.FilterPredicate(PROJECT_LOGO_ID,
                Query.FilterOperator.EQUAL, projectId);
        Query q = new Query(PROJECT_LOGO).setFilter(filter);
        PreparedQuery preparedQuery = datastore.prepare(q);
        Entity entity = preparedQuery.asSingleEntity();

        Blob imageData = (Blob) entity.getProperty(PICTURE);
        Image image = ImagesServiceFactory.makeImage(imageData.getBytes());
        if ("true".equals(metadata)) {
            if (resize != null && !"".equals(resize)) {
                int width = Integer.parseInt(resize);
                Transform resizeTransform = ImagesServiceFactory.makeResize(width, 50);
                image = imagesService.applyTransform(resizeTransform, image);
            }
            if ("true".equals(rotate)) {
                Transform rotateTransform = ImagesServiceFactory.makeRotate(90);
                image = imagesService.applyTransform(rotateTransform, image);
            }

            Map<String,Object> map = new HashMap<String, Object>();
            map.put("height", image.getHeight());
            map.put("width", image.getWidth());
            map.put("format", image.getFormat().compareTo(Image.Format.PNG));
            JSONUtils.serialize(map, response);
        } else {
            response.setContentType("image/png");
            response.getOutputStream().write(image.getImageData());
        }
    }

    protected void doDelete(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        Query query = new Query(PROJECT_LOGO);
        DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();
        PreparedQuery preparedQuery = datastore.prepare(query);
        for (Entity entity : preparedQuery.asIterable()) {
            datastore.delete(entity.getKey());
        }
    }
}
