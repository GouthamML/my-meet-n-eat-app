var app = angular.module("flask_app", []);

app.config(['$interpolateProvider', function($interpolateProvider) {
  $interpolateProvider.startSymbol('{a');
  $interpolateProvider.endSymbol('a}');
}]);

app.controller('loginview', function($scope){
  $scope.register = false;
  $scope.login = true;
  $scope.action_string = 'Register!';


  $scope.action = function(){
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
  
  $scope.action = function(){
      $scope.request = !$scope.request;
      console.log($scope.request);
      $scope.action_string = $scope.request === true
                              ? 'Cancel'
                              : 'Create Request';
    };

});