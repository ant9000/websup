<!doctype html>
<head>
    <meta charset="utf-8" />
    <title>WebSup</title>
    <link rel="shortcut icon" href="/static/img/favicon.ico" type="image/x-icon" sizes="16x16 24x24 32x32 64x64"/>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="/static/js/jquery-1.11.2.min.js"></script>
    <script>
        $(document).ready(function() {
            if (!window.WebSocket) {
                if (window.MozWebSocket) {
                    window.WebSocket = window.MozWebSocket;
                } else {
                    alert("Your browser doesn't support WebSockets.");
                    return;
                }
            }
            var ws, connecting=false;
            function connect(){
              connecting = true;
              ws = new WebSocket('ws://127.0.0.1:8080/websocket');
              ws.onopen = function(evt) {
                  connecting = false;
                  ws.send('connected');
                  $('#connection').addClass('connected');
              }
              ws.onmessage = function(evt) {
                var message = JSON.parse(evt.data);
                $('body').append('<div class="bubble">'+message.text+'</div>');
                $('body .bubble:last').get(0).scrollIntoView();
              }
              ws.onclose = function(evt) {
                  $('#connection').removeClass('connected');
                  connecting = false;
                  ws = null;
              }
            }
            function checkConnection(){
              if((ws===null) && !connecting){ connect(); }
            }
            setInterval(checkConnection,1000); 
            connect();
        });
    </script>
</head>
<body>
    <div id="connection"><h2>Websup!</h2></div>
</body>
</html>
