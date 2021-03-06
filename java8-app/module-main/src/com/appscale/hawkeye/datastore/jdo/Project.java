package com.appscale.hawkeye.datastore.jdo;

import com.google.appengine.api.datastore.Key;

import javax.jdo.annotations.PersistenceCapable;
import javax.jdo.annotations.Persistent;
import javax.jdo.annotations.PrimaryKey;
import javax.jdo.annotations.Cacheable;

@PersistenceCapable
public class Project {

    @PrimaryKey
    @Persistent
    private Key key;

    @Persistent
    private String name;

    @Persistent
    @Cacheable("false")
    private int rating;

    public Project(Key key, String name, int rating) {
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
