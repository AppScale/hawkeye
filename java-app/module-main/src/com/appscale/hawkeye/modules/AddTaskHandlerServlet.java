package com.appscale.hawkeye.envvar;

import com.google.appengine.api.taskqueue.Queue;
import com.google.appengine.api.taskqueue.QueueFactory;
import com.google.appengine.api.taskqueue.TaskOptions;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class AddTaskHandlerServlet extends HttpServlet {

    DatastoreService datastore = DatastoreServiceFactory.getDatastoreService();

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
    	String id = request.getParameter("id");
    	String queue_name = request.getParameter("queue");
		
		if (queue == null)
        	Queue queue = QueueFactory.getDefaultQueue();
        else
        	Queue queue = QueueFactory.getQueue(queue_name);

        String url = "/modules/create-entity"
        TaskOptions options = TaskOptions.Builder.withUrl(url).param("id", id);
		queue.add(options);
    }
}
