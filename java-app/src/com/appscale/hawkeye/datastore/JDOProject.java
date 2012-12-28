package com.appscale.hawkeye.datastore;

import com.google.appengine.api.datastore.Key;

import javax.jdo.annotations.PersistenceCapable;
import javax.jdo.annotations.Persistent;
import javax.jdo.annotations.PrimaryKey;

@PersistenceCapable
public class JDOProject {

    @PrimaryKey
    @Persistent
    private Key key;

    @Persistent
    private String name;

    @Persistent
    private int rating;

    public JDOProject(Key key, String name, int rating) {
        this.key = key;
        this.name = name;
        this.rating = rating;
    }

    public Key getKey() {
        return key;
    }

    public String getName() {
        return name;
    }

    public int getRating() {
        return rating;
    }

    public void setKey(Key key) {
        this.key = key;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setRating(int rating) {
        this.rating = rating;
    }
}
