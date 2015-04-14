'use strict';

var websupControllers = angular.module('websupControllers', []);

websupControllers.controller('MainCtrl', ['$scope', '$location', 'socket', '$log', '$window', function($scope,$location,socket,$log,$window){
  // SESSION INFO
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
      $scope.refreshGroups();
    }else if(data.content=='not authenticated'){
      $window.location = '/login';
    } 
  });

  // GROUPS
  $scope.groups = {};
  $scope.first_group = null;
  $scope.$on('group',function(evt,data){
    $log.log('GroupsCtrl',data);
    var group = data.content;
    if(!angular.isDefined($scope.groups[group.id])){
      $scope.groups[group.id] = { group_id: group.id };
      if(!$scope.first_group){ $scope.first_group = group.id; }
    }
    angular.extend($scope.groups[group.id],group);
  });
  $scope.refreshGroups = function(group_id){
    socket.send({ type: 'group', 'command': 'groups-list' });
  }

  // CONVERSATIONS
  $scope.conversations = [];
  $scope.conversationIds = {};
  $scope.messages = [];
  $scope.current_conversation = null;
  $scope.$on('message',function(evt,data){
    $log.log('MessagesCtrl',data);
    var message = data.content;
    var number = message.own? message.to : message.from;
    var display = message.notify;
    if(message.is_group){
      var group = $scope.groups[number];
      if(group && group.subject){ display = group.subject; }
    }
    var idx = $scope.conversationIds[number];
    if(!angular.isDefined(idx)){
      idx = $scope.conversations.length;
      $scope.conversationIds[number] = idx;
      $scope.conversations.push({ 
        number: number,
        display: display,
        messages: []
      });
    }
    $scope.conversations[idx]['last_timestamp'] = message.timestamp;
    $scope.conversations[idx]['messages'].push(message);
    $scope.current_conversation = number;
    $scope.messages = $scope.conversations[idx]['messages'];
  });
  //
  socket.start();
}]);

websupControllers.controller('MessagesCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
  $scope.to = '';
  $scope.content = '';

  $scope.setConversation = function(number){
    var idx = $scope.conversationIds[number];
    if(angular.isDefined(idx)){
      $scope.current_conversation = number;
      $scope.messages = $scope.conversations[idx]['messages'];
      $scope.to = number;
    }
  }

  $scope.sendMessage = function(){
    socket.send({ type: 'message', 'to': $scope.to, 'content': $scope.content });
    $scope.content = '';
  }
}]);

websupControllers.controller('GroupsCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
  $scope.current_group = null;
  $scope.participants = [];
  $scope.setGroup = function(group_id){
    if(angular.isDefined($scope.groups[group_id])){
      $scope.current_group = group_id;
      $scope.participants = $scope.groups[group_id].participants || [];
    }
  }
  if($scope.first_group){ $scope.setGroup($scope.first_group); }
}]);
