package com.appscale.hawkeye.envvar;

import com.appscale.hawkeye.JSONUtils;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class EnvironmentVariableHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {
        Map<String,Object> env = new HashMap<String, Object>();
        env.putAll(System.getenv());
        JSONUtils.serialize(env, response);
    }
}
