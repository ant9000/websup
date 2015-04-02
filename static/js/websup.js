'use strict';

// Declare app level module which depends on views, and components
var websup = angular.module('websup', [
  'ngRoute',
  'ui.bootstrap',
]);

websup.factory('socket', ['$window', function(win) {
  if(!win.WebSocket){
    if(win.MozWebSocket){
      win.WebSocket = win.MozWebSocket;
    }else{
      win.alert("Your browser doesn't support WebSockets.");
      return function(){};
    }
  }

  var ws;
  var state = 'disconnected';
  function connect(){
    state = 'connecting';
    ws = new WebSocket('ws://'+win.location.host+'/websocket');
    ws.onopen = function(evt) {
      state = 'connected';
      ws.send(JSON.stringify({type:'session',msg:'connected'}));
    }
    ws.onclose = function(evt) {
      state = 'disconnected';
      ws = null;
    }
    function checkConnection(){
      if((ws===null) && (state!='connecting')){ connect(); }
    }
    //automatic reconnection
    setInterval(checkConnection,1000); 
  }
  connect();
  return ws;
}]);

websup.controller('MainCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
  $scope.connection_state = socket.state;
  $scope.users = {};
  $scope.current_user = null;
  $scope.username = 'anonymous';

  socket.onmessage = function(evt){
    var message = JSON.parse(evt.data);
    $log.log(message);
    if(message.type == 'whatsapp'){
      $scope.current_user = message.number;
      if($scope.users[$scope.current_user] == undefined){
        $scope.users[$scope.current_user] = { 
          number: message.number,
          notify: message.notify,
          messages: []
        };
      }
      $scope.users[$scope.current_user]['last_timestamp'] = message.timestamp;
      $scope.users[$scope.current_user]['messages'].push(message);
    }else if(message.type=='session'){
      if(message.content=='reconnect'){
        // TODO: session expired
      } 
    }
  }
}]);
