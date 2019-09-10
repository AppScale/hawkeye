package com.appscale.hawkeye.users;

import com.appscale.hawkeye.JSONUtils;
import com.google.appengine.api.users.User;
import com.google.appengine.api.users.UserService;
import com.google.appengine.api.users.UserServiceFactory;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class LoginURLHandlerServlet extends HttpServlet {

    protected void doGet(HttpServletRequest request,
                         HttpServletResponse response) throws ServletException, IOException {

        UserService userService = UserServiceFactory.getUserService();
        User user = userService.getCurrentUser();
        Map<String,Object> map = new HashMap<String, Object>();
        if (user != null) {
            map.put("type", "logout");
            map.put("url", userService.createLogoutURL("/java/users/"));
        } else {
            map.put("type", "login");
            map.put("url", userService.createLoginURL("/java/users/"));
        }
        JSONUtils.serialize(map, response);
    }
}
