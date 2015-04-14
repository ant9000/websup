<!doctype html>
<html lang="en">
<head>
<style>
body {
  font:1em/1.4 Cambria, Georgia, sans-serif;
  color:#333;
  background:#fff;
}
p { font-size: 70%; padding: 0; margin: 0; }
.number { font-weight: bold; }
img { float: left; margin: 0px 15px; }
a { text-decoration: none; }
</style>
</head>
<body>
<%
from datetime import datetime
timestamp = datetime.fromtimestamp(message['timestamp'])
%> 
<p>
  [<span class="time">{{ timestamp }}</span>]
  <span class="number">
    {{! message[message.get('own',False) and 'to' or 'from'] }}
% if message.get('notify'):
    - {{! message['notify'] }}
% end
  </span>
</p>
<hr />
% if message.get('url'):
<a href="{{! message['url'] }}" target="_blank">
% end
% if message.get('thumb'):
<img src="{{! message['thumb'] }}" />
% end
{{! message['content'] }}
% if message.get('url'):
</a>
% end
</body>
</html>
