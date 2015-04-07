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
    otherwise({
      redirectTo: '/messages'
    });
}]);
