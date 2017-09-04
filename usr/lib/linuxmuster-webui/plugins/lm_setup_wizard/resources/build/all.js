'use strict';

angular.module('lm.setup_wizard', ['core']);

angular.module('lm.setup_wizard').run(function (config, $location, identity) {
    identity.promise.then(function () {
        return config.promise;
    }).then(function () {
        if (identity.user && (!config.data.linuxmuster || !config.data.linuxmuster.initialized)) {
            return $location.path('/view/lm/init/welcome');
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

  $routeProvider.when('/view/lm/init/network', {
    templateUrl: '/lm_setup_wizard:partial/init-network.html',
    controller: 'InitNetworkController',
    controllerAs: '$ctrl'
  });

  $routeProvider.when('/view/lm/init/passwords', {
    templateUrl: '/lm_setup_wizard:partial/init-passwords.html',
    controller: 'InitPasswordsController',
    controllerAs: '$ctrl'
  });

  $routeProvider.when('/view/lm/init/setup', {
    templateUrl: '/lm_setup_wizard:partial/init-setup.html',
    controller: 'InitSetupController',
    controllerAs: '$ctrl'
  });
});

angular.module('lm.setup_wizard').controller('InitWelcomeController', function (gettext, pageTitle) {
  pageTitle.set(gettext('Setup Wizard'));
});

angular.module('lm.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle) {
  var _this = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};

  this.apply = function () {
    $http.post('/api/lm/setup-wizard/update-ini', _this.ini).then(function () {
      return $location.path('/view/lm/init/network');
    });
  };
});

angular.module('lm.setup_wizard').controller('InitNetworkController', function ($location, $http, gettext, pageTitle) {
  var _this2 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};

  this.apply = function () {
    $http.post('/api/lm/setup-wizard/update-ini', _this2.ini).then(function () {
      return $location.path('/view/lm/init/passwords');
    });
  };
});

angular.module('lm.setup_wizard').controller('InitPasswordsController', function ($location, $http, gettext, pageTitle, notify) {
  var _this3 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};

  this.finish = function () {
    if (_this3.ini.adminpw != _this3.adminpwConfirmation) {
      notify.error('Password do not match');
      return;
    }
    if (!_this3.enableOPSI) {
      delete _this3.ini['opsiip'];
    }
    if (!_this3.enableFirewall) {
      delete _this3.ini['firewallip'];
      delete _this3.ini['firewallpw'];
    }
    if (!_this3.enableSMTPRelay) {
      delete _this3.ini['smtprelay'];
    }
    $http.post('/api/lm/setup-wizard/update-ini', _this3.ini).then(function () {
      return $location.path('/view/lm/init/setup');
    });
  };
});

angular.module('lm.setup_wizard').controller('InitSetupController', function ($location, $http, gettext, pageTitle, notify) {
  var _this4 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.isWorking = true;
  $http.post('/api/lm/setup-wizard/provision').then(function () {
    _this4.isWorking = false;
    notify.success(gettext('Setup complete'));
  }).catch(function () {
    _this4.isWorking = true;
  });
  this.close = function () {
    $location.path('/');
  };
});