package com.appscale.hawkeye.appidentity;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.appidentity.AppIdentityService;
import com.google.appengine.api.appidentity.AppIdentityServiceFactory;
import com.google.appengine.api.appidentity.PublicCertificate;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class CertificateHandler extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        AppIdentityService appIdentity = AppIdentityServiceFactory.getAppIdentityService();
        Collection<PublicCertificate> certs = appIdentity.getPublicCertificatesForApp();

        List<Map<String,Object>> certMaps = new ArrayList<>();
        for (PublicCertificate publicCert : certs) {
            Map<String,Object> certDetails = new HashMap<>();
            certDetails.put("key_name", publicCert.getCertificateName());
            certDetails.put("pem", publicCert.getX509CertificateInPemFormat());
            certMaps.add(certDetails);
        }
        JSONUtils.serializeMaps(certMaps, response);
    }
}
