$(function() {

	var socket = io.connect('/msgs');

    socket.on('connect', function () {
        socket.emit('join', window.user_id);
    });

    socket.on('newmsg', function (msg) {
    	alert('in newmsg');
    	window.console.log('in newmsg');
    	window.console.log(msg);
    	$('#msgs').prepend($('<div>').append($('<p>').text(msg.subject)));
    });
});