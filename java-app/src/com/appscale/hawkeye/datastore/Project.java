package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONSerializable;
import com.google.appengine.labs.repackaged.org.json.JSONException;
import com.google.appengine.labs.repackaged.org.json.JSONObject;

public class Project implements JSONSerializable {

    private String projectId;
    private String name;
    private String description;
    private String license;
    private long rating;

    public String getProjectId() {
        return projectId;
    }

    public void setProjectId(String projectId) {
        this.projectId = projectId;
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

    public String getLicense() {
        return license;
    }

    public void setLicense(String license) {
        this.license = license;
    }

    public long getRating() {
        return rating;
    }

    public void setRating(long rating) {
        this.rating = rating;
    }

    public JSONObject toJSON() {
        try {
            JSONObject json = new JSONObject().
                    put("project_id", projectId).
                    put("name", name).
                    put("description", description).
                    put("license", license).
                    put("type", "project");
            if (rating >= 0) {
                json.put("rating", rating);
            }
            return json;
        } catch (JSONException e) {
            throw new RuntimeException("Error constructing JSON", e);
        }
    }
}
