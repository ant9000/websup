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

  // MESSAGING
  $scope.newmessage = {
    to: '',
    display: '',
    content: '',
    is_group: false
  }
  $scope.sendMessage = function(){
    socket.send(angular.extend({ type: 'message' }, $scope.newmessage));
    $scope.newmessage.content = '';
  }

  // GROUPS
  $scope.groups = {};
  $scope.current_group = null;
  $scope.participants = [];
  $scope.$on('group',function(evt,data){
    $log.log('GroupsCtrl',data);
    var group = data.content;
    if(!angular.isDefined($scope.groups[group.id])){
      $scope.groups[group.id] = { group_id: group.id };
    }
    angular.extend($scope.groups[group.id],group);
    if(group.id == $scope.current_group || group.id){ $scope.setGroup(group.id,false); }
  });
  $scope.setGroup = function(group_id,set_to){
    if(angular.isDefined($scope.groups[group_id])){
      $scope.current_group = group_id;
      $scope.participants = $scope.groups[group_id].participants || [];
      if(set_to!==false){
        $scope.newmessage.to = group_id;
        $scope.newmessage.display =  $scope.groups[group_id].subject || group_id;
        $scope.newmessage.is_group = true;
      }
    }
  }
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
    var display = '';
    if(message.is_group){
      var group = $scope.groups[number];
      if(group && group.subject){ display = group.subject; }
    }else{
      if(message.notify){ display = message.notify; }
    }
    var idx = $scope.conversationIds[number];
    if(!angular.isDefined(idx)){
      idx = $scope.conversations.length;
      $scope.conversationIds[number] = idx;
      $scope.conversations.push({ 
        number: number,
        is_group: message.is_group,
        messages: []
      });
    }
    $scope.conversations[idx]['display'] = display;
    $scope.conversations[idx]['last_timestamp'] = message.timestamp;
    $scope.conversations[idx]['messages'].push(message);
    $scope.setConversation(number,false);
  });
  $scope.setConversation = function(number,set_to){
    var idx = $scope.conversationIds[number];
    if(angular.isDefined(idx)){
      $scope.current_conversation = number;
      $scope.messages = $scope.conversations[idx]['messages'];
      if(set_to!==false){
        $scope.newmessage.to = number;
        $scope.newmessage.display = $scope.conversations[idx].display;
        $scope.newmessage.is_group = $scope.conversations[idx].is_group;
      }
    }
  }

  // Start communication
  socket.start();
}]);

websupControllers.controller('MessagesCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
}]);

websupControllers.controller('GroupsCtrl', ['$scope', 'socket', '$log', function($scope,socket,$log){
  $scope.setNewmessageTo = function(number){
    $scope.newmessage.to = number;
    $scope.newmessage.display = '';
    $scope.newmessage.is_group = false;
  }
}]);
