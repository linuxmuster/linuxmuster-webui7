angular.module('lm.setup_wizard').config(function($routeProvider) {
  $routeProvider.when('/view/lm/init/welcome', {
    templateUrl: '/lm_setup_wizard:partial/init-welcome.html',
    controller: 'InitWelcomeController',
    controllerAs: '$ctrl',
  })

  $routeProvider.when('/view/lm/init/school', {
    templateUrl: '/lm_setup_wizard:partial/init-school.html',
    controller: 'InitSchoolController',
    controllerAs: '$ctrl',
  })

  $routeProvider.when('/view/lm/init/license', {
    templateUrl: '/lm_setup_wizard:partial/init-license.html',
    controller: 'InitLicenseController',
    controllerAs: '$ctrl',
  })
})


angular.module('lm.setup_wizard').controller('InitWelcomeController', function (gettext, pageTitle) {
  pageTitle.set(gettext('Setup Wizard'))
})


angular.module('lm.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}

  this.apply = () => {
    $http.post('/api/lm/setup-wizard/update-ini', this.ini).then(() => {
      return $location.path('/view/lm/init/network')
    })
  }
})


angular.module('lm.setup_wizard').controller('InitLanguageController', function($scope, $location, $interval, $http, PVShellSystem, config, identity, gettext, pageTitle, locale) {
    pageTitle.set(gettext('Setup Wizard'));

    const interval = $interval(() => $http.get('/api/lm/system/get-mac')
    , 60000);

    $scope.$on('$destroy', () => $interval.cancel(interval));

    PVShellSystem.listLanguages().then(l => $scope.languages = l);

    const languageMap = {
        'Chinese': 'zh',
        'English': 'en',
        'French': 'fr',
        'German': 'de',
        'Italian': 'it',
        'Portugese': 'pt',
        'Russian': 'ru',
        'Spanish': 'es',
        'Turkish': 'tr',
        'Polish': 'pl',
    };

    $scope.selectLanguage = l =>
        PVShellSystem.setLanguage(l).then(function() {
            $location.path('/view/lm/init/license');
            if (config.data.linuxmuster == null) { config.data.linuxmuster = {}; }
            config.data.linuxmuster.language = l;
            config.data.language = languageMap[l];
            return locale.setLanguage(languageMap[l]);
        })
    ;

    return $scope.cancel = function() {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };
});


angular.module('lm.setup_wizard').controller('InitLicenseController', function($scope, $location, $sce, $interval, $http, PVShellSystem, config, PVShellLicenseText, identity, gettext) {
    const interval = $interval(() => $http.get('/api/lm/system/get-mac')
    , 60000);

    $scope.$on('$destroy', () => $interval.cancel(interval));

    return config.promise.then(function() {
        let license = PVShellLicenseText['English'];
        if (config.data.linuxmuster.language === 'Italian') {
            license = PVShellLicenseText['Italian'];
        }

        $scope.licenseText = $sce.trustAsHtml(license);
        return $scope.cancel = function() {
            if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
                return $location.path('/view/lm/init/welcome');
            }
        };
    });
});


angular.module('lm.setup_wizard').controller('InitPasswordsController', function($scope, $location, $http, $interval, PVShellSystem, config, identity, gettext) {
    $scope.passwords = {};
    $scope.confirmations = {};

    const interval = $interval(() => $http.get('/api/lm/system/get-mac')
    , 60000);

    $scope.$on('$destroy', () => $interval.cancel(interval));

    $scope.save = function() {
        for (let u of ['user', 'maintainer']) {
            if (!$scope.passwords[u]) {
                alert(gettext(`You need to set password for the ${u}`));
                return;
            }
            if ($scope.passwords[u] !== $scope.confirmations[u]) {
                alert(gettext(`Password and confirmation don't match for the ${u}`));
                return;
            }
            if ($scope.passwords[u].length < 8) {
                alert(gettext(`Password for ${u} must be at least 8 characters long`));
                return;
            }
        }

        return $http.post("/api/auth-users/set-password/user", $scope.passwords['user']).then(() =>
            $http.post("/api/auth-users/set-password/maintainer", $scope.passwords['maintainer']).then(() =>
                config.load().then(() => $location.path('/view/lm/init/datetime'))
            )
        );
    };

    return $scope.cancel = function() {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };
});


