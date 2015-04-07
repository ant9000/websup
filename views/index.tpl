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

    <script src="/static/js/websup.js"></script>
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

        <div class="row">
            <div class="col-md-4">
                <div id="users-list" class="list-group">
                    <div ng-repeat="user in users|orderBy:'-last_timestamp'"
                         class="user list-group-item" ng-class="{ active: user.number == current_user }"
                         ng-click="setUser(user.number)">
                      <span class="number">{{ user.number }}<span ng-if="user.notify"> - {{ user.notify }}</span></span>
                      <p class="time text-right">{{ user.last_timestamp }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div ng-if="messages.length" ng-repeat="message in messages" id="messages-container">
                     <div class="bubble" ng-class="{ own: message.own }">
                       <a ng-if="message.url" href="{{ message.url }}" target="_blank">
                         <img ng-if="message.thumb" ng-src="{{ message.thumb }}" />
                         <span ng-bind-html="message.text"></span>
                       </a>
                       <span ng-if="!message.url">
                         <img ng-if="message.thumb" ng-src="{{ message.thumb }}" />
                         <span ng-bind-html="message.text"></span>
                       </span>
                       <div style="text-align: right;" class="clearfix">
                         <p>[<span class="time">{{ message.timestamp*1000 | date:'yyyy/MM/dd HH:mm:ss' }}</span>]</p>
                       </div>
                     </div>
                </div>
            </div>
        </div>

    </div>

    <nav class="navbar navbar-fixed-bottom">
        <div class="container">
            <div class="panel panel-primary">
                <div class="panel-body">
                    <div class="row">
                        <form id="msg-form" ng-submit="sendMessage()">
                            <div class="col-lg-2">
                                <input type="number" string-to-number class="form-control" placeholder="number" name="number" ng-model="number" required="" />
                            </div>
                            <div class="col-lg-9">
                                <input type="text" class="form-control" placeholder="content" name="content" ng-model="content" required="" />
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
</body>
</html>
