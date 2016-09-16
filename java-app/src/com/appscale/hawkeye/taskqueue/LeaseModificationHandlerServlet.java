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
import java.lang.Math;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.Map;
import java.util.concurrent.Future;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;

public class LeaseModificationHandlerServlet extends HttpServlet {

    public static final String HAWKEYEJAVA_PULL_QUEUE = "hawkeyejava-PullQueue-0";
    private static final Queue queue = QueueFactory.getQueue(HAWKEYEJAVA_PULL_QUEUE);
    private static final int SMALL_WAIT = 5000;  // A small interval to wait for a service.

    private static final Logger logger = Logger.getLogger("foobar");

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        String payload = "hello world";
        TaskOptions taskOptions = TaskOptions.Builder
                                  .withMethod(TaskOptions.Method.PULL)
                                  .payload(payload);
        queue.add(taskOptions);

        try {
            Thread.sleep(SMALL_WAIT);
        } catch (InterruptedException e ){}

        int duration = 120;
        List<TaskHandle> tasks = queue.leaseTasks(duration, TimeUnit.SECONDS, 1);
        TaskHandle task = tasks.get(0);
        long eta = task.getEtaMillis();
        long expected = eta + duration*1000;
        try {
            assert Math.abs(eta-expected) < SMALL_WAIT;
        } catch (AssertionError e) {
            response.setStatus(500);
            response.getWriter().write("Initial Lease: ETA=" + eta + ", Expected=" + expected);
            return;
        }

        duration = 2;
        TaskHandle modified_task = queue.modifyTaskLease(task, duration, TimeUnit.SECONDS);
        long modified_eta = modified_task.getEtaMillis();
        expected = eta + duration*1000;
        try {
            assert Math.abs(modified_eta-expected) < SMALL_WAIT;
        } catch (AssertionError e) {
            response.setStatus(500);
            response.getWriter().write("Lease Update: ETA=" + eta + ", Expected=" + expected);
            return;
        }

        try {
            Thread.sleep(duration*1000);
        } catch (InterruptedException e ){}

        try {
            queue.modifyTaskLease(task, 240, TimeUnit.SECONDS);
        } catch (java.lang.IllegalStateException e) {
            return;
        }

        response.setStatus(500);
        response.getWriter().write("Task lease was modified after expiration.");
    }

}
