<!doctype html>
<head>
    <meta charset="utf-8" />
    <title>WebSup</title>

    <style>
        li { list-style: none; }
        #connection { background: url(/static/img/bullet-black-icon.png) no-repeat; padding-left: 36px; }
        #connection.connected { background-image: url(/static/img/bullet-blue-icon.png); }
        .emoji { width: 18px; height: 18px; }
    </style>

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.4/jquery.min.js"></script>
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
                var message = evt.data;
                $('#messages').append("<li>"+message+"</li>");
                $('#messages li:last').get(0).scrollIntoView();
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
    <div id="messages" style="height:400px;overflow:auto;border:1px solid #ccc;margin:2px;padding:2px;"></div>
</body>
</html>
