package com.appscale.hawkeye;

import com.appscale.hawkeye.datastore.Module;
import com.appscale.hawkeye.datastore.Project;
import com.google.appengine.api.datastore.Entity;
import com.google.appengine.api.datastore.PreparedQuery;
import com.google.appengine.labs.repackaged.org.json.JSONArray;
import com.google.appengine.labs.repackaged.org.json.JSONObject;

import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class JSONUtils {

    public static void serialize(Entity entity,
                                 HttpServletResponse response) throws IOException {
        setContentType(response);
        response.getOutputStream().println(toJSONSerializable(entity).toJSON().toString());
    }

    public static void serialize(Map<String,Object> map,
                                 HttpServletResponse response) throws IOException {
        JSONObject json = new JSONObject(map);
        setContentType(response);
        response.getOutputStream().println(json.toString());
    }

    public static void serialize(List<JSONSerializable> list,
                                 HttpServletResponse response) throws IOException {
        List<JSONObject> jsonObjects = new ArrayList<JSONObject>();
        for (JSONSerializable obj : list) {
            jsonObjects.add(obj.toJSON());
        }
        JSONArray json = new JSONArray(jsonObjects);
        setContentType(response);
        response.getOutputStream().println(json.toString());
    }

    public static void serialize(PreparedQuery preparedQuery,
                                 HttpServletResponse response) throws IOException {
        List<JSONSerializable> entities = new ArrayList<JSONSerializable>();
        for (Entity result : preparedQuery.asIterable()) {
            JSONSerializable json = toJSONSerializable(result);
            if (json != null) {
                entities.add(json);
            }
        }

        serialize(entities, response);
    }

    private static JSONSerializable toJSONSerializable(Entity entity) {
        if (entity.hasProperty("moduleId")) {
            Module module = new Module();
            module.setModuleId((String) entity.getProperty("moduleId"));
            module.setName((String) entity.getProperty("name"));
            module.setDescription((String) entity.getProperty("description"));
            return module;
        } else if (entity.hasProperty("projectId")) {
            Project project = new Project();
            project.setProjectId((String) entity.getProperty("projectId"));
            project.setName((String) entity.getProperty("name"));
            project.setDescription((String) entity.getProperty("description"));
            project.setLicense((String) entity.getProperty("license"));
            project.setRating((Long) entity.getProperty("rating"));
            return project;
        }
        return null;
    }

    private static void setContentType(HttpServletResponse response) {
        response.setContentType("application/json");
    }
}
