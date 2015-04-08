'use strict';

var websupControllers = angular.module('websupControllers', []);

websupControllers.controller('MainCtrl', ['$scope', 'socket', '$log', '$window', function($scope,socket,$log,$window){
  $scope.username = null;
  $scope.$on('connection',function(evt,state){
    $log.log(state);
    $scope.connection_state = state;
  });
  $scope.$on('session',function(evt,data){
    $log.log('MainCtrl',data);
    if(data.content=='connected'){
      $scope.username = data.username;
    }else if(data.content=='not authenticated'){
      $window.location = '/login';
    } 
  });
  socket.start();
}]);

websupControllers.controller('MessagesCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
  $scope.current_user = null;
  $scope.users = {};
  $scope.messages = [];
  $scope.number = '';
  $scope.content = '';
  $scope.$on('message',function(evt,data){
    $log.log('MessagesCtrl',data);
    var message = data.content;
    $scope.current_user = message.number;
//  $log.log($scope.current_user);
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
}]);
