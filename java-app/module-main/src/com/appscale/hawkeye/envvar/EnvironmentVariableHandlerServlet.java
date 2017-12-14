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
	Map<String, String> env = System.getenv();
	String value = System.getenv("SHOULD_BE_BAZ");

        Map<String,Object> map = new HashMap<String, Object>();
        if (value != null) {
            map.put("success", true);
            map.put("value", value);
        } else {
            map.put("success", false);
            map.put("value", value);
        }
        JSONUtils.serialize(map, response);
    }
}
