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

  $routeProvider.when('/view/lm/init/network', {
    templateUrl: '/lm_setup_wizard:partial/init-network.html',
    controller: 'InitNetworkController',
    controllerAs: '$ctrl',
  })

  $routeProvider.when('/view/lm/init/passwords', {
    templateUrl: '/lm_setup_wizard:partial/init-passwords.html',
    controller: 'InitPasswordsController',
    controllerAs: '$ctrl',
  })

  $routeProvider.when('/view/lm/init/setup', {
    templateUrl: '/lm_setup_wizard:partial/init-setup.html',
    controller: 'InitSetupController',
    controllerAs: '$ctrl',
  })
})


angular.module('lm.setup_wizard').controller('InitWelcomeController', function (gettext, pageTitle, $http, config) {
  pageTitle.set(gettext('Setup Wizard'))
  this.config = config
  $http.get('/api/core/languages').then(response => this.languages = response.data)

  this.apply = async () => {
    await this.config.save()
    $location.path('/view/lm/init/network')
  }
})


angular.module('lm.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}

  this.apply = async () => {
    await $http.post('/api/lm/setup-wizard/update-ini', this.ini)
    $location.path('/view/lm/init/network')
  }
})

angular.module('lm.setup_wizard').controller('InitNetworkController', function ($location, $http, gettext, pageTitle, network) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}
  this.interfaces = []

  network.getConfig().then(interfaces => {
    this.interfaces = interfaces.map(x => x.name)
  })

  this.apply = () => {
    $http.post('/api/lm/setup-wizard/update-ini', this.ini).then(() => {
      return $location.path('/view/lm/init/passwords')
    })
  }
})

angular.module('lm.setup_wizard').controller('InitPasswordsController', function ($location, $http, gettext, pageTitle, notify) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}

  this.finish = () => {
    if (this.ini.adminpw != this.adminpwConfirmation) {
      notify.error('Administrator password missmatch')
      return
    }
    if (this.ini.firewallpw != this.firewallpwConfirmation) {
      notify.error('Firewall password missmatch')
      return
    }
    if (!this.enableOPSI) {
      delete this.ini['opsiip']
    }
    if (!this.enableFirewall) {
      delete this.ini['firewallip']
      delete this.ini['firewallpw']
    }
    if (!this.enableSMTPRelay) {
      delete this.ini['smtprelay']
    }
    $http.post('/api/lm/setup-wizard/update-ini', this.ini).then(() => {
      return $location.path('/view/lm/init/setup')
    })
  }
})

angular.module('lm.setup_wizard').controller('InitSetupController', function ($location, $http, gettext, pageTitle, notify) {
  pageTitle.set(gettext('Setup Wizard'))
  this.isWorking = true
  $http.post('/api/lm/setup-wizard/provision').then(() => {
    this.isWorking = false
    notify.success(gettext('Setup complete'))
  }).catch(() => {
    this.isWorking = true
  })
  this.close = () => {
    $location.path('/')
  }
})
