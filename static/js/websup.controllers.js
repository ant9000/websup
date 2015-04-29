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
    $scope.session = data.content;
    if($scope.session.status=='connected'){
      $scope.refreshGroups();
    }else if($scope.session.status=='not authenticated'){
      $window.location = '/login';
    }else if($scope.session.status=='logged in'){
      // TODO
    }else if($scope.session.status=='error'){
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
  function updateGroup(group){
    var idx = $scope.groupIds[group.id];
    if(!angular.isDefined(idx)){
      idx = $scope.groups.length;
      $scope.groupIds[group.id] = idx;
      $scope.groups.push({ group_id: group.id, participants: [] });
    }
    angular.extend($scope.groups[idx],group);
    if(group.id == ($scope.current_group || group.id)){ $scope.setGroup(group.id,false); }
  }
  $scope.$on('group-list',function(evt,data){
    $scope.groups = [];
    $scope.groupIds = {};
    $scope.current_group = null;
    $scope.participants = [];
    var groups = data.content.groups;
    for(var i=0;i<groups.length;i++){ updateGroup(groups[i]); }
  });
  $scope.$on('group',function(evt,data){
    updateGroup(data.content);
  });
  $scope.$on('group-add',function(evt,data){
    var group = data.content;
    var idx = $scope.groupIds[group.id];
    if(angular.isDefined(idx)){
      $scope.groups[idx].participants = _.union($scope.groups[idx].participants, group.participants);
      if($scope.current_group == group.id){ $scope.participants = $scope.groups[idx].participants; }
    }
  });
  $scope.$on('group-del',function(evt,data){
    var group = data.content;
    var idx = $scope.groupIds[group.id];
    if(angular.isDefined(idx)){
      $scope.groups[idx].participants = _.difference($scope.groups[idx].participants, group.participants);
      if($scope.current_group == group.id){ $scope.participants = $scope.groups[idx].participants; }
    }
  });
  $scope.$on('group-leave',function(evt,data){
    var group = data.content;
    var idx = $scope.groupIds[group.id];
    if(angular.isDefined(idx)){
      var groups = _.first($scope.groups,idx).concat(_.rest($scope.groups,idx+1));
      var groupIds = {};
      angular.forEach($scope.groups,function(group,idx){ groupIds[group.id] = idx; });
      $scope.groups = groups;
      $scope.groupIds = groupIds;
      if($scope.current_group == group.id){
        if($scope.groups.length){
          $scope.current_group = $scope.groups[0].id;
          $scope.participants = $scope.groups[0].participants;
        }else{
          $scope.current_group = null;
          $scope.participants = [];
        }
      }
    }
  });
  $scope.setGroup = function(group_id,set_to){
    var idx = $scope.groupIds[group_id];
    if(angular.isDefined(idx)){
      $scope.current_group = group_id;
      $scope.participants = $scope.groups[idx].participants;
      if(set_to!==false){
        $scope.newmessage.to = group_id;
        $scope.newmessage.display =  $scope.groups[idx].subject || group_id;
        $scope.newmessage.is_group = true;
      }
    }
  }
  $scope.refreshGroups = function(){
    socket.send({ type: 'group', command: 'list' });
  }
  $scope.groupInfo = function(group_id){
    socket.send({ type: 'group', command: 'info', group_id: group_id });
  }

  // CONVERSATIONS
  $scope.conversations = [];
  $scope.conversationIds = {};
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
      $scope.current_conversation = $scope.conversations[idx];
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

websupControllers.controller('MessagesCtrl', ['$scope', '$window', '$log', function($scope, $window, $log){
  $scope.messageRead = function(message_id){
     $window.alert('TODO');
  };
}]);

websupControllers.controller('GroupsCtrl', ['$scope', '$window', '$modal', 'socket', '$log', function($scope, $window, $modal, socket, $log){
  $scope.editGroup = function(group){
    var modalInstance = $modal.open({
      templateUrl: 'editGroup.html',
      controller: 'EditGroupCtrl',
      size: 'sm',
      resolve: {
         group: function(){ return angular.copy(group); }
      }
    });
    var initial = angular.copy(group);
    modalInstance.result.then(function(group) {
      $log.log('Edit group: ',group, initial);
      if(group.leave){
        $log.log('Leaving group: ', group.id);
        socket.send({ type: 'group', command: 'leave', 'group_id': group.id });
        return; // no need to change anything else
      }
      if(group.subject && (group.subject != initial.subject)){
        var command = group.id? 'subject' : 'create';
        socket.send({ type: 'group', 'command': command, 'group_id': group.id, 'subject': group.subject });
      }
      if(group.participants && (group.participants != initial.participants)){
        $log.log('Participants: ', group.participants, 'Initial: ', initial.participants);
        socket.send({ type: 'group', command: 'participants-set', 'group_id': group.id, 'old': initial.participants, 'new': group.participants });
      }
    }, function(){
      $log.log('Modal dismissed at: ' + new Date());
    });
  };
  $scope.messageGroupParticipant = function(number){
    $scope.newmessage.to = number;
    $scope.newmessage.display = '';
    $scope.newmessage.is_group = false;
    angular.element('#newmessage-content').focus();
  };
}]);

websupControllers.controller('EditGroupCtrl', function ($scope, $modalInstance, group) {
  $scope.group = group;
});
