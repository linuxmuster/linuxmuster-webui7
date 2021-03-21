'use strict';

angular.module('lmn.setup_wizard', ['core']);

angular.module('lmn.setup_wizard').run(function ($http, $location, identity) {
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

angular.module('lmn.setup_wizard').config(function ($routeProvider) {
    $routeProvider.when('/view/lm/init/welcome', {
        templateUrl: '/lmn_setup_wizard:partial/init-welcome.html',
        controller: 'InitWelcomeController',
        controllerAs: '$ctrl'
    });

    $routeProvider.when('/view/lm/init/school', {
        templateUrl: '/lmn_setup_wizard:partial/init-school.html',
        controller: 'InitSchoolController',
        controllerAs: '$ctrl'
    });

    $routeProvider.when('/view/lm/init/account', {
        templateUrl: '/lmn_setup_wizard:partial/init-account.html',
        controller: 'InitAccountController',
        controllerAs: '$ctrl'
    });

    $routeProvider.when('/view/lm/init/externalservices', {
        templateUrl: '/lmn_setup_wizard:partial/init-externalServices.html',
        controller: 'InitExternalServicesController',
        controllerAs: '$ctrl'
    });

    $routeProvider.when('/view/lm/init/summary', {
        templateUrl: '/lmn_setup_wizard:partial/init-summary.html',
        controller: 'InitSummaryController',
        controllerAs: '$ctrl'
    });

    $routeProvider.when('/view/lm/init/done', {
        templateUrl: '/lmn_setup_wizard:partial/init-done.html',
        controller: 'InitDoneController',
        controllerAs: '$ctrl'
    });

    $routeProvider.when('/view/lm/init/setup', {
        templateUrl: '/lmn_setup_wizard:partial/init-setup.html',
        controller: 'InitSetupController',
        controllerAs: '$ctrl'
    });
});

angular.module('lmn.setup_wizard').controller('InitWelcomeController', function (gettext, pageTitle, $http, $route, locale, config, $location, notify) {
    var _this = this;

    pageTitle.set(gettext('Setup Wizard'));
    this.config = config;
    console.log(config);
    $http.get('/api/core/languages').then(function (response) {
        return _this.languages = response.data;
    });

    this.updateLanguage = function () {
        locale.setLanguage(_this.config.data.language);
        $route.reload();
    };

    this.apply = async function () {
        if (!_this.licenseAccepted) {
            notify.error('Please accept the license !');
            return;
        }
        await _this.config.save();
        $location.path('/view/lm/init/school');
    };
});

angular.module('lmn.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle, notify) {
    var _this2 = this;

    pageTitle.set(gettext('Setup Wizard'));
    $http.get('/api/core/languages').then(function (response) {
        return _this2.languages = response.data;
    });

    $http.get('/api/lm/setup-wizard/read-ini').then(function (response) {
        return _this2.ini = response.data;
    });

    // fields to validate
    // define property values so they are not null
    this.ini = { schoolname: "", domainname: "", servername: ""
        // list of fields which need validation
    };var fields = ["schoolname", "domainname", "servername"];

    this.apply = async function () {
        $dataMissing = false;
        $badCharacters = false;

        // var fields=["schoolname", "servername", "domainname"]

        for (var i = 0; i < fields.length; i++) {
            var field = fields[i];
            console.log($dataMissing);
            console.log($badCharacters);
            console.log(_this2.ini[field]);
            console.log(_this2);
            if (_this2.ini[field] == '') {
                document.getElementById(field + '-input').style.background = 'rgba(255, 178, 178, 0.29)';
                document.getElementById(field + '-input').style.borderColor = 'red';
                $dataMissing = true;
            } else {
                // in this case null means it does not fit the pattenr defined in html
                if (_this2.ini[field] == null) {
                    document.getElementById(field + '-input').style.background = 'rgba(255, 178, 178, 0.29)';
                    document.getElementById(field + '-input').style.borderColor = 'red';
                    $badCharacters = true;
                } else {
                    document.getElementById(field + '-input').style.background = '';
                    document.getElementById(field + '-input').style.borderColor = '';
                }
            }
        }

        if ($dataMissing == true) {
            notify.error('Required data missing');
            return;
        }
        if ($badCharacters == true) {
            notify.error('Malformed input');
            return;
        }

        await $http.post('/api/lm/setup-wizard/update-ini', _this2.ini);
        $location.path('/view/lm/init/account');
    };
});

angular.module('lmn.setup_wizard').controller('InitAccountController', function ($scope, $location, $http, gettext, pageTitle, notify) {
    var _this3 = this;

    pageTitle.set(gettext('Setup Wizard'));
    this.ini = {};
    this.apply = function () {
        if (_this3.ini.adminpw != _this3.adminpwConfirmation) {
            notify.error('Administrator password missmatch');
            return;
        }
        if (!validCharPwd(_this3.ini.adminpw)) {
            notify.error('Password contains invalid characters');
            return;
        }
        if (!isStrongPwd(_this3.ini.adminpw)) {
            notify.error('Password too weak');
            return;
        }
        $http.post('/api/lm/setup-wizard/update-ini', _this3.ini).then(function () {
            return $location.path('/view/lm/init/externalservices');
        });
    };
});

angular.module('lmn.setup_wizard').controller('InitExternalServicesController', function ($location, $http, gettext, pageTitle, notify) {
    var _this4 = this;

    pageTitle.set(gettext('Setup Wizard'));
    this.ini = {};
    $http.get('/api/lm/setup-wizard/read-ini').then(function (response) {
        return _this4.ini = response.data;
    });

    this.apply = function () {
        console.log(_this4.enableOPSI);

        if (!_this4.enableOPSI) {
            _this4.ini['opsiip'] = 'null';
        }
        if (!_this4.enableDOCKER) {
            _this4.ini['dockerip'] = 'null';
        }
        if (!_this4.enableMail) {
            _this4.ini['mailip'] = 'null';
            _this4.ini['smtprelay'] = 'null';
            _this4.ini['smtpuser'] = 'null';
            _this4.ini['smtppw'] = 'null';
        }

        if (_this4.enableMail) {

            if (_this4.ini.smtppw != _this4.smtppwConfirmation) {
                notify.error('SMTP password missmatch');
                return;
            }
        }
        $http.post('/api/lm/setup-wizard/update-ini', _this4.ini).then(function () {
            return $location.path('/view/lm/init/summary');
        });
    };
});

angular.module('lmn.setup_wizard').controller('InitSummaryController', function ($location, $http, gettext, pageTitle, notify) {
    var _this5 = this;

    pageTitle.set(gettext('Setup Wizard'));
    this.ini = {};
    this.checks = {};
    this.checked = false;
    this.ok = false;
    $http.get('/api/lm/setup-wizard/read-ini').then(function (response) {
        return _this5.ini = response.data;
    });

    this.check = function () {
        notify.info(gettext("Checks launched, this may take some time"));
        $http.post('/api/lm/setup-wizard/check-data', { setup: _this5.ini }).then(function (response) {
            _this5.checks = response.data;
            console.log(_this5.checks);
            _this5.checked = true;
            _this5.ok = _this5.checks.bool;
            if (!_this5.ok) {
                notify.error(gettext("Please verify the data again"));
            }
        });
    };
    this.finish = function () {
        $http.post('/api/lm/setup-wizard/update-ini', _this5.ini).then(function () {
            return $location.path('/view/lm/init/setup');
        });
    };
});

angular.module('lmn.setup_wizard').controller('InitSetupController', function ($location, $http, gettext, pageTitle, notify) {
    var _this6 = this;

    pageTitle.set(gettext('Setup Wizard'));
    this.isWorking = true;
    $http.post('/api/lm/setup-wizard/provision', { start: 'setup' }).then(function () {
        _this6.isWorking = false;
        notify.success(gettext('Setup complete'));
    }).catch(function () {
        _this6.isWorking = true;
    });
    this.finish = function () {
        return $location.path('/view/lm/init/done');
    };
});

angular.module('lmn.setup_wizard').controller('InitDoneController', function ($window, $http, gettext, pageTitle, core, notify, $timeout, messagebox) {
    var _this7 = this;

    pageTitle.set(gettext('Setup Done'));

    $http.get('/api/lm/read-config-setup').then(function (resp) {
        oldUrl = new URL(window.location.href); // TODO Fix port with ajenti new config
        servername = resp.data['setup']['servername'] ? resp.data['setup']['servername'] : resp.data['setup']['hostname'];
        //url = 'https://' + servername + '.' + resp.data['setup']['domainname'] + ':' + oldUrl.port // TODO Fix port with ajenti new config
        // Use host ip instead of domain name 
        hostip = resp.data['setup']['hostip'] ? resp.data['setup']['hostip'] : '10.0.0.1';
        url = 'https://' + hostip + ':' + oldUrl.port; // TODO Fix port with ajenti new config
    });

    this.redirect = function () {
        $window.location.href = url;
    };

    this.restartUI = function () {
        var msg = messagebox.show({ progress: true, title: gettext('Restarting') });
        return $http.get('/api/core/restart-master').then(function () {
            return $timeout(function () {
                msg.close();
                messagebox.show({ title: gettext('Restarted'), text: gettext('Please wait') });
                $timeout(function () {
                    _this7.redirect();
                    return setTimeout(function () {
                        return _this7.redirect();
                    }, 5000);
                });
            }, 5000);
        }).catch(function (err) {
            msg.close();
            notify.error(gettext('Could not restart'), err.message);
            return $q.reject(err);
        });
    };

    this.close = function () {
        _this7.restartUI();
    };
});

function resetColor(id) {
    document.getElementById(id).style.background = '';
    document.getElementById(id).style.borderColor = '';
}

function validCharPwd(password) {
    var regExp = /^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$/;
    var validPassword = regExp.test(password);
    return validPassword;
}

function isStrongPwd(password) {
    console.log("check strength");
    var regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#§+\-$%&*{}()\]\[]|(?=.*\d)).{7,}/;
    var validPassword = regExp.test(password);
    return validPassword;
}


