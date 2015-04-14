'use strict';

var websupControllers = angular.module('websupControllers', []);

websupControllers.controller('MainCtrl', ['$scope', '$location', 'socket', '$log', '$window', function($scope,$location,socket,$log,$window){
  $scope.$location = $location;
  $scope.username = null;
  $scope.$on('connection',function(evt,state){
    $log.log(state);
    $scope.connection_state = state;
  });
  $scope.$on('session',function(evt,data){
    $log.log('MainCtrl',data);
    if(data.content=='connected'){
      $scope.username = data.username;
      $scope.phone = data.phone;
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
    if(!angular.isDefined($scope.users[$scope.current_user])){
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
    $scope.number = number;
  }
  $scope.sendMessage = function(){
    socket.send({ type: 'message', 'number': $scope.number, 'content': $scope.content });
    $scope.content = '';
  }
}]);

websupControllers.controller('GroupsCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
  $scope.current_group = null;
  $scope.groups = {};
  $scope.participants = [];
  $scope.$on('group',function(evt,data){
    $log.log('GroupsCtrl',data);
    var group = data.content;
    if(!angular.isDefined($scope.groups[group.id])){
      $scope.groups[group.id] = { group_id: group.id };
    }
    angular.extend($scope.groups[group.id],group);
    if(group.id == $scope.current_group || group.id){ $scope.setGroup(group.id); }
  });
  $scope.setGroup = function(group_id){
    if(angular.isDefined($scope.groups[group_id])){
      $scope.current_group = group_id;
      $scope.participants = $scope.groups[group_id].participants || [];
    }
  }
  socket.send({ type: 'group', 'command': 'groups-list' });
}]);
