'use strict';

var fnitterAppControllers = angular.module('fnitterAppControllers', []);

fnitterAppControllers.controller('fnitterActivityCtrl', [
  '$scope',
  '$http',
  '$log',
  'fnitterSettings',

  function ($scope, $http, $log, fnitterSettings) {
    // Make menu button active
    $('.list-group .active').toggleClass('active');
    $('.list-group').find('a[href$="/"]').toggleClass('active');
  }
]);

fnitterAppControllers.controller('fnitterNewAccountCtrl', [
  '$scope',
  '$http',
  '$log',
  'fnitterSettings',

  function ($scope, $http, $log, fnitterSettings) {
    // Make menu button active
    $('.list-group .active').toggleClass('active');
    $('.list-group').find('a[href$="/new"]').toggleClass('active');

    // Enable dismissal button in alert
    $('.close').on('click', function () {
      $('.alert').toggleClass('fade');
    });

    $scope.screen_name = '';

    $scope.new_person = function () {
      // Hide any possible alert
      $('.alert').addClass('fade');

      // Don't submit empty form
      if ($scope.person === undefined) {
        return 0;
      }
      $scope.screen_name = /[^/]*$/.exec($scope.person.screen_name)[0];
      if ( $scope.screen_name.length <= 0) {
        return 0;
      }

      $http({
        method: 'POST',
        headers: {
          'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        url: fnitterSettings.apiUrl + '/account/' + $scope.screen_name,
        data: $scope.screen_name
      }).
        success(function (data) {
          $('#newPersonForm').find("textarea input[type=text]").val("");
          $('.alert').removeClass('alert-warning');
          $('.alert').addClass('alert-success');
          $('.alert').toggleClass('fade');
          $log.info(data);
          $scope.post_status = 'Konto tillagt';
          $scope.post_message = data.message;
      }).
        error(function (data, status, headers, config) {
          $log.error('POST fail line: ' + data.line);
          $('.alert').removeClass('alert-success');
          $('.alert').addClass('alert-warning');
          $('.alert').toggleClass('fade');
          $scope.post_message = data.message;
          $scope.post_status = 'Kontot kunde inte läggas till';
      });
    };
  }
]);

fnitterAppControllers.controller('fnitterManageAccountCtrl', [
  '$scope',
  '$http',
  '$log',
  'fnitterSettings',

  function ($scope, $http, $log, fnitterSettings) {
    // Make menu button active
    $('.list-group .active').toggleClass('active');
    $('.list-group').find('a[href$="/manage"]').toggleClass('active');

    $scope.reload_list = function () {
      $http.get(fnitterSettings.apiUrl + '/accounts').
        success(function (data, status) {
          $log.info(data);
          $scope.accounts = data.data;
        }).
        error(function (data, status) {
          $log.error(data);
          $log.error(status);
          $scope.accounts = [];
        });
    };

    $scope.reload_list();
  }
]);

fnitterAppControllers.controller('fnitterManageTasksCtrl', [
  '$scope',
  '$http',
  '$log',
  
  function ($scope, $http, $log) {
  }
]);
