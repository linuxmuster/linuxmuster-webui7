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

angular.module('lm.setup_wizard').controller('InitWelcomeController', function (gettext, pageTitle, $http, config) {
  var _this = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.config = config;
  $http.get('/api/core/languages').then(function (response) {
    return _this.languages = response.data;
  });

  this.apply = async function () {
    await _this.config.save();
    $location.path('/view/lm/init/network');
  };
});

angular.module('lm.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle) {
  var _this2 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};

  this.apply = async function () {
    await $http.post('/api/lm/setup-wizard/update-ini', _this2.ini);
    $location.path('/view/lm/init/network');
  };
});

angular.module('lm.setup_wizard').controller('InitNetworkController', function ($location, $http, gettext, pageTitle, network) {
  var _this3 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};
  this.interfaces = [];

  network.getConfig().then(function (interfaces) {
    _this3.interfaces = interfaces.map(function (x) {
      return x.name;
    });
  });

  this.apply = function () {
    $http.post('/api/lm/setup-wizard/update-ini', _this3.ini).then(function () {
      return $location.path('/view/lm/init/passwords');
    });
  };
});

angular.module('lm.setup_wizard').controller('InitPasswordsController', function ($location, $http, gettext, pageTitle, notify) {
  var _this4 = this;

  pageTitle.set(gettext('Setup Wizard'));
  this.ini = {};

  this.finish = function () {
    if (_this4.ini.adminpw != _this4.adminpwConfirmation) {
      notify.error('Password do not match');
      return;
    }
    if (!_this4.enableOPSI) {
      delete _this4.ini['opsiip'];
    }
    if (!_this4.enableFirewall) {
      delete _this4.ini['firewallip'];
      delete _this4.ini['firewallpw'];
    }
    if (!_this4.enableSMTPRelay) {
      delete _this4.ini['smtprelay'];
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


