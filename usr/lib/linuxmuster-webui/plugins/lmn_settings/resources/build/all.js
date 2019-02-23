// Generated by CoffeeScript 2.3.1
(function() {
  angular.module('lm.settings', ['core', 'lm.common']);

}).call(this);

// Generated by CoffeeScript 2.3.1
(function() {
  angular.module('lm.settings').config(function($routeProvider) {
    return $routeProvider.when('/view/lm/schoolsettings', {
      controller: 'LMSettingsController',
      templateUrl: '/lm_settings:resources/partial/index.html'
    });
  });

  angular.module('lm.settings').controller('LMSettingsController', function($scope, $http, $uibModal, gettext, notify, pageTitle, lmFileBackups) {
    pageTitle.set(gettext('Settings'));
    $scope.logLevels = [
      {
        name: gettext('Minimal'),
        value: 0
      },
      {
        name: gettext('Average'),
        value: 1
      },
      {
        name: gettext('Maximal'),
        value: 2
      }
    ];
    $scope.encodings = ['auto', 'ASCII', 'ISO_8859-1', 'ISO_8859-15', 'WIN-1252', 'UTF-8'];
    $http.get('/api/lm/schoolsettings').then(function(resp) {
      var encoding, file, i, len, ref, school, userfile;
      school = 'default-school';
      console.log(resp.data);
      encoding = {};
      ref = ['userfile.students.csv', 'userfile.extrastudents.csv', 'userfile.teachers.csv', 'userfile.extrastudents.csv'];
      //TODO: Remove comments
      //for file in ['userfile.students.csv', 'userfile.teachers.csv', 'userfile.extrastudents.csv', 'classfile.extraclasses.csv', ]
      for (i = 0, len = ref.length; i < len; i++) {
        file = ref[i];
        userfile = file.substring(file.indexOf('.') + 1);
        if (resp.data[file]['encoding'] === 'auto') {
          //console.log(userfile)
          console.log('is auto');
          $http.post('/api/lmn/schoolsettings/determine-encoding', {
            path: '/etc/linuxmuster/sophomorix/' + school + '/' + userfile,
            file: file
          }).then(function(response) {
            encoding[response['config']['data']['file']] = response.data;
            return console.log(encoding);
          });
        }
      }
      //console.log(encoding)
      $scope.encoding = encoding;
      return $scope.settings = resp.data;
    });
    $http.get('/api/lm/schoolsettings/school-share').then(function(resp) {
      return $scope.schoolShareEnabled = resp.data;
    });
    $scope.setSchoolShare = function(enabled) {
      $scope.schoolShareEnabled = enabled;
      return $http.post('/api/lm/schoolsettings/school-share', enabled);
    };
    $scope.save = function() {
      return $http.post('/api/lm/schoolsettings', $scope.settings).then(function() {
        return notify.success(gettext('Saved'));
      });
    };
    return $scope.backups = function() {
      return lmFileBackups.show('/etc/linuxmuster/sophomorix/user/sophomorix.conf');
    };
  });

}).call(this);

