package com.appscale.hawkeye.datastore;

public class Counter {

    private long counter = 0;

    public long getCounter() {
        return counter;
    }

    public void setCounter(long counter) {
        this.counter = counter;
    }

    public void increment() {
        this.counter++;
    }
}
