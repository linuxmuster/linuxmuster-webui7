angular.module('lmn.settings').controller('LMglobalSettingsController', ($scope, $http, $sce, notify, pageTitle, identity, messagebox, config, core, locale, gettext) => {
    pageTitle.set(gettext('Global Settings'));

    config.load();
    $scope.config = config;

    $scope.newClientCertificate = {
        c: 'NA',
        st: 'NA',
        o: '',
        cn: ''
    };

    $scope.getSmtpConfig = () => {
        config.getSmtpConfig().then((smtpConfig) => $scope.smtp_config = smtpConfig);
    };

    identity.promise.then(() => {
       // $scope.newClientCertificate.o = identity.machine.name;
       // passwd.list().then((data) => {
       //    $scope.availableUsers = data;
       //    $scope.$watch('newClientCertificate.user', () => $scope.newClientCertificate.cn = `${identity.user}@${identity.machine.hostname}`);
       //    $scope.newClientCertificate.user = 'root';
       // });
       $http.get('/api/core/languages').then(rq => $scope.languages = rq.data);
    });


    $scope.$watch('config.data.language', () => {
       if (config.data) {
          locale.setLanguage(config.data.language);
       }
    });

    $scope.save = () =>
        config.save().then(data =>
            notify.success(gettext('Global config saved'))
        ).catch(() =>
            notify.error(gettext('Could not save global config')));

        // config.setSmtpConfig($scope.smtp_config).then(data =>
        //     notify.success(gettext('Smtp config saved'))
        // ).catch(() =>
        //     notify.error(gettext('Could not save smtp config')));


    $scope.createNewServerCertificate = () =>
       messagebox.show({
          title: gettext('Self-signed certificate'),
          text: gettext('Generating a new certificate will void all existing client authentication certificates!'),
          positive: gettext('Generate'),
          negative: gettext('Cancel')
       }).then(() => {
          config.data.ssl.client_auth.force = false;
          notify.info(gettext('Generating certificate'), gettext('Please wait'));
          return $http.get('/api/settings/generate-server-certificate').success(function(data) {
             notify.success(gettext('Certificate successfully generated'));
             config.data.ssl.enable = true;
             config.data.ssl.certificate = data.path;
             config.data.ssl.client_auth.certificates = [];
             $scope.save();
          })
          .error(err => notify.error(gettext('Certificate generation failed'), err.message));
       })
    ;

    $scope.restart = () => core.restart();
});
 
