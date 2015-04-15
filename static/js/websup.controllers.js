'use strict';

var websupControllers = angular.module('websupControllers', []);

websupControllers.controller('MainCtrl', ['$scope', '$location', 'socket', '$log', '$window', function($scope,$location,socket,$log,$window){
  $scope.$location = $location;

  // SESSION INFO
  $scope.username = null;
  $scope.$on('connection',function(evt,state){
    $log.log(state);
    $scope.connection_state = state;
  });
  $scope.$on('session',function(evt,data){
    $log.log('MainCtrl',data);
    var session = data.content;
    if(session.status=='connected'){
      $scope.username = session.username;
      $scope.phone = session.phone;
      $scope.refreshGroups();
    }else if(session.status=='not authenticated'){
      $window.location = '/login';
    }else if(session.status=='logged in'){
      // TODO
    }else if(session.status=='error'){
      // TODO
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
  $scope.groups = [];
  $scope.groupIds = {};
  $scope.current_group = null;
  $scope.participants = [];
  $scope.$on('group',function(evt,data){
    $log.log('GroupsCtrl',data);
    var group = data.content;
    var idx = $scope.groupIds[group.id];
    if(!angular.isDefined(idx)){
      idx = $scope.groups.length;
      $scope.groupIds[group.id] = idx;
      $scope.groups.push({ group_id: group.id });
    }
    angular.extend($scope.groups[idx],group);
    if(group.id == $scope.current_group || group.id){ $scope.setGroup(group.id,false); }
  });
  $scope.setGroup = function(group_id,set_to){
    var idx = $scope.groupIds[group_id];
    if(angular.isDefined(idx)){
      $scope.current_group = group_id;
      $scope.participants = $scope.groups[idx].participants || [];
      if(set_to!==false){
        $scope.newmessage.to = group_id;
        $scope.newmessage.display =  $scope.groups[idx].subject || group_id;
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
      var group = $scope.groups[$scope.groupIds[number]];
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

websupControllers.controller('MessagesCtrl', ['$scope', '$log', function($scope,$log){
}]);

websupControllers.controller('GroupsCtrl', ['$scope', '$log', function($scope,$log){
  $scope.setNewmessageTo = function(number){
    $scope.newmessage.to = number;
    $scope.newmessage.display = '';
    $scope.newmessage.is_group = false;
    angular.element('#newmessage-content').focus();
  }
}]);
