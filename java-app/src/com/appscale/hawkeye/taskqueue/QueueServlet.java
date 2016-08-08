package com.appscale.hawkeye.taskqueue;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.taskqueue.Queue;
import com.google.appengine.api.taskqueue.QueueFactory;
import com.google.appengine.api.taskqueue.TaskHandle;
import com.google.appengine.api.taskqueue.TaskOptions;

import org.json.JSONObject;
import org.json.JSONArray;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

public class QueueServlet extends HttpServlet {

    public static final String HAWKEYEJAVA_PUSH_QUEUE = "hawkeyejava-PushQueue-0";
    public static final String HAWKEYEJAVA_PULL_QUEUE = "hawkeyejava-PullQueue-0";

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        JSONObject result = new JSONObject();
        JSONArray queueArray = new JSONArray();
        JSONArray existsArray = new JSONArray();

        // Test each queue is working.
        Queue defaultQueue = QueueFactory.getDefaultQueue();
        TaskOptions pushTaskOptions = TaskOptions.Builder.
                withUrl("/java/taskqueue/clean_up");
        queueArray.put(defaultQueue.getQueueName());
        try {
            defaultQueue.add(pushTaskOptions);
            existsArray.put(true);
        } catch (java.lang.IllegalStateException exception) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            existsArray.put(false);
        }

        Queue pushQueue = QueueFactory.getQueue(HAWKEYEJAVA_PUSH_QUEUE);
        queueArray.put(pushQueue.getQueueName());
        try {
            pushQueue.add(pushTaskOptions);
            existsArray.put(true);
        } catch (java.lang.IllegalStateException exception) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            existsArray.put(false);
        }

        Queue pullQueue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);
        queueArray.put(pullQueue.getQueueName());
        try {
            pullQueue.add(TaskOptions.Builder.withMethod(TaskOptions.Method.PULL).payload("this is a fake payload"));
            existsArray.put(true);
        } catch (java.lang.IllegalStateException exception) {
            response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            existsArray.put(false);
        }

        // Send results.
        result.put("queues", queueArray);
        result.put("exists", existsArray);
        response.setContentType("application/json");
        response.getWriter().write(result.toString());

    }
}
