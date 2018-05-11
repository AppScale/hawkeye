package com.appscale.hawkeye.warmup;

import com.google.appengine.api.datastore.Key;
import com.google.appengine.api.datastore.KeyFactory;

public class Constants {
    public static final Key WARMUP_KEY = KeyFactory.createKey("WarmupEntity", "warmup-key");
}
