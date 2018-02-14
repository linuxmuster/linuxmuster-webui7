angular.module('lmn.session').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/session',
        controller: 'LMNSessionController'
        templateUrl: '/lmn_session:resources/partial/session.html'

angular.module('lmn.session').controller 'LMNSessionController', ($scope, $http, $location, $route, $uibModal, gettext, notify, messagebox, pageTitle, lmFileEditor, lmEncodingMap) ->
    pageTitle.set(gettext('Session'))


    $scope.showSessions = () ->
                $http.post('/api/lmn/sessions', {action: 'getSessions'}).then (resp) ->
                            messagebox.show(title: gettext('Initial password'), text: resp.data, positive: 'OK')

    $http.get("/api/lmn/session/senssions").then (resp) ->
                $scope.sessions = resp.data


