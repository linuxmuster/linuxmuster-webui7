'use strict';

angular.module('lm.setup_wizard', ['core']);

angular.module('lm.setup_wizard').run(function (config, $location) {
    config.promise.then(function () {
        if (!config.data.linuxmuster || !config.data.linuxmuster.initialized) {
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

    $routeProvider.when('/view/lm/init/license', {
        templateUrl: '/lm_setup_wizard:partial/init-license.html',
        controller: 'InitLicenseController',
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

angular.module('lm.setup_wizard').controller('InitLanguageController', function ($scope, $location, $interval, $http, PVShellSystem, config, identity, gettext, pageTitle, locale) {
    pageTitle.set(gettext('Setup Wizard'));

    var interval = $interval(function () {
        return $http.get('/api/lm/system/get-mac');
    }, 60000);

    $scope.$on('$destroy', function () {
        return $interval.cancel(interval);
    });

    PVShellSystem.listLanguages().then(function (l) {
        return $scope.languages = l;
    });

    var languageMap = {
        'Chinese': 'zh',
        'English': 'en',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portugese': 'pt',
        'Russian': 'ru',
        'Spanish': 'es',
        'Turkish': 'tr',
        'Polish': 'pl'
    };

    $scope.selectLanguage = function (l) {
        return PVShellSystem.setLanguage(l).then(function () {
            $location.path('/view/lm/init/license');
            if (config.data.linuxmuster == null) {
                config.data.linuxmuster = {};
            }
            config.data.linuxmuster.language = l;
            config.data.language = languageMap[l];
            return locale.setLanguage(languageMap[l]);
        });
    };

    return $scope.cancel = function () {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };
});

angular.module('lm.setup_wizard').controller('InitLicenseController', function ($scope, $location, $sce, $interval, $http, PVShellSystem, config, PVShellLicenseText, identity, gettext) {
    var interval = $interval(function () {
        return $http.get('/api/lm/system/get-mac');
    }, 60000);

    $scope.$on('$destroy', function () {
        return $interval.cancel(interval);
    });

    return config.promise.then(function () {
        var license = PVShellLicenseText['English'];
        if (config.data.linuxmuster.language === 'Italian') {
            license = PVShellLicenseText['Italian'];
        }

        $scope.licenseText = $sce.trustAsHtml(license);
        return $scope.cancel = function () {
            if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
                return $location.path('/view/lm/init/welcome');
            }
        };
    });
});

angular.module('lm.setup_wizard').controller('InitPasswordsController', function ($scope, $location, $http, $interval, PVShellSystem, config, identity, gettext) {
    $scope.passwords = {};
    $scope.confirmations = {};

    var interval = $interval(function () {
        return $http.get('/api/lm/system/get-mac');
    }, 60000);

    $scope.$on('$destroy', function () {
        return $interval.cancel(interval);
    });

    $scope.save = function () {
        var _arr = ['user', 'maintainer'];

        for (var _i = 0; _i < _arr.length; _i++) {
            var u = _arr[_i];
            if (!$scope.passwords[u]) {
                alert(gettext('You need to set password for the ' + u));
                return;
            }
            if ($scope.passwords[u] !== $scope.confirmations[u]) {
                alert(gettext('Password and confirmation don\'t match for the ' + u));
                return;
            }
            if ($scope.passwords[u].length < 8) {
                alert(gettext('Password for ' + u + ' must be at least 8 characters long'));
                return;
            }
        }

        return $http.post("/api/auth-users/set-password/user", $scope.passwords['user']).then(function () {
            return $http.post("/api/auth-users/set-password/maintainer", $scope.passwords['maintainer']).then(function () {
                return config.load().then(function () {
                    return $location.path('/view/lm/init/datetime');
                });
            });
        });
    };

    return $scope.cancel = function () {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };
});

angular.module('lm.setup_wizard').controller('InitDateTimeController', function ($scope, $location, $timeout, $http, PVShellSystem, config, $interval, datetime, customization, identity, notify, gettext) {
    $scope._ = {};

    var interval = $interval(function () {
        return $http.get('/api/lm/system/get-mac');
    }, 60000);

    $scope.$on('$destroy', function () {
        return $interval.cancel(interval);
    });

    $scope.refresh = function () {
        return datetime.getTimezone().then(function (data) {
            $scope._.timezone = data.tz;
            $scope.offset = data.offset;

            $scope._.time = undefined;
            return datetime.getTime().then(function (time) {
                return $scope._.time = new Date((time + $scope.offset) * 1000);
            });
        });
    };

    $scope.refresh();

    $scope.setTimezone = function () {
        return datetime.setTimezone($scope._.timezone).then(function () {
            return $timeout(function () {
                $scope.refresh();
                return notify.success(gettext('Timezone set'));
            }, 1000);
        }).catch(function (e) {
            return notify.error(gettext('Failed'), e.message);
        });
    };

    $scope.apply = function () {
        return datetime.setTime($scope._.time.getTime() / 1000 - $scope.offset).then(function () {
            return $scope.finish();
        });
    };

    $scope.finish = function () {
        if (config.data.linuxmuster == null) {
            config.data.linuxmuster = {};
        }
        config.data.linuxmuster.initialized = true;
        return config.save().then(function () {
            return PVShellSystem.finishSetup($location.host() === 'localhost' ? 'local' : 'remote').then(function () {
                return $location.path('/view/lm/init/wifi');
            });
        });
    };

    $scope.cancel = function () {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };

    return datetime.listTimezones().then(function (data) {
        return $scope.timezones = data;
    });
});

angular.module('lm.setup_wizard').controller('InitWifiController', function ($scope, $location, $q, $http, $interval, PVShellSystem, config, network, identity, gettext, messagebox, notify, customization) {
    $scope._ = {};

    var interval = $interval(function () {
        return $http.get('/api/lm/system/get-mac');
    }, 60000);

    $scope.$on('$destroy', function () {
        return $interval.cancel(interval);
    });

    $scope.interfaceName = function (n) {
        return {
            enp2s0: 'FIELD',
            enp3s0: 'LAN',
            wlp4s0: 'WiFi',
            wlan0: 'Test WiFi'
        }[n] || n;
    };

    config.promise.then(function () {
        if (config.data.linuxmuster.wifi == null) {
            config.data.linuxmuster.wifi = {};
        }

        return $http.get('/api/lm/wifi/devices').success(function (data) {
            $scope.wirelessDevices = data;
            $scope.wirelessConfig = config.data.linuxmuster.wifi;
            $scope.passwordConfirmations = {};
            return Array.from($scope.wirelessDevices).map(function (device) {
                return function (device) {
                    if ($scope.wirelessConfig[device] == null) {
                        $scope.wirelessConfig[device] = {
                            ssid: identity.machine.hostname || 'pvpro-6787',
                            password: ''
                        };
                    }
                    $scope.wirelessConfig[device].enable = true;
                    $scope.wirelessConfig[device].enableWPA = true;
                    return $scope.passwordConfirmations[device] = $scope.wirelessConfig[device].password;
                }(device);
            });
        });
    });

    $scope.apply = function () {
        var _iteratorNormalCompletion = true;
        var _didIteratorError = false;
        var _iteratorError = undefined;

        try {
            for (var _iterator = Array.from($scope.wirelessDevices)[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                var device = _step.value;

                if ($scope.wirelessConfig[device].password.length < 8) {
                    notify.warning(gettext('Password for ' + device + ' must be at least 8 characters long'));
                    return;
                }
                if ($scope.wirelessConfig[device].password !== $scope.passwordConfirmations[device]) {
                    notify.warning(gettext('Password for ' + device + ' does not match confirmation'));
                    return;
                }
            }
        } catch (err) {
            _didIteratorError = true;
            _iteratorError = err;
        } finally {
            try {
                if (!_iteratorNormalCompletion && _iterator.return) {
                    _iterator.return();
                }
            } finally {
                if (_didIteratorError) {
                    throw _iteratorError;
                }
            }
        }

        return messagebox.show({
            title: gettext('Warning'),
            text: gettext('If you are connected through WiFi, changing password will disconnect your session.'),
            positive: gettext('Continue'),
            negative: gettext('Cancel')
        }).then(function () {
            var qs = [];

            var _iteratorNormalCompletion2 = true;
            var _didIteratorError2 = false;
            var _iteratorError2 = undefined;

            try {
                for (var _iterator2 = Array.from($scope.wirelessDevices)[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                    device = _step2.value;

                    (function (device) {
                        return qs.push($http.post('/api/lm/wifi/' + device + '/setup/ap', $scope.wirelessConfig[device]));
                    })(device);
                }
            } catch (err) {
                _didIteratorError2 = true;
                _iteratorError2 = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion2 && _iterator2.return) {
                        _iterator2.return();
                    }
                } finally {
                    if (_didIteratorError2) {
                        throw _iteratorError2;
                    }
                }
            }

            return $q.all(qs).then(function (out) {
                notify.success(gettext('Saved'));
                // config.data.linuxmuster ?= {}
                // config.data.linuxmuster.initialized = true
                return config.save().then(function () {
                    return (
                        // PVShellSystem.finishSetup().then () ->
                        $location.path(customization.plugins.core.startupURL)
                    );
                });
            }).catch(function (e) {
                return notify.error(gettext('Failed'), e.data.message);
            });
        });
    };

    return $scope.cancel = function () {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };
});