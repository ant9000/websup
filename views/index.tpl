<!doctype html>
<html lang="en">
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
    <div class="container">
        <div class="panel panel-primary">
            <div class="panel-heading">
                <div class="panel-title" id="connection">
                    <h3>Websup!</h3>
                </div>
            </div>
            <div class="panel-body">
                Welcome, <b>{{ username or 'anonymous' }}</b>.
            </div>
% if username:
            <div class="panel-footer">
                    Click to <span><a href="/logout">logout</a>.
            </div>
% end
        </div>

        <div class="row">
            <p></p>
        </div>

        <div class="row">
            <div class="col-md-4">
                <div id="users-list" class="list-group"></div>
            </div>
            <div class="col-md-4">
                <div id="messages-container"></div>
            </div>
        </div>

    </div>

    <nav class="navbar navbar-fixed-bottom">
        <div class="container">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <div class="row">
                        <form id="msg-form">
                            <div class="col-lg-2">
                                <input type="text" class="form-control" placeholder="number" id="number" name="number" />
                            </div>
                            <div class="col-lg-9">
                                <input type="text" class="form-control" placeholder="content" id="content" name="content" />
                            </div>
                            <div class="col-lg-1">
                                <button type="submit" class="btn btn-default pull-right"> Send </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </nav>

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
        function showMessage(message,own){
            $('#users-list .user').removeClass('active');
            $('#user-'+message.number).remove();
            $('#users-list').prepend(templates['user'](message));
            var messages = $('#messages-'+message.number);
            if(!messages.length){
                messages = $('<div>');
                messages.attr('id','messages-'+message.number);
                messages.addClass('messages');
                $('#messages-container').append(messages);
            }
            $('#messages-container .messages').hide();
            messages.show();
            message.odd = $('.bubble',messages).length % 2;
            message.own = own ? 1 : 0;
            messages.append(templates['bubble'](message));
            $('.bubble:last',messages).get(0).scrollIntoView();
        }
        function connect(){
            connecting = true;
            ws = new WebSocket('ws://'+window.location.host+'/websocket');
            ws.onopen = function(evt) {
                connecting = false;
                ws.send(JSON.stringify({type:'session',msg:'connected'}));
                $('#connection').addClass('connected');
            }
            ws.onmessage = function(evt) {
                var data = JSON.parse(evt.data);
                if(data.type == 'whatsapp'){
                    showMessage(data.content);
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
            var number=$(this).data('number');
            $('#users-list .user').removeClass('active');
            $('#user-'+number).addClass('active');
            $('#messages-container .messages').hide();
            $('#messages-'+number).show();
            $('#number').val(number);
        });
        $('#msg-form').on('submit',function(e){
            e.preventDefault();
            var number = $('#number').val(), content = $('#content').val();
            if($.isNumeric(number) && !$.isEmptyObject(content)){
                ws.send(JSON.stringify({ type: 'message', number: number, content: content }));
                $('#content').val('');
            }
        });
    });
</script>
<script>
function pad(s) { return ((''+s).length<2?'0':'')+s; }
Handlebars.registerHelper('time', function(unix_timestamp) {
  var dt = unix_timestamp ? new Date(unix_timestamp * 1000) : new Date();
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
<div class="bubble{{#if odd}} odd{{/if}}{{#if own}} own{{/if}}">
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
<div class="user list-group-item active" id="user-{{ number }}" data-number="{{ number }}">
  <span class="number">{{ number }}{{#if notify}} - {{{ notify }}}{{/if}}</span>
  <p class="time text-right">{{ time timestamp }}</p>
</div>
</script>
"""}}
</html>
