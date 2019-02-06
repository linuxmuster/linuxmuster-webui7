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

  $routeProvider.when('/view/lm/init/account', {
    templateUrl: '/lm_setup_wizard:partial/init-account.html',
    controller: 'InitAccountController',
    controllerAs: '$ctrl',
  })

  $routeProvider.when('/view/lm/init/externalservices', {
    templateUrl: '/lm_setup_wizard:partial/init-externalServices.html',
    controller: 'InitExternalServicesController',
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
  console.log ("test")
  console.log (config)
  $http.get('/api/core/languages').then(response => this.languages = response.data)

  this.apply = async () => {
    await this.config.save()
    $location.path('/view/lm/init/account')
  }
})


angular.module('lm.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle, notify) {
  pageTitle.set(gettext('Setup Wizard'))
  $http.get('/api/core/languages').then(response => this.languages = response.data)
  this.ini = {}
  this.apply = async () => {
    $dataMissing=false

    var fields=["schoolname", "servername", "domainname"]

    for (var i=0; i < fields.length; i++){
      var field=fields[i]
      if (this.ini[field] == null || this.ini[field] == '') {
        document.getElementById(field+'-input').style.background = 'rgba(255, 178, 178, 0.29)'
        document.getElementById(field+'-input').style.borderColor = 'red'
        $dataMissing=true
      }
      else {
        document.getElementById(field+'-input').style.background = ''
        document.getElementById(field+'-input').style.borderColor = ''
      }

    }

    if ($dataMissing == true){
      notify.error('Required data missing')
      return
    }
    await $http.post('/api/lm/setup-wizard/update-ini', this.ini)
      $location.path('/view/lm/init/account')
  }
})



angular.module('lm.setup_wizard').controller('InitAccountController', function ($scope, $location, $http, gettext, pageTitle, notify) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}
  this.apply = () => {
    if (this.ini.adminpw != this.adminpwConfirmation) {
      notify.error('Administrator password missmatch')
      return
    }
    if (!validCharPwd(this.ini.adminpw)){
      notify.error('Password contains invalid characters')
      return
    }
    if (!isStrongPwd(this.ini.adminpw)){
      notify.error('Password too weak')
      return
    }
    $http.post('/api/lm/setup-wizard/update-ini', this.ini).then(() => {
      return $location.path('/view/lm/init/externalservices')
    })
  }
})

angular.module('lm.setup_wizard').controller('InitExternalServicesController', function ($location, $http, gettext, pageTitle, notify) {
  pageTitle.set(gettext('Setup Wizard'))
  this.ini = {}

  this.finish = () => {
    if (this.ini.smtppw != this.smtppwConfirmation) {
      notify.error('SMTP password missmatch')
      return
    }
    if (!this.enableOPSI) {
      delete this.ini['opsiip']
    }
    if (!this.enableDOCKER) {
      delete this.ini['dockerip']
    }
    if (!this.enableMail) {
      delete this.ini['mailip']
      delete this.ini['smtprelay']
      delete this.ini['smtpuser']
      delete this.ini['smtppw']
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
    notify.success(gettext('Restart Webui'))
    $http.post('/api/lm/setup-wizard/restart').then(() => {
        $location.path('/')
    })
  }
})

function resetColor(id){
        document.getElementById(id).style.background = ''
        document.getElementById(id).style.borderColor = ''
}

function validCharPwd(password) {
    console.log ("check valids");
        var regExp = /^[a-zA-Z 0-9 !@#§+\-$%&*{}()\]\[]+$/
        var validPassword = regExp.test(password);
        return validPassword;
}

function isStrongPwd(password) {
        console.log ("check strength");
        var regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#§+\-$%&*{}()\]\[]|(?=.*\d)).{7,}/;
        var validPassword = regExp.test(password);
        return validPassword;
}
