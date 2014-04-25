'use strict';

var fnitterAppControllers = angular.module('fnitterAppControllers', []);

fnitterAppControllers.controller('fnitterActivityCtrl',
  function ($scope, $http, $log, fnitterSettings) {
    // Make menu button active
    $('.list-group .active').toggleClass('active');
    $('.list-group').find('a[href$="/"]').toggleClass('active');

    $scope.listener_status = function () {
      $http.get(fnitterSettings.apiUrl + '/task/Driver.tasks.follow_accounts').
        success(function (data, status) {
          $log.info(data);
          return true;
        }).
        error(function (data, status) {
          $log.error(status);
          return false;
        });
    };

    if ($scope.listener_status() === true) {
      $scope.listener_mode = 'play';
    } else {
      $scope.listener_mode = 'stop';
    }
  }
);

fnitterAppControllers.controller('fnitterManageAccountCtrl',
  function ($scope, $http, $log, fnitterSettings, accountsSrv) {
    // Make menu button active
    $('.list-group .active').toggleClass('active');
    $('.list-group').find('a[href$="/manage"]').toggleClass('active');

    $scope.accounts = [];
    $scope.accounts = accountsSrv.get();

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
);

fnitterAppControllers.controller('fnitterManageTasksCtrl', 
  function ($scope, $http, $log, $timeout, fnitterSettings, accountsSrv) {
    // Make menu button active
    $('.list-group .active').toggleClass('active');
    $('.list-group').find('a[href$="/tasks"]').toggleClass('active');

    $scope.listener_running = false;
    $scope.listener_toggle_text = 'Starta lyssnaren';
    $scope.listener_toggle = function () {};

    // Get status of listener task
    $scope.listener_status = function () {
      $http.get(fnitterSettings.apiUrl + '/tasks/Tasks.follow_accounts').
      success(function (data, status) {
        $scope.listener_toggle_text = 'Stoppa lyssnaren';
        $scope.listener_running = true;
        $('#listener-button').prop('disabled', true);
      }).
      error(function (data, status) {
        $scope.listener_toggle_text = 'Starta lyssnaren';
        $scope.listener_running = false;
        $('#listener-button').prop('disabled', false);
      });
    };
    $scope.listener_status();

    // Toggle the listener task
    $scope.listener_toggle = function () {
      $scope.listener_status();
      if ($scope.listener_running === true) {
        $http.delete(fnitterSettings.apiUrl + '/tasks/Tasks.follow_accounts').
        success(function (data, status) {
          $log.info('killed listener task');
        }).
        error(function (data, status) {
          $log.error('failed killing listener task');
        });
      } else {
        // Get accounts list
        $scope.accounts = accountsSrv.get();
        var task_arguments = [];
        $.each($scope.accounts, function (index, value) {
          task_arguments.push(value.user_id);
        });

        $log.info(task_arguments);
        $http.post(
          fnitterSettings.apiUrl + '/tasks/Tasks.follow_accounts?unique=true',
          { data: task_arguments }
        ).success(function (data, status) {
          $log.info('starting listener task');
        }).error(function (data, status) {
          $log.error('failed starting listener task');
        });
      }
    };

    // Reload tasks list
    $scope.reload_tasks = function () {
      $http.get(fnitterSettings.apiUrl + '/tasks').
      success(function (data, status) {
        $log.info(data);
        $scope.tasks = data.tasks;
      }).
      error(function (data, status) {
        $log.error(data);
        $log.error(status);
        $scope.tasks = [];
      });
    };

    $scope.reload_tasks();

    // Reload tasks list constantly
    $timeout(function () {
      $log.info('updating tasks');
      $scope.reload_tasks();
    }, 3000);
  }
);
