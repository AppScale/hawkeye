package com.appscale.hawkeye.channel;

import com.google.appengine.api.channel.ChannelMessage;
import com.google.appengine.api.channel.ChannelService;
import com.google.appengine.api.channel.ChannelServiceFactory;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class MessageHandler extends HttpServlet {
    public void doPost(HttpServletRequest request, HttpServletResponse response) {
        ChannelService channelService = ChannelServiceFactory.getChannelService();
        String channelID = request.getParameter("channelID");
        String messageContent = request.getParameter("message");
        ChannelMessage message = new ChannelMessage(channelID, messageContent);
        channelService.sendMessage(message);
    }
}
