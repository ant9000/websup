<!doctype html>
<html lang="en" ng-app="websup">
% # Angular.js uses the same syntax as STL for declaring variables,
% # so we include the template in a safe string
{{!"""
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
    <script src="/static/js/angular-route.js"></script>
    <script src="/static/js/ui-bootstrap-tpls-0.12.1.min.js"></script>

    <script src="/static/js/jquery-1.11.2.min.js"></script>
    <script src="/static/js/handlebars-v2.0.0.js"></script>

    <script src="/static/js/websup.js"></script>
</head>
<body ng-controller="MainCtrl">
    <div class="container">
        <div class="panel panel-primary">
            <div class="panel-heading">
                <div class="panel-title {{ connection_state }}">
                    <h3>Websup!</h3>
                </div>
            </div>
            <div class="panel-body">
                Welcome, <b>{{ username }}</b>.
            </div>
<!--
/ if username:
            <div class="panel-footer">
                    Click to <span><a href="/logout">logout</a>.
            </div>
/ end
-->
        </div>

        <div class="row">
            <p></p>
        </div>

        <div class="row">
            <div class="col-md-4">
                <div id="users-list" class="list-group">
                    <div ng-repeat="user in users" class="user list-group-item active" id="user-{{ user.number }}" data-number="{{ user.number }}">
                      <span class="number">{{ user.number }}<span ng-if="user.notify"> - {{ user.notify }}</span></span>
                      <p class="time text-right">{{ user.last_timestamp }}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div ng-if="current_user" ng-repeater="message in messages[current_user]" id="messages-container">
                     <div class="bubble {{ message.own }}">
                       <a ng-if="message.url" href="{{ message.url }}" target="_blank">
                         {{ message.thumb }} 
                         {{ message.text }}
                       </a>
                       <span ng-if="!message.url">
                         {{ message.thumb }} 
                         {{ message.text }}
                       </span>
                       <div style="text-align: right;" class="clearfix">
                         <p>[<span class="time">{{ message.timestamp }}</span>]</p>
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
</body>
"""}}
</html>
