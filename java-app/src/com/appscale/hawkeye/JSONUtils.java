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

    public static void serialize(JSONSerializable json,
                                 HttpServletResponse response) throws IOException {
        setContentType(response);
        response.getOutputStream().println(json.toJSON().toString());
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
        serialize(preparedQuery.asIterable(), response);
    }

    public static void serialize(Iterable<Entity> iterable,
                                 HttpServletResponse response) throws IOException {
        List<JSONSerializable> entities = new ArrayList<JSONSerializable>();
        for (Entity result : iterable) {
            JSONSerializable json = toJSONSerializable(result);
            if (json != null) {
                entities.add(json);
            }
        }

        serialize(entities, response);
    }

    private static JSONSerializable toJSONSerializable(Entity entity) {
        if (entity.hasProperty("module_id")) {
            Module module = new Module();
            module.setModuleId((String) entity.getProperty("module_id"));
            module.setName((String) entity.getProperty("name"));
            module.setDescription((String) entity.getProperty("description"));
            return module;
        } else if (entity.hasProperty("project_id")) {
            Project project = new Project();
            project.setProjectId((String) entity.getProperty("project_id"));
            project.setName((String) entity.getProperty("name"));
            project.setDescription((String) entity.getProperty("description"));
            project.setLicense((String) entity.getProperty("license"));
            if (entity.hasProperty("rating")) {
                project.setRating((Long) entity.getProperty("rating"));
            } else {
                project.setRating(-1);
            }
            return project;
        }
        return null;
    }

    private static void setContentType(HttpServletResponse response) {
        response.setContentType("application/json");
    }
}
