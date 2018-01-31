package com.appscale.hawkeye.appidentity;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.appidentity.AppIdentityService;
import com.google.appengine.api.appidentity.AppIdentityServiceFactory;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

public class AccessTokenHandler extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        ArrayList<String> scopes = new ArrayList<>();
        scopes.add("https://www.googleapis.com/auth/cloud-platform");
        AppIdentityService appIdentity = AppIdentityServiceFactory.getAppIdentityService();
        AppIdentityService.GetAccessTokenResult accessToken = appIdentity.getAccessToken(scopes);

        Map<String,Object> accessTokenDetails = new HashMap<>();
        accessTokenDetails.put("token", accessToken.getAccessToken());
        Date expirationTime = accessToken.getExpirationTime();
        accessTokenDetails.put("expires", Long.toString(expirationTime.getTime()));
        JSONUtils.serialize(accessTokenDetails, response);
    }
}
