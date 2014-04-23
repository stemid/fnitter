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
      controller: 'fnitterManageAccountCtrl',
      resolve: { // Resolve service 
        'accountsData': function (accountsSrv) {
          return accountsSrv.promise;
        }
      }
    }).
    when('/tasks', {
      templateUrl: 'manage_tasks.html',
      controller: 'fnitterManageTasksCtrl',
      resolve: {
        'accountsData': function (accountsSrv) {
          return accountsSrv.promise;
        }
      }
    }).
    otherwise({
      redirectTo: '/'
    });
  }
]);

// Service to get account list anytime
fnitterApp.service('accountsSrv', [
  '$http', 
  'fnitterSettings', 
  
  function ($http, fnitterSettings) {
    var accounts = null;

    // Create a promise object 
    var promise = $http.get(fnitterSettings.apiUrl + '/accounts').
    success(function (data, status) {
      accounts = data.data;
    });

    return {
      // Expose promise object to get $http.success and .error methods. 
      promise: promise,
      get: function () {
        return accounts;
      }
    };
  }
]);

