angular.module('lmn.setup_wizard').config(function($routeProvider) {
    $routeProvider.when('/view/lmn/init/welcome', {
        templateUrl: '/lmn_setup_wizard:partial/init-welcome.html',
        controller: 'InitWelcomeController',
        controllerAs: '$ctrl',
    })

    $routeProvider.when('/view/lmn/init/school', {
        templateUrl: '/lmn_setup_wizard:partial/init-school.html',
        controller: 'InitSchoolController',
        controllerAs: '$ctrl',
    })

    $routeProvider.when('/view/lmn/init/account', {
        templateUrl: '/lmn_setup_wizard:partial/init-account.html',
        controller: 'InitAccountController',
        controllerAs: '$ctrl',
    })

    $routeProvider.when('/view/lmn/init/externalservices', {
        templateUrl: '/lmn_setup_wizard:partial/init-externalServices.html',
        controller: 'InitExternalServicesController',
        controllerAs: '$ctrl',
    })

    $routeProvider.when('/view/lmn/init/summary', {
        templateUrl: '/lmn_setup_wizard:partial/init-summary.html',
        controller: 'InitSummaryController',
        controllerAs: '$ctrl',
    })

    $routeProvider.when('/view/lmn/init/done', {
        templateUrl: '/lmn_setup_wizard:partial/init-done.html',
        controller: 'InitDoneController',
        controllerAs: '$ctrl',
    })

    $routeProvider.when('/view/lmn/init/setup', {
        templateUrl: '/lmn_setup_wizard:partial/init-setup.html',
        controller: 'InitSetupController',
        controllerAs: '$ctrl',
    })
})


angular.module('lmn.setup_wizard').controller('InitWelcomeController', function (gettext, pageTitle, $http, $route, locale, config, $location, notify) {
    pageTitle.set(gettext('Setup Wizard'))
    this.config = config
    console.log (config)
    $http.get('/api/core/languages').then(response => this.languages = response.data)

    this.updateLanguage = () => {
        locale.setLanguage(this.config.data.language);
        $route.reload();
    }

    this.apply = async () => {
        if (!this.licenseAccepted) {
            notify.error('Please accept the license !')
            return
        }
        await this.config.save()
        $location.path('/view/lmn/init/school')
    }
})



angular.module('lmn.setup_wizard').controller('InitSchoolController', function ($location, $http, gettext, pageTitle, notify) {
    pageTitle.set(gettext('Setup Wizard'))
    $http.get('/api/core/languages').then(response => this.languages = response.data)

    $http.get('/api/lmn/setup-wizard/setup').then(response => this.ini = response.data)

    // fields to validate
    // define property values so they are not null
    this.ini = {schoolname: "", domainname: "", servername: ""}
    // list of fields which need validation
    var fields=["schoolname", "domainname", "servername"]

    this.apply = async () => {
        $dataMissing=false
        $badCharacters=false

        // var fields=["schoolname", "servername", "domainname"]

        for (var i=0; i < fields.length; i++){
            var field=fields[i]
            console.log ($dataMissing)
            console.log ($badCharacters)
            console.log (this.ini[field])
            console.log (this)
            if (this.ini[field] == '') {
                document.getElementById(field+'-input').style.background = 'rgba(255, 178, 178, 0.29)'
                document.getElementById(field+'-input').style.borderColor = 'red'
                $dataMissing=true
            }
            else {
                // in this case null means it does not fit the pattenr defined in html
                if (this.ini[field] == null) {
                    document.getElementById(field+'-input').style.background = 'rgba(255, 178, 178, 0.29)'
                    document.getElementById(field+'-input').style.borderColor = 'red'
                    $badCharacters=true
                }
                else {
                    document.getElementById(field+'-input').style.background = ''
                    document.getElementById(field+'-input').style.borderColor = ''
                }
            }

        }

        if ($dataMissing == true){
            notify.error('Required data missing')
            return
        }
        if ($badCharacters == true){
            notify.error('Malformed input')
            return
        }


        await $http.post('/api/lmn/setup-wizard/setup', this.ini)
        $location.path('/view/lmn/init/account')
    }
})



angular.module('lmn.setup_wizard').controller('InitAccountController', function ($scope, $location, $http, gettext, pageTitle, notify) {
    pageTitle.set(gettext('Setup Wizard'))
    this.ini = {}

    this.samePW = () => {
        return this.ini.adminpw == this.adminpwConfirmation
    }

    this.validPW = () => {
        return validCharPwd(this.ini.adminpw)
    }

    this.strongPW = () => {
        return isStrongPwd(this.ini.adminpw)
    }

    this.checkPW = () => {
        return this.validPW() && this.strongPW() && this.samePW()
    }

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
        $http.post('/api/lmn/setup-wizard/setup', this.ini).then(() => {
            return $location.path('/view/lmn/init/externalservices')
        })
    }
})

