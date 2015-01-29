<!doctype html>
<head>
<style>
body {
  font:1em/1.4 Cambria, Georgia, sans-serif;
  color:#333;
  background:#fff;
}
.emoji { width: 18px; height: 18px; }
p { font-size: 70%; padding: 0; margin: 0; }
.sender { font-weight: bold; }
</style>
</head>
<body>
<p>[<span class="time">{{ item.datetime }}</span>] <span class="sender">{{ item.sender }}</span></p>
<hr />
{{! item.text }}
</body>
</html>
