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
                Please login with your credentials.
            </div>
        </div>

% if error:
        <div class="row">
            <div class="col-md-8">
                <div class="alert alert-danger">{{ error }}</div>
           </div>
        </div>
% end

        <div class="row">
            <form method="post" name="login" class="form col-md-8">
                <div class="form-group row">
                    <label for="username" class="col-md-2">Username:</label>
                    <div class="col-xs-4">
                        <input type="text" name="username" id="username" class="form-control" autofocus />
                    </div>
                </div>
                <div class="form-group row">
                    <label for="password" class="col-md-2">Password:</label>
                    <div class="col-xs-4">
                        <input type="password" name="password" id="password" class="form-control" />
                    </div>
                </div>
                <button type="submit" class="btn btn-primary"> Login </button>
            </form>
        </div>

    </div>
    <script src="/static/js/jquery-1.11.2.min.js"></script>
    <script src="/static/js/handlebars-v2.0.0.js"></script>
    <script src="/static/js/bootstrap.min.js"></script>
</body>
</html>