angular.module('lmn.setup_wizard').controller('InitExternalServicesController', function ($location, $http, gettext, pageTitle, notify) {
    pageTitle.set(gettext('Setup Wizard'))
    this.ini = {}
    $http.get('/api/lmn/setup-wizard/setup').then(response => this.ini = response.data)

    this.apply= () => {
        console.log(this.enableOPSI)

        if (!this.enableOPSI) {
            this.ini['opsiip'] = 'null'
        }
        if (!this.enableDOCKER) {
            this.ini['dockerip'] = 'null'
        }
        if (!this.enableMail) {
            this.ini['mailip'] = 'null'
            this.ini['smtprelay'] = 'null'
            this.ini['smtpuser'] = 'null'
            this.ini['smtppw'] = 'null'
        }

        if (this.enableMail){

        if (this.ini.smtppw != this.smtppwConfirmation) {
            notify.error('SMTP password missmatch')
            return
        }
        }
        $http.post('/api/lmn/setup-wizard/setup', this.ini).then(() => {
            return $location.path('/view/lmn/init/summary')
        })

    }
})

angular.module('lmn.setup_wizard').controller('InitSummaryController', function ($location, $http, gettext, pageTitle, notify) {
    pageTitle.set(gettext('Setup Wizard'))
    this.ini = {}
    $http.get('/api/lmn/setup-wizard/setup').then(response => this.ini = response.data)

    this.finish= () => {
        $http.post('/api/lmn/setup-wizard/setup', this.ini).then(() => {
            return $location.path('/view/lmn/init/setup')
        })
    }
})

angular.module('lmn.setup_wizard').controller('InitSetupController', function ($location, $http, gettext, pageTitle, notify) {
    pageTitle.set(gettext('Setup Wizard'))
    this.isWorking = true
    $http.post('/api/lmn/setup-wizard/provision', {start: 'setup'}).then(() => {
        this.isWorking = false
        notify.success(gettext('Setup complete'))
    }).catch(() => {
        this.isWorking = true
    })
    this.finish = () => {
        return $location.path('/view/lmn/init/done')

    }
})

angular.module('lmn.setup_wizard').controller('InitDoneController', function ($window, $http, gettext, pageTitle, core, notify, $timeout, messageboxi, $q) {
    pageTitle.set(gettext('Setup Done'))

    $http.get('/api/lmn/read-config-setup').then( (resp) => {
        oldUrl = new URL(window.location.href) // TODO Fix port with ajenti new config
        servername = (resp.data['setup']['servername']) ? resp.data['setup']['servername'] : resp.data['setup']['hostname']
        //url = 'https://' + servername + '.' + resp.data['setup']['domainname'] + ':' + oldUrl.port // TODO Fix port with ajenti new config
        // Use host ip instead of domain name 
        hostip = (resp.data['setup']['hostip']) ? resp.data['setup']['hostip'] : '10.0.0.1'
        url = 'https://' + hostip + ':' + oldUrl.port // TODO Fix port with ajenti new config
        }
    )

    this.redirect = () => {
        $window.location.href = url
    }

    this.restartUI = () => {
        let msg = messagebox.show({progress: true, title: gettext('Restarting')});
        return $http.post('/api/core/restart-master').then(() => {
            return $timeout(() => {
                msg.close();
                messagebox.show({title: gettext('Restarted'), text: gettext('Please wait')});
                $timeout(() => {
                    this.redirect();
                    return setTimeout(() => {
                        return this.redirect();
                    }, 5000);
                });
            }, 5000);
        }).catch((err) => {
            msg.close();
            notify.error(gettext('Could not restart'), err.message);
            return $q.reject(err);
        });
    };

    this.close = () => {
        this.restartUI()
    }
})

function resetColor(id){
    document.getElementById(id).style.background = ''
    document.getElementById(id).style.borderColor = ''
}

function validCharPwd(password) {
    var regExp = /^[a-zA-Z0-9!@#§+\-%&*{}()\]\[]+$/
    var validPassword = regExp.test(password);
    return validPassword;
}

function isStrongPwd(password) {
    // console.log ("check strength");
    var regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#§+\-%&*{}()\]\[]|(?=.*\d)).{7,}/;
    var validPassword = regExp.test(password);
    return validPassword;
}