angular.module('lm.setup_wizard').controller('InitDateTimeController', function($scope, $location, $timeout, $http, PVShellSystem, config, $interval, datetime, customization, identity, notify, gettext) {
    $scope._ = {};

    const interval = $interval(() => $http.get('/api/lm/system/get-mac')
    , 60000);

    $scope.$on('$destroy', () => $interval.cancel(interval));

    $scope.refresh = () =>
        datetime.getTimezone().then(function(data) {
            $scope._.timezone = data.tz;
            $scope.offset = data.offset;

            $scope._.time = undefined;
            return datetime.getTime().then(time => $scope._.time = new Date((time + $scope.offset) * 1000));
        })
    ;

    $scope.refresh();

    $scope.setTimezone = () =>
        datetime.setTimezone($scope._.timezone).then(() =>
            $timeout(function() {
                $scope.refresh();
                return notify.success(gettext('Timezone set'));
            }
            , 1000)).catch(e => notify.error(gettext('Failed'), e.message))
    ;

    $scope.apply = () =>
        datetime.setTime(($scope._.time.getTime() / 1000) - $scope.offset).then(() => $scope.finish())
    ;

    $scope.finish = function() {
        if (config.data.linuxmuster == null) { config.data.linuxmuster = {}; }
        config.data.linuxmuster.initialized = true;
        return config.save().then(() =>
            PVShellSystem.finishSetup($location.host() === 'localhost' ? 'local' : 'remote').then(() => $location.path('/view/lm/init/wifi'))
        );
    };

    $scope.cancel = function() {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };

    return datetime.listTimezones().then(data => $scope.timezones = data);
});


angular.module('lm.setup_wizard').controller('InitWifiController', function($scope, $location, $q, $http, $interval, PVShellSystem, config, network, identity, gettext, messagebox, notify, customization) {
    $scope._ = {};

    const interval = $interval(() => $http.get('/api/lm/system/get-mac')
    , 60000);

    $scope.$on('$destroy', () => $interval.cancel(interval));

    $scope.interfaceName = n =>
        ({
            enp2s0: 'FIELD',
            enp3s0: 'LAN',
            wlp4s0: 'WiFi',
            wlan0: 'Test WiFi'
        }[n] || n)
    ;

    config.promise.then(function() {
        if (config.data.linuxmuster.wifi == null) { config.data.linuxmuster.wifi = {}; }

        return $http.get('/api/lm/wifi/devices').success(function(data) {
            $scope.wirelessDevices = data;
            $scope.wirelessConfig = config.data.linuxmuster.wifi;
            $scope.passwordConfirmations = {};
            return Array.from($scope.wirelessDevices).map((device) =>
                (function(device) {
                    if ($scope.wirelessConfig[device] == null) { $scope.wirelessConfig[device] = {
                        ssid: identity.machine.hostname || 'pvpro-6787',
                        password: ''
                    }; }
                    $scope.wirelessConfig[device].enable = true;
                    $scope.wirelessConfig[device].enableWPA = true;
                    return $scope.passwordConfirmations[device] = $scope.wirelessConfig[device].password;
                })(device));
        });
    });

    $scope.apply = function() {
        for (var device of Array.from($scope.wirelessDevices)) {
            if ($scope.wirelessConfig[device].password.length < 8) {
                notify.warning(gettext(`Password for ${device} must be at least 8 characters long`));
                return;
            }
            if ($scope.wirelessConfig[device].password !== $scope.passwordConfirmations[device]) {
                notify.warning(gettext(`Password for ${device} does not match confirmation`));
                return;
            }
        }

        return messagebox.show({
            title: gettext('Warning'),
            text: gettext('If you are connected through WiFi, changing password will disconnect your session.'),
            positive: gettext('Continue'),
            negative: gettext('Cancel')
        }).then(function() {
            const qs = [];

            for (device of Array.from($scope.wirelessDevices)) {
                (device => qs.push($http.post(`/api/lm/wifi/${device}/setup/ap`, $scope.wirelessConfig[device])))(device);
            }

            return $q.all(qs).then(function(out) {
                notify.success(gettext('Saved'));
                // config.data.linuxmuster ?= {}
                // config.data.linuxmuster.initialized = true
                return config.save().then(() =>
                    // PVShellSystem.finishSetup().then () ->
                    $location.path(customization.plugins.core.startupURL)
                );}).catch(e => notify.error(gettext('Failed'), e.data.message));
        });
    };

    return $scope.cancel = function() {
        if (confirm(gettext('Are you sure you want to cancel the setup process?'))) {
            return $location.path('/view/lm/init/welcome');
        }
    };
});
