'use strict';

angular.module('lm.setup_wizard', ['core', 'ajenti.network']);

angular.module('lm.setup_wizard').run(function ($http, $location, identity) {
  identity.promise.then(function () {
    if (identity.user) {
      $http.get('/api/lm/setup-wizard/is-configured').then(function (response) {
        if (!response.data) {
          $location.path('/view/lm/init/welcome');
        }
      });
    }
  });
});


'use strict';

angular.module('lm.setup_wizard').config(function ($routeProvider) {
  $routeProvider.when('/view/lm/init/welcome', {
    templateUrl: '/lm_setup_wizard:partial/init-welcome.html',
    controller: 'InitWelcomeController',
    controllerAs: '$ctrl'
  });

  $routeProvider.when('/view/lm/init/school', {
    templateUrl: '/lm_setup_wizard:partial/init-school.html',
    controller: 'InitSchoolController',
    controllerAs: '$ctrl'
  });

  $routeProvider.when('/view/lm/init/account', {
    templateUrl: '/lm_setup_wizard:partial/init-account.html',
    controller: 'InitAccountController',
    controllerAs: '$ctrl'
  });

  $routeProvider.when('/view/lm/init/externalservices', {
    templateUrl: '/lm_setup_wizard:partial/init-externalServices.html',
    controller: 'InitExternalServicesController',
    controllerAs: '$ctrl'
  });

  $routeProvider.when('/view/lm/init/setup', {
    templateUrl: '/lm_setup_wizard:partial/init-setup.html',
    controller: 'InitSetupController',
    controllerAs: '$ctrl'
  });
});

angular.module('lm.setup_wizard').controller('InitWelcomeController', function (gettext, pageTitle, $http, config) {
  var _this = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.config = config;
  $http.get('/api/core/languages').then(function (response) {
    return _this.languages = response.data;
  });

  this.apply = async function () {
    await _this.config.save();
    $location.path('/view/lm/init/account');
  };
});

angular.module('lm.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle, notify) {
  var _this2 = this;

  pageTitle.set(gettext('Setup Wizard'));
  $http.get('/api/core/languages').then(function (response) {
    return _this2.languages = response.data;
  });
  this.ini = {};
  this.apply = async function () {
    $dataMissing = false;

    var fields = ["schoolname", "servername", "domainname"];

    for (var i = 0; i < fields.length; i++) {
      var field = fields[i];
      if (_this2.ini[field] == null || _this2.ini[field] == '') {
        document.getElementById(field + '-input').style.background = 'rgba(255, 178, 178, 0.29)';
        document.getElementById(field + '-input').style.borderColor = 'red';
        $dataMissing = true;
      } else {
        document.getElementById(field + '-input').style.background = '';
        document.getElementById(field + '-input').style.borderColor = '';
      }
    }

    if ($dataMissing == true) {
      notify.error('Required data missing');
      return;
    }
    await $http.post('/api/lm/setup-wizard/update-ini', _this2.ini);
    $location.path('/view/lm/init/account');
  };
});

angular.module('lm.setup_wizard').controller('InitAccountController', function ($scope, $location, $http, gettext, pageTitle, notify) {
  var _this3 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};
  this.apply = function () {
    if (_this3.ini.adminpw != _this3.adminpwConfirmation) {
      notify.error('Administrator password missmatch');
      return;
    }
    if (!isStrongPwd1(_this3.ini.adminpw)) {
      notify.error('Password too weak');
      return;
    }
    $http.post('/api/lm/setup-wizard/update-ini', _this3.ini).then(function () {
      return $location.path('/view/lm/init/externalservices');
    });
  };
});

angular.module('lm.setup_wizard').controller('InitExternalServicesController', function ($location, $http, gettext, pageTitle, notify) {
  var _this4 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};

  this.finish = function () {
    if (_this4.ini.smtppw != _this4.smtppwConfirmation) {
      notify.error('SMTP password missmatch');
      return;
    }
    if (!_this4.enableOPSI) {
      delete _this4.ini['opsiip'];
    }
    if (!_this4.enableDocker) {
      delete _this4.ini['dockerip'];
    }
    if (!_this4.enableMail) {
      delete _this4.ini['mailip'];
      delete _this4.ini['smtprelay'];
      delete _this4.ini['smtpuser'];
      delete _this4.ini['smtppw'];
    }
    $http.post('/api/lm/setup-wizard/update-ini', _this4.ini).then(function () {
      return $location.path('/view/lm/init/setup');
    });
  };
});

angular.module('lm.setup_wizard').controller('InitSetupController', function ($location, $http, gettext, pageTitle, notify) {
  var _this5 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.isWorking = true;
  $http.post('/api/lm/setup-wizard/provision').then(function () {
    _this5.isWorking = false;
    notify.success(gettext('Setup complete'));
  }).catch(function () {
    _this5.isWorking = true;
  });
  this.close = function () {
    $location.path('/');
  };
});

function resetColor(id) {
  document.getElementById(id).style.background = '';
  document.getElementById(id).style.borderColor = '';
}

function isStrongPwd1(password) {
  var regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/;
  var validPassword = regExp.test(password);
  return validPassword;
}


