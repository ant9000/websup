<!doctype html>
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>WebSup</title>
    <link rel="shortcut icon" href="/static/img/favicon.ico" type="image/x-icon" sizes="16x16 24x24 32x32 64x64"/>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/bootstrap-theme.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div id="connection">
        <h2>Websup!</h2>
        <p>
            Welcome, <b>{{ username or 'anonymous' }}</b>.
% if username:
            Click to <span><a href="/logout">logout</a>.
% end
        </p>
    </div>

    <div class="container">
        <div class="row">
            <div id="users-list" class="col-md-4 list-group"></div>
            <div id="messages-container" class="col-md-8"></div>
        </div>
    </div>
<script src="/static/js/jquery-1.11.2.min.js"></script>
<script src="/static/js/handlebars-v2.0.0.js"></script>
<script src="/static/js/bootstrap.min.js"></script>
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
            ws.onmessage = function(evt) {
                var data = JSON.parse(evt.data);
                if(data.type == 'whatsapp'){
                    var message = data.content;
                    $('#users-list .user').removeClass('active');
                    $('#user-'+message.sender).remove();
                    $('#users-list').prepend(templates['user'](message));
                    var messages = $('#messages-'+message.sender);
                    if(!messages.length){
                        messages = $('<div>');
                        messages.attr('id','messages-'+message.sender);
                        messages.addClass('messages');
                        $('#messages-container').append(messages);
                    }
                    $('#messages-container .messages').hide();
                    messages.show();
                    message.odd = $('.bubble',messages).length % 2;
                    messages.append(templates['bubble'](message));
                    $('.bubble:last',messages).get(0).scrollIntoView();
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
        $('#users-list').on('click','.user',function(){
            var sender=$(this).data('sender');
            $('#users-list .user').removeClass('active');
            $('#user-'+sender).addClass('active');
            $('#messages-container .messages').hide();
            $('#messages-'+sender).show();
        });
    });
</script>
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
</body>
% # Handlebars.js uses the same syntax as STL for declaring variables,
% # so we include the template in a safe string
{{!"""
<script id="bubble" class="template" type="text/x-handlebars-template">
<div class="bubble{{#if odd}} odd{{/if}}">
  {{#if url}}<a href="{{{ url }}}" target="_blank">{{/if}}
    {{{ thumb }}} 
    {{{ text }}}
  {{#if url}}</a>{{/if}}
  <div style="text-align: right;" class="clearfix">
    <p>[<span class="time">{{ time timestamp }}</span>]</p>
  </div>
</div>
</script>
<script id="user" class="template" type="text/x-handlebars-template">
<div class="user list-group-item active" id="user-{{ sender }}" data-sender="{{ sender }}">
  <span class="sender">{{ sender }}{{#if notify}} - {{{ notify }}}{{/if}}</span>
  <p class="time text-right">{{ time timestamp }}</p>
</div>
</script>
"""}}
</html>
