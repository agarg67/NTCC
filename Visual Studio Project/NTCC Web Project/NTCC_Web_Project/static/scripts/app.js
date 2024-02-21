document.addEventListener('DOMContentLoaded', function () {
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    socket.on('connect', function () {
        console.log('Websocket connected!');
    });

    document.getElementById('commandForm').onsubmit = function (e) {
        e.preventDefault();
        var commandInput = document.getElementById('commandInput');
        var command = commandInput.value;
        socket.emit('send_command', { 'command': command });
        commandInput.value = '';
    };

    socket.on('server_response', function (data) {
        var outputElement = document.getElementById('output');
        outputElement.innerHTML += '<p>' + data.data + '</p>';
    });
});
