package com.appscale.hawkeye.appidentity;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.appidentity.AppIdentityService;
import com.google.appengine.api.appidentity.AppIdentityServiceFactory;
import org.apache.commons.codec.binary.Base64;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class SignBlobHandler extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        AppIdentityService appIdentity = AppIdentityServiceFactory.getAppIdentityService();
        String encodedBlob = request.getParameter("blob");
        byte[] blob = Base64.decodeBase64(encodedBlob);
        AppIdentityService.SigningResult result = appIdentity.signForApp(blob);

        Map<String,Object> signatureDetails = new HashMap<>();
        signatureDetails.put("key_name", result.getKeyName());
        String encodedSignature = Base64.encodeBase64String(result.getSignature());
        signatureDetails.put("signature", encodedSignature);
        JSONUtils.serialize(signatureDetails, response);
    }
}
