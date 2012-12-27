package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONSerializable;
import com.google.appengine.labs.repackaged.org.json.JSONException;
import com.google.appengine.labs.repackaged.org.json.JSONObject;

public class Module implements JSONSerializable {

    private String moduleId;
    private String name;
    private String description;

    public String getModuleId() {
        return moduleId;
    }

    public void setModuleId(String moduleId) {
        this.moduleId = moduleId;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public JSONObject toJSON() {
        try {
            return new JSONObject().
                    put("module_id", moduleId).
                    put("name", name).
                    put("description", description).
                    put("type", "module");
        } catch (JSONException e) {
            throw new RuntimeException("Error constructing JSON", e);
        }
    }
}
