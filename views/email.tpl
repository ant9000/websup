<!doctype html>
<head>
<style>
body {
  font:1em/1.4 Cambria, Georgia, sans-serif;
  color:#333;
  background:#fff;
}
p { font-size: 70%; padding: 0; margin: 0; }
.sender { font-weight: bold; }
img { float: left; margin: 0px 15px; }
a { text-decoration: none; }
</style>
</head>
<body>
<p>
  [<span class="time">{{ item.datetime }}</span>]
  <span class="sender">
    {{! item.sender }}
% if item.notify:
    - {{! item.notify }}
% end
  </span>
</p>
<hr />
% if item.url:
<a href="{{! item.url }}" target="_blank">
% end
{{! item.thumb }}
{{! item.text }}
% if item.url:
</a>
% end
</body>
</html>
