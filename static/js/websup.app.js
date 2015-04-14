'use strict';

var websup = angular.module('websup', [
  'ngRoute',
  'ui.bootstrap',
  'ngSanitize',
  'websupServices',
  'websupControllers',
]);

websup.config(['$routeProvider', function($routeProvider) {
  $routeProvider.
    when('/messages', {
      templateUrl: '/static/pages/messages.html',
      controller: 'MessagesCtrl'
    }).
    when('/groups', {
      templateUrl: '/static/pages/groups.html',
      controller: 'GroupsCtrl'
    }).
    otherwise({
      redirectTo: '/messages'
    });
}]);

websup.filter('cutDomain',function(){
  return function(input){
     return (input || '').replace(/@.*/,'');
  }
});
