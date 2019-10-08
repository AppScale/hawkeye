async function getToken(channelID) {
    return new Promise((resolve, reject) => {
        let request = new XMLHttpRequest();
        let url = '/java/channel/get-token?channelID=' + channelID;
        request.open('GET', url);
        request.onload = function() {
            if (this.status >= 200 && this.status < 400) {
                resolve(this.response);
                return;
            } else {
                reject(new Error(this.response));
                return;
            }
        }
        request.onerror = function() {
            reject(new Error('Encountered error during request'));
        }
        request.send();
    });
};

function writeMessage(message) {
    document.getElementById('message').innerHTML = message.data;
}

function markOpen() {
    document.getElementById('message').innerHTML = 'Channel open';
}

async function openChannel(channelID) {
    let token = await getToken(channelID);
    let channel = new goog.appengine.Channel(token);
    var handler = {'onopen': markOpen, 'onmessage': writeMessage}
    let socket = channel.open(handler);
}

document.addEventListener('DOMContentLoaded', function(event) {
    // Assume the page was requested with '?channelID=<channel_id>'.
    let channelID = window.location.search.substring(1).split('=')[1];
    openChannel(channelID);
});
