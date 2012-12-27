package com.appscale.hawkeye;

import com.google.appengine.labs.repackaged.org.json.JSONObject;

public interface JSONSerializable {

    public JSONObject toJSON();

}
