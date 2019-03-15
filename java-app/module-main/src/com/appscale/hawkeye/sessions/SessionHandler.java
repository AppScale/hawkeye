package com.appscale.hawkeye.sessions;

import com.appscale.hawkeye.JSONUtils;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

public class SessionHandler extends HttpServlet {
    private String instanceID = UUID.randomUUID().toString();

    public void doPost(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String name = request.getParameter("name");
        HttpSession session = request.getSession();
        session.setAttribute("name", name);
        response.getWriter().print(instanceID);
    }

    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        HttpSession session = request.getSession(false);
        if (session == null) {
            response.setStatus(404);
            response.getWriter().print("Session not found");
            return;
        }

        String name = (String)session.getAttribute("name");
        Map<String,Object> sessionDetails = new HashMap<>();
        sessionDetails.put("instanceId", instanceID);
        sessionDetails.put("name", name);
        JSONUtils.serialize(sessionDetails, response);
    }
}
