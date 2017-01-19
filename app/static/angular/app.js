var app = angular.module("flask_app", []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

app.controller('loginview', function($scope){
  $scope.register = false;
  $scope.login = true;
  $scope.action_string = 'Register!';

  $scope.action  = () => {
    $scope.register = !$scope.register;
    if ($scope.register === true){
      $scope.login = false;
      $scope.action_string = 'Login!';
    } 
    else {
      $scope.login = true;
      $scope.action_string = 'Register!';
    }
  };

});

app.controller('requestview', function($scope){
  $scope.request = false;
  $scope.action_string = 'Create Request';
  $scope.table = false;
  $scope.request_table_string = 'Me Requests';
  $scope.edit = false;
  $scope.edit_string = 'Cancel';
  
  $scope.action = () => {
      $scope.request = !$scope.request;
      $scope.action_string = $scope.request === true
                              ? 'Cancel'
                              : 'Create Request';
    };

  $scope.request_table = () => {
      $scope.table = !$scope.table;
      $scope.request_table_string = $scope.table === true
                              ? 'Hide Requests'
                              : 'Me Requests';
  };

  $scope.request_edit  = () => {
    $scope.edit = true;
  };

  $scope.cancel = () => {
    $scope.edit = false;
  }

});