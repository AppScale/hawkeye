package com.appscale.hawkeye.appidentity;

import com.google.apphosting.api.ApiProxy;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class HostnameHandler extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        ApiProxy.Environment env = ApiProxy.getCurrentEnvironment();
        String hostname = (String)env.getAttributes().get("com.google.appengine.runtime.default_version_hostname");
        response.getWriter().print(hostname);
    }
}
