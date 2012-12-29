package com.appscale.hawkeye.taskqueue;

import com.google.appengine.api.taskqueue.DeferredTask;

public class DeferredCounterTask implements DeferredTask {

    private String key;

    public DeferredCounterTask(String key) {
        this.key = key;
    }

    @Override
    public void run() {
        TaskUtils.process(key);
    }
}
