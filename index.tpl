<!doctype html>
<head>
    <meta charset="utf-8" />
    <title>WebSup</title>

    <style>
        li { list-style: none; }
    </style>

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
    <script>
        $(document).ready(function() {
            function log(message){
                $('#messages').append("<li>"+message+"</li>");
                $('#messages li:last').get(0).scrollIntoView();
            }
            if (!window.WebSocket) {
                if (window.MozWebSocket) {
                    window.WebSocket = window.MozWebSocket;
                } else {
                    log("Your browser doesn't support WebSockets.");
                }
            }
            var ws = new WebSocket('ws://127.0.0.1:8080/websocket');
            ws.onopen = function(evt) {
                log('WebSocket connection opened.');
                ws.send('');
            }
            ws.onmessage = function(evt) {
                log(evt.data);
            }
            ws.onclose = function(evt) {
                log('WebSocket connection closed.');
            }
        });
    </script>
</head>
<body>
    <h2>Websup!</h2>
    <div id="messages" style="height:400px;overflow:auto;border:1px solid #ccc;margin:2px;padding:2px;"></div>
</body>
</html>
