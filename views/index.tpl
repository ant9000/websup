<!doctype html>
<head>
    <meta charset="utf-8" />
    <title>WebSup</title>
    <link rel="shortcut icon" href="/static/img/favicon.ico" type="image/x-icon" sizes="16x16 24x24 32x32 64x64"/>
    <link rel="stylesheet" href="/static/css/style.css">
    <script src="/static/js/jquery-1.11.2.min.js"></script>
    <script src="/static/js/handlebars-v2.0.0.js"></script>
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
            var templates = {};
            $("script.template").each(function(){
                var source = $(this).html();
                var template = Handlebars.compile(source);
                templates[this.id] = template;
            });
            var ws, connecting=false;
            function connect(){
                connecting = true;
                ws = new WebSocket('ws://'+window.location.host+'/websocket');
                ws.onopen = function(evt) {
                    connecting = false;
                    ws.send('connected');
                    $('#connection').addClass('connected');
                }
                var counter=0;
                ws.onmessage = function(evt) {
                    var data = JSON.parse(evt.data);
                    if(data.type == 'whatsapp'){
                        var message = data.content;
                        message.odd = counter++ % 2;
                        $('body').append(templates['bubble'](message));
                        $('body .bubble:last').get(0).scrollIntoView();
                    }else if(data.type=='session'){
                        if(data.content=='reconnect'){
                            // TODO
                            alert('Session expired.');
                        } 
                    }
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
    <div id="connection">
        <h2>Websup!</h2>

        <p>Welcome, <b>{{ username }}</b>. Click to <span><a href="/logout">logout</a> </p>

    </div>
</body>
<script>
function pad(s) { return ((''+s).length<2?'0':'')+s; }
Handlebars.registerHelper('time', function(unix_timestamp) {
  var dt = new Date(unix_timestamp * 1000);
  var Y = dt.getFullYear();
  var M = pad(dt.getMonth()+1);
  var D = pad(dt.getDate());
  var h = pad(dt.getHours());
  var m = pad(dt.getMinutes());
  var s = pad(dt.getSeconds());
  return new Handlebars.SafeString(Y+'/'+M+'/'+D+' '+h+':'+m+':'+s);
});
</script>
% # Handlebars.js uses the same syntax as STL for declaring variables,
% # so we include the template in a safe string
{{!"""
<script id="bubble" class="template" type="text/x-handlebars-template">
<div class="bubble{{#if odd}} odd{{/if}}">
  <p>[<span class="time">{{ time timestamp }}</span>] <span class="sender">{{{ sender }}}</span></p>
  <hr />
  {{#if url}}<a href="{{{ url }}}" target="_blank">{{/if}}
    {{{ thumb }}} 
    {{{ text }}}
  {{#if url}}</a>{{/if}}
  <div style="clear:both;"></div>
</div>
</script>
"""}}
</html>
