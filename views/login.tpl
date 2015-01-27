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
        });
    </script>
</head>
<body>
    <div id="connection">

      <h2>Login</h2>

% if error:
      <div class="error">{{ error }}</div>
% end

      <p>Please login with your credentials:</p>
      <form method="post" name="login">
          <input type="text" name="username" />
          <input type="password" name="password" />

          <br/><br/>
          <button type="submit"> Login </button>
      </form>
    </div>
</body>
</html>
