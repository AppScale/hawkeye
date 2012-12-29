package com.appscale.hawkeye.datastore;

import com.appscale.hawkeye.JSONSerializable;
import com.google.appengine.labs.repackaged.org.json.JSONException;
import com.google.appengine.labs.repackaged.org.json.JSONObject;

public class Project implements JSONSerializable {

    public static final String PROJECT_ID = "project_id";
    public static final String NAME = "name";
    public static final String DESCRIPTION = "description";
    public static final String LICENSE = "license";
    public static final String RATING = "rating";


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
                    put(PROJECT_ID, projectId).
                    put(NAME, name).
                    put(DESCRIPTION, description).
                    put(LICENSE, license).
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
