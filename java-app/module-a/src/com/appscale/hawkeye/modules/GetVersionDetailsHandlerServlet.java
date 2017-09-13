package com.appscale.hawkeye.modules;

import com.appscale.hawkeye.JSONUtils;

import com.google.appengine.api.labs.modules.ModulesService;
import com.google.appengine.api.labs.modules.ModulesServiceFactory;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.Map;

public class GetVersionDetailsHandlerServlet extends HttpServlet {

    private ModulesService modulesApi = ModulesServiceFactory.getModulesService();
    private Logger logger = Logger.getLogger("modulesLogger");

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        Map<String,Object> map = new HashMap<String, Object>();
        String currentModuleName = modulesApi.getCurrentModule();
        logger.log(Level.INFO, "==================");
        logger.log(Level.INFO, currentModuleName);
        map.put("modules", modulesApi.getModules());
        map.put("current_module_versions", modulesApi.getVersions(currentModuleName));
        map.put("default_version", modulesApi.getDefaultVersion(currentModuleName));
        map.put("current_module", currentModuleName);
        map.put("current_version", modulesApi.getCurrentVersion());
        map.put("current_instance_id", modulesApi.getCurrentInstanceId());
        JSONUtils.serialize(map, response);
    }
}
