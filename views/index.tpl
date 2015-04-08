<!doctype html>
<html lang="en" ng-app="websup">
<head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>WebSup</title>
    <link rel="shortcut icon" href="/static/img/favicon.ico" type="image/x-icon" sizes="16x16 24x24 32x32 64x64"/>
    <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/bootstrap-theme.min.css">
    <link rel="stylesheet" href="/static/css/style.css">

    <script src="/static/js/angular.min.js"></script>
    <script src="/static/js/angular-route.min.js"></script>
    <script src="/static/js/angular-sanitize.min.js"></script>
    <script src="/static/js/ui-bootstrap-tpls-0.12.1.min.js"></script>

    <script src="/static/js/jquery-1.11.2.min.js"></script>
    <script src="/static/js/handlebars-v2.0.0.js"></script>

    <script src="/static/js/websup.app.js"></script>
    <script src="/static/js/websup.services.js"></script>
    <script src="/static/js/websup.controllers.js"></script>
</head>
<body ng-controller="MainCtrl">
    <div class="container">
        <div class="panel panel-primary">
            <div class="panel-heading">
                <div class="panel-title {{ connection_state }}" id="connection">
                    <h3>Websup!</h3>
                </div>
            </div>
            <div ng-if="username" class="panel-body">
                Welcome, <b>{{ username }}</b>.
            </div>
            <div ng-if="username && username.substr(0,9)!='anonymous'" class="panel-footer">
                Click to <span><a href="/logout">logout</a>.
            </div>
        </div>

        <div class="row">
            <p></p>
        </div>

       <div ng-view></div>
   </div>
</body>
</html>
