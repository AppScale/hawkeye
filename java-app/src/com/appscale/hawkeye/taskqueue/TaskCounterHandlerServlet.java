package com.appscale.hawkeye.taskqueue;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.taskqueue.Queue;
import com.google.appengine.api.taskqueue.QueueFactory;
import com.google.appengine.api.taskqueue.QueueStatistics;
import com.google.appengine.api.taskqueue.TaskOptions;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class TaskCounterHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String key = request.getParameter("key");
        String stats = request.getParameter("stats");

        if (key != null && !key.isEmpty()) {
            Long count = TaskUtils.getCountByKey(key);
            if (count != null && !count.equals(-1)) {
                Map<String, Object> map = new HashMap<String, Object>();
                map.put(key, count);
                JSONUtils.serialize(map, response);
                return;
            } else {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            }
        } else if (stats.equals("true")) {
            QueueStatistics queueStatistics = QueueFactory.getDefaultQueue().fetchStatistics();
            Map<String, Object> map = new HashMap<String, Object>();
            map.put("queue", queueStatistics.getQueueName());
            map.put("tasks", queueStatistics.getNumTasks());
            map.put("oldest_eta", queueStatistics.getOldestEtaUsec());
            map.put("exec_last_minute", queueStatistics.getExecutedLastMinute());
            map.put("in_flight", queueStatistics.getRequestsInFlight());
            JSONUtils.serialize(map, response);
        }
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String key = request.getParameter("key");
        String getMethod = request.getParameter("get");
        String defer = request.getParameter("defer");
        String retry = request.getParameter("retry");
        String eta = request.getParameter("eta");

        Queue queue = QueueFactory.getDefaultQueue();
        if ("defer".equals(defer)) {
            DeferredCounterTask deferredCounterTask = new DeferredCounterTask(key);
            queue.add(TaskOptions.Builder.withPayload(deferredCounterTask));
        } else if ("true".equals(getMethod)) {
            TaskOptions taskOptions = TaskOptions.Builder.
                    withUrl("/java/taskqueue/worker?key=" + key).
                    method(TaskOptions.Method.GET);
            queue.add(taskOptions);
        } else {
            if (retry != null) {
                TaskOptions taskOptions = TaskOptions.Builder.
                        withUrl("/java/taskqueue/worker").
                        param("key", key).
                        param("retry", retry);
                queue.add(taskOptions);
            } else if (eta != null) {
                long adjustedEta = System.currentTimeMillis() + Long.parseLong(eta) * 1000;
                TaskOptions taskOptions = TaskOptions.Builder.
                        withUrl("/java/taskqueue/worker").
                        param("key", key).
                        param("eta", "true").
                        etaMillis(adjustedEta);
                queue.add(taskOptions);
            } else {
                queue.add(TaskOptions.Builder.withUrl("/java/taskqueue/worker").param("key", key));
            }
        }
        Map<String, Object> map = new HashMap<String, Object>();
        map.put("status", true);
        JSONUtils.serialize(map, response);
    }

    protected void doDelete(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        TaskUtils.deleteCounters();
    }
}
