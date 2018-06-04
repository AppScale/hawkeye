package com.appscale.hawkeye.appidentity;

import com.google.appengine.api.appidentity.AppIdentityService;
import com.google.appengine.api.appidentity.AppIdentityServiceFactory;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

public class ServiceAccountNameHandler extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        AppIdentityService appIdentity = AppIdentityServiceFactory.getAppIdentityService();
        String serviceAccountName = appIdentity.getServiceAccountName();
        response.getWriter().print(serviceAccountName);
    }
}
