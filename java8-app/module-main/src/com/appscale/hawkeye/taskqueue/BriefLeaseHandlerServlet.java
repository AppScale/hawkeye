package com.appscale.hawkeye.taskqueue;

import com.google.appengine.api.taskqueue.Queue;
import com.google.appengine.api.taskqueue.QueueFactory;
import com.google.appengine.api.taskqueue.TaskHandle;
import com.google.appengine.api.taskqueue.TaskOptions;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.TimeUnit;

public class BriefLeaseHandlerServlet extends HttpServlet {

    private static final String HAWKEYEJAVA_PULL_QUEUE = "hawkeyejava-PullQueue-0";
    private static final Queue queue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);
    private static final int SMALL_WAIT = 5000;  // A small interval to wait for a service.

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String payload = "hello world";
        queue.add(TaskOptions.Builder.withMethod(TaskOptions.Method.PULL).payload(payload));
        queue.add(TaskOptions.Builder.withMethod(TaskOptions.Method.PULL).payload(payload));

        try {
            Thread.sleep(SMALL_WAIT);
        } catch (InterruptedException e ) {
            response.setStatus(500);
            return;
        }

        // Only 2 tasks should be leased despite asking for 3.
        List<TaskHandle> tasks = queue.leaseTasks(1, TimeUnit.NANOSECONDS, 3);
        if (tasks.size() > 2) {
            response.setStatus(500);
            response.getWriter().write("Leased 3 tasks when only 2 were available.");
        }
    }

}
