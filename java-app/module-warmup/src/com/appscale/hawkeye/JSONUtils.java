package com.appscale.hawkeye;

import com.google.appengine.api.datastore.Entity;
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
        response.getOutputStream().println(toJSON(entity).toString());
    }

    public static void serialize(Iterable<Entity> entities,
                                 HttpServletResponse response) throws IOException {
        List<JSONObject> list = new ArrayList<JSONObject>();
        for (Entity entity : entities) {
            list.add(toJSON(entity));
        }
        JSONArray jsonArray = new JSONArray(list);
        setContentType(response);
        response.getOutputStream().println(jsonArray.toString());
    }

    public static void serialize(Map<String,Object> map,
                                 HttpServletResponse response) throws IOException {
        JSONObject json = new JSONObject(map);
        setContentType(response);
        response.getOutputStream().println(json.toString());
    }

    private static JSONObject toJSON(Entity entity) {
        return new JSONObject(entity.getProperties());
    }

    private static void setContentType(HttpServletResponse response) {
        response.setContentType("application/json");
    }
}
