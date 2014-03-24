'use strict';

$(document).ready(function () {
  $('[data-toggle=offcanvas]').click(function () {
    $('.row-offcanvas').toggleClass('active')
  });
});

var fnitterApp = angular.module('fnitterApp', [
  'ngRoute',
  'ui.bootstrap',
  'fnitterAppControllers'
]);

fnitterApp.constant('fnitterSettings', {
  apiUrl: 'http://zakalwe:8000'
});

fnitterApp.config([
  '$routeProvider',
  '$httpProvider',

  function ($routeProvider, $httpProvider) {
    // Först aktivera CORS (Cross Site JS Requests)
    $httpProvider.defaults.useXDomain = true;
    delete $httpProvider.defaults.headers.common['X-Requested-With'];

    $routeProvider.
      when('/', {
        templateUrl: 'account_activity.html',
        controller: 'fnitterActivityCtrl'
    }).
      when('/manage', {
        templateUrl: 'manage_account.html',
        controller: 'fnitterManageAccountCtrl'
    }).
      when('/tasks', {
        templateUrl: 'manage_tasks.html',
        controller: 'fnitterManageTasksCtrl'
    }).
      otherwise({
        redirectTo: '/'
    });
  }
]);
