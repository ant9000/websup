'use strict';

// Declare app level module which depends on views, and components
var websup = angular.module('websup', [
  'ngRoute',
  'ui.bootstrap',
]);

websup.factory('socket', ['$rootScope', '$window', function($rootScope, $window) {
  if(!$window.WebSocket){
    if($window.MozWebSocket){
      $window.WebSocket = $window.MozWebSocket;
    }else{
      $window.alert("Your browser doesn't support WebSockets.");
      return function(){};
    }
  }

  var ws;
  $rootScope.connection_state = 'disconnected';
  function connect(){
    $rootScope.connection_state = 'connecting';
    ws = new WebSocket('ws://'+$window.location.host+'/websocket');
    ws.onopen = function(evt) {
      $rootScope.connection_state = 'connected';
      ws.send(JSON.stringify({type:'session',msg:'connected'}));
    }
    ws.onclose = function(evt) {
      $rootScope.connection_state = 'disconnected';
      ws = null;
    }
    function checkConnection(){
      if((ws===null) && ($rootScope.connection_state!='connecting')){ connect(); }
    }
    //automatic reconnection
    setInterval(checkConnection,1000); 
  }
  connect();
  return ws;
}]);

websup.controller('MainCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
  $scope.users = {};
  $scope.current_user = null;
  $scope.username = null;
  $scope.messages = [];

  socket.onmessage = function(evt){
    var data = JSON.parse(evt.data);
//  $log.log(data);
    if(data.type == 'whatsapp'){
      var message = data.content;
      $scope.$apply(function(){
        $scope.current_user = message.number;
//      $log.log($scope.current_user);
        if($scope.users[$scope.current_user] == undefined){
          $scope.users[$scope.current_user] = { 
            number: message.number,
            notify: message.notify,
            messages: []
          };
        }
        $scope.users[$scope.current_user]['last_timestamp'] = message.timestamp;
        $scope.users[$scope.current_user]['messages'].push(message);
        $scope.messages = $scope.users[$scope.current_user].messages;
      });
    }else if(data.type=='session'){
      if(data.content=='reconnect'){
        // TODO: session expired
      } 
    }
  }
}]);
