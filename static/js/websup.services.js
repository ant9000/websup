'use strict';

var websupServices = angular.module('websupServices', []);

websupServices.factory('socket', ['$window', '$rootScope', '$interval', '$log', function($window, $rootScope, $interval, $log) {
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
      var data = JSON.parse(evt.data);
      $log.log('socket',data)
      $rootScope.$broadcast(data.type, data);
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
