package com.appscale.hawkeye.channel;

import com.google.appengine.api.channel.ChannelService;
import com.google.appengine.api.channel.ChannelServiceFactory;

import java.io.IOException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class TokenHandler extends HttpServlet {
    public void doGet(HttpServletRequest request, HttpServletResponse response) throws IOException {
        ChannelService channelService = ChannelServiceFactory.getChannelService();
        String channelID = request.getParameter("channelID");
        String token = channelService.createChannel(channelID);
        response.getWriter().print(token);
    }
}
