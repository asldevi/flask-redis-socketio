$(function() {

    var socket = io.connect('/msgs');

    socket.on('connect', function () {
        socket.emit('join', window.user_id);
    });

    socket.on('newmsg', function (msg) {
        if (msg.subject != undefined){
            $('#msgs').prepend($('<div>').append($('<b>').text(msg.subject + '   ' + msg.content + '   ' +  msg.sent_at)));
        }
    });
});