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
import java.util.concurrent.Future;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

public class PullTaskHandlerServlet extends HttpServlet {

    public static final String HAWKEYEJAVA_PULL_QUEUE = "hawkeyejava-PullQueue-0";
    private static final Queue queue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String key = request.getParameter("key");
        String action = request.getParameter("action");

        Map<String,Object> map = new HashMap<String, Object>();
        if ("add".equals(action)) {
            TaskOptions taskOptions = TaskOptions.Builder
                                      .withMethod(TaskOptions.Method.PULL)
                                      .payload(key);
            queue.add(taskOptions);
            map.put("success", true);
            JSONUtils.serialize(map, response);
        } else if ("add_async".equals(action)) {
            byte[] tag = "newest".getBytes();
            TaskOptions taskOptions = TaskOptions.Builder.withMethod(TaskOptions.Method.PULL)
                                      .payload(key)
                                      .tag(tag)
                                      .countdownMillis(10000);
            Future<TaskHandle> future = queue.addAsync(taskOptions);
            try {
                TaskHandle task = future.get();
                map.put("success", true);
                JSONUtils.serialize(map, response);
            } catch(InterruptedException e) {
                return;
            } catch(ExecutionException e) {
                return;
            }
        }
    }

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String action = request.getParameter("action");
        String tag = request.getParameter("tag");

        Map<String,Object> map = new HashMap<String, Object>();
        map.put("success", true);
        List<String> results = new ArrayList<String>();

        if ("lease".equals(action)) {
            logger.log(Level.INFO, "Action: leaseTasks & deleteTaskAsync");
            List<TaskHandle> tasks = queue.leaseTasks(3600, TimeUnit.SECONDS, 100);
            for (TaskHandle task : tasks) {
                results.add(new String(task.getPayload()));
                Future<Boolean> future = queue.deleteTaskAsync(task);
                try {
                    if (!future.get()) {
                        response.getWriter().write("deleteTaskAsync failed");
                        return;
                    }
                } catch(InterruptedException e) {
                    return;
                } catch(ExecutionException e) {
                    return;
                }
            }
        } else if ("lease_by_tag".equals(action)) {
            logger.log(Level.INFO, "Action: leaseTasksByTag & deleteTask by name");
            List<TaskHandle> tasks = queue.leaseTasksByTag(3600, TimeUnit.SECONDS, 100, tag);
            for (TaskHandle task : tasks) {
                results.add(new String(task.getPayload()));
                if (!queue.deleteTask(task.getName())) {
                    response.getWriter().write("deleteTask by name failed");
                    return;
                }
            }
        }

        map.put("tasks", results);
        JSONUtils.serialize(map, response);
    }

    protected void doDelete(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {
        Queue queue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);
        queue.purge();
    }
}
