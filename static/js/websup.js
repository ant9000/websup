'use strict';

// Declare app level module which depends on views, and components
var websup = angular.module('websup', [
  'ngRoute',
  'ui.bootstrap',
  'ngSanitize'
]);

websup.factory('socket', ['$window', '$rootScope', '$interval', '$log', function($window, $rootScope, $interval, $log) {
  if(!$window.WebSocket){
    if($window.MozWebSocket){
      $window.WebSocket = $window.MozWebSocket;
    }else{
      $window.alert("Your browser doesn't support WebSockets.");
      return function(){};
    }
  }

  var ws = null;
  var connection_state = 'disconnected';
  function connect(){
    connection_state = 'connecting';
    $rootScope.$broadcast('connection', connection_state);
    ws = new WebSocket('ws://'+$window.location.host+'/websocket');
    ws.onopen = function(evt){
      connection_state = 'connected';
      $rootScope.$broadcast('connection', connection_state);
      ws.send(JSON.stringify({type:'session',msg:'connected'}));
    }
    ws.onclose = function(evt){
      connection_state = 'disconnected';
      $rootScope.$broadcast('connection', connection_state);
      ws = null;
    }
    ws.onmessage = function(evt){
      $rootScope.$broadcast('message', evt);
    }
  }
  function checkConnection(){
    if((ws===null) && (connection_state!='connecting')){ connect(); }
  }
  return {
     start: function(){
       //automatic reconnection
       $interval(checkConnection,1000); 
       connect();
     },
     send: function(number, content){
       ws.send(JSON.stringify({ type: 'message', number: number, content: content }));
     }
  }
}]);

websup.controller('MainCtrl', ['$scope', 'socket', '$log', '$window', function($scope,socket,$log,$window){
  $scope.username = null;
  $scope.current_user = null;
  $scope.users = {};
  $scope.messages = [];
  $scope.number = '';
  $scope.content = '';
  $scope.$on('connection',function(evt,state){
    $log.log(state);
    $scope.connection_state = state;
  });
  $scope.$on('message',function(evt,packet){
    var data = JSON.parse(packet.data);
    $log.log(data);
    if(data.type == 'whatsapp'){
      var message = data.content;
      $scope.current_user = message.number;
//    $log.log($scope.current_user);
      if($scope.users[$scope.current_user] == undefined){
        $scope.users[$scope.current_user] = { 
          number: message.number,
          notify: message.notify,
          messages: []
        };
      }
      $scope.users[$scope.current_user]['last_timestamp'] = message.timestamp;
      $scope.users[$scope.current_user]['messages'].push(message);
      $scope.messages = $scope.users[$scope.current_user]['messages'];
    }else if(data.type=='session'){
      if(data.content=='connected'){
        $scope.username = data.username;
      }else if(data.content=='not authenticated'){
        $window.location = '/login';
      } 
    }
  });
  $scope.setUser = function(number){
    $scope.current_user = number;
    $scope.messages = $scope.users[$scope.current_user]['messages'];
    $scope.number = parseInt(number);
  }
  $scope.sendMessage = function(){
    socket.send($scope.number,$scope.content);
    $scope.content = '';
  }
  socket.start();
}]);
