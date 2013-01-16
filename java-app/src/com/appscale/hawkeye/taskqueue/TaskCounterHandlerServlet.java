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

    protected void doPost(HttpServletRequest request,
                          HttpServletResponse response) throws ServletException, IOException {

        String key = request.getParameter("key");
        String getMethod = request.getParameter("get");
        String defer = request.getParameter("defer");
        String retry = request.getParameter("retry");

        Queue queue = QueueFactory.getDefaultQueue();
        if ("defer".equals(defer)) {
            DeferredCounterTask deferredCounterTask = new DeferredCounterTask(key);
            queue.add(TaskOptions.Builder.withPayload(deferredCounterTask));
        } else if ("true".equals(getMethod)) {
            queue.add(TaskOptions.Builder.withUrl("/java/taskqueue/worker?key=" + key).
                    method(TaskOptions.Method.GET));
        } else {
            queue.add(TaskOptions.Builder.withUrl("/java/taskqueue/worker").param("key", key).param("retry", retry));
        }
        Map<String,Object> map = new HashMap<String, Object>();
        map.put("status", true);
        JSONUtils.serialize(map, response);
    }

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        String key = request.getParameter("key");
        String stats = request.getParameter("stats");
        if (key != null && !"".equals(key)) {
            long count = TaskUtils.getCountByKey(key);
            if (count == -1) {
                response.setStatus(HttpServletResponse.SC_NOT_FOUND);
            } else {
                Map<String,Object> map = new HashMap<String, Object>();
                map.put(key, count);
                JSONUtils.serialize(map, response);
            }
        } else if ("true".equals(stats)) {
            QueueStatistics queueStatistics = QueueFactory.getDefaultQueue().fetchStatistics();
            Map<String,Object> map = new HashMap<String, Object>();
            map.put("queue", queueStatistics.getQueueName());
            map.put("tasks", queueStatistics.getNumTasks());
            map.put("oldest_eta", queueStatistics.getOldestEtaUsec());
            map.put("exec_last_minute", queueStatistics.getExecutedLastMinute());
            map.put("in_flight", queueStatistics.getRequestsInFlight());
            JSONUtils.serialize(map, response);
        }
    }

    protected void doDelete(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        TaskUtils.deleteCounters();
    }
}
