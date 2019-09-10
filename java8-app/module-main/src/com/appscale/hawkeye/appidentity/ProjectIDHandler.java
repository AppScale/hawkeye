package com.appscale.hawkeye.appidentity;

import com.google.apphosting.api.ApiProxy;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class ProjectIDHandler extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        String projectID = ApiProxy.getCurrentEnvironment().getAppId();
        response.getWriter().print(projectID);
    }
}
