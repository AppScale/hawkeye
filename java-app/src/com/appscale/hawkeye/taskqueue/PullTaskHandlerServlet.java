package com.appscale.hawkeye.taskqueue;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.taskqueue.Queue;
import com.google.appengine.api.taskqueue.QueueFactory;
import com.google.appengine.api.taskqueue.TaskHandle;
import com.google.appengine.api.taskqueue.TaskOptions;

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

public class PullTaskHandlerServlet extends HttpServlet {

    public static final String HAWKEYEJAVA_PULL_QUEUE = "hawkeyejava-PullQueue-0";

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String key = request.getParameter("key");

        Queue queue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);
        queue.add(TaskOptions.Builder.withMethod(TaskOptions.Method.PULL).payload(key));

        Map<String,Object> map = new HashMap<String, Object>();
        map.put("status", true);
        JSONUtils.serialize(map, response);
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        Queue queue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);

        List<TaskHandle> tasks = queue.leaseTasks(3600, TimeUnit.SECONDS, 100);
        List<String> results = new ArrayList<String>();
        for (TaskHandle task : tasks) {
            results.add(new String(task.getPayload()));
        }
        queue.deleteTask(tasks);

        Map<String,Object> map = new HashMap<String, Object>();
        map.put("tasks", results);
        JSONUtils.serialize(map, response);
    }

    protected void doDelete(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        Queue queue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);
        queue.purge();
    }
}
