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

angular.module('lm.setup_wizard').controller('InitNetworkController', function ($location, $http, gettext, pageTitle) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}

  this.apply = () => {
    $http.post('/api/lm/setup-wizard/update-ini', this.ini).then(() => {
      return $location.path('/view/lm/init/passwords')
    })
  }
})

angular.module('lm.setup_wizard').controller('InitPasswordsController', function ($location, $http, gettext, pageTitle) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}

  this.apply = () => {
    $http.post('/api/lm/setup-wizard/update-ini', this.ini).then(() => {
      return $location.path('/view/lm/init/setup')
    })
  }
})
