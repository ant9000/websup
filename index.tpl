<!doctype html>
<head>
    <meta charset="utf-8" />
    <title>WebSocket Push Test</title>

    <style>
        li { list-style: none; }
    </style>

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
    <script>
        $(document).ready(function() {
            if (!window.WebSocket) {
                if (window.MozWebSocket) {
                    window.WebSocket = window.MozWebSocket;
                } else {
                    $('#messages').append("<li>Your browser doesn't support WebSockets.</li>");
                }
            }
            ws = new WebSocket('ws://127.0.0.1:8080/websocket');
            ws.onopen = function(evt) {
                $('#messages').prepend('<li>WebSocket connection opened.</li>');
                ws.send('');
            }
            ws.onmessage = function(evt) {
                $('#messages').prepend('<li>' + evt.data + '</li>');
            }
            ws.onclose = function(evt) {
                $('#messages').prepend('<li>WebSocket connection closed.</li>');
            }
        });
    </script>
</head>
<body>
    <h2>Bottle Websockets!</h2>
    <div id="messages" style="height:400px;overflow:auto;border:1px solid #ccc;margin:2px;padding:2px;"></div>
</body>
</html>
