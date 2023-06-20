angular.module('lmn.settings').controller('LMglobalSettingsController', ($scope, $http, $sce, $location, notify, pageTitle, identity, messagebox, config, core, locale, gettext) => {
    pageTitle.set(gettext('Global Settings'));

    config.load();
    $scope.config = config;

    $scope.newClientCertificate = {
        c: 'NA',
        st: 'NA',
        o: '',
        cn: ''
    };

    $scope.activetab = 0;

    $scope.help_trusted_domains = gettext(
        "If Ajenti is installed behind a proxy, oder reachable by a fqdn other than provided by the host,\n" +
        "you can then specify the other domains here, and by this way avoiding some resources loading problems."
    )

    $scope.help_trusted_proxies = gettext(
        "If Ajenti is installed behind one or more proxies, specify the ip of these proxies here, in order to\n" +
        "get the real client ip address."
    )

    $scope.help_certificate = gettext(
        "This certificate is the default certificate used to create client certificate and to provide https connection.\n" +
        "Using a Let's Encrypt certificate here will break the client certificate generator.\n" +
        "Using a self-generated certificate is fine here."
    );

    $scope.help_fqdn_certificate = gettext(
        "If you have a special certificate for your domain, like a Let's Encrypt certificate, put it there.\n" +
        "If you are not sure, just use the same certificate as the one above."
    );

    $http.get('/api/lmn/subnets').then((resp) => $scope.subnets = resp.data);

    $scope.removeSubnet = (subnet) => {
        messagebox.show({
            text: gettext('Are you sure you want to delete permanently this subnet ?'),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => $scope.subnets.remove(subnet))
    }

    $scope.addSubnet = () => {
        $scope.subnets.push({'routerIp':'', 'network':'', 'beginRange':'', 'endRange':'', 'setupFlag':''});
    }

    $scope.saveApplySubnets = () => {
        $http.post('/api/lmn/subnets', $scope.subnets).then(() => {
            notify.success(gettext('Saved'));
        });
    }

    $scope.getSmtpConfig = () => {
        config.getSmtpConfig().then((smtpConfig) => $scope.smtp_config = smtpConfig);
    };

    $scope.add_trusted_proxy = () => {
        config.data.trusted_proxies.push("");
    };

    $scope.add_trusted_domain = () => {
        config.data.trusted_domains.push("");
    };

    $scope.delete_trusted_proxy = (proxy) => {
        messagebox.show({
            title: gettext(`Remove ${proxy}`),
            text: gettext(`Do you really want to remove the proxy ${proxy} from the list ?`),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            pos = $scope.config.data.trusted_proxies.indexOf(proxy);
            $scope.config.data.trusted_proxies.splice(pos, 1);
            notify.success(gettext(`${proxy} removed`));
        });
    };

    $scope.delete_trusted_domain = (domain) => {
        messagebox.show({
            title: gettext(`Remove ${domain}`),
            text: gettext(`Do you really want to remove the domain ${domain} from the list ?`),
            positive: gettext('Delete'),
            negative: gettext('Cancel')
        }).then(() => {
            pos = $scope.config.data.trusted_domains.indexOf(domain);
            $scope.config.data.trusted_domains.splice(pos, 1);
            notify.success(gettext(`${domain} removed`));
        });
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

    $scope.save = () => {
        config.save().then(data =>
            notify.success(gettext('Global config saved'))
        ).catch(() =>
            notify.error(gettext('Could not save global config')));

        if ($scope.smtp_config) {
            config.setSmtpConfig($scope.smtp_config).then(data =>
                notify.success(gettext('Smtp config saved'))
            ).catch(() =>
                notify.error(gettext('Could not save smtp config')));
        }
    }

    $scope.createNewServerCertificate = () =>
       messagebox.show({
          title: gettext('Self-signed certificate'),
          text: gettext('Generating a new certificate will void all existing client authentication certificates!'),
          positive: gettext('Generate'),
          negative: gettext('Cancel')
       }).then(() => {
          config.data.ssl.client_auth.force = false;
          notify.info(gettext('Generating certificate'), gettext('Please wait'));
          return $http.get('/api/settings/generate-server-certificate').then(function(resp) {
             notify.success(gettext('Certificate successfully generated'));
             config.data.ssl.enable = true;
             config.data.ssl.certificate = resp.data.path;
             config.data.ssl.client_auth.certificates = [];
             $scope.save();
          }, (err) => notify.error(gettext('Certificate generation failed'), err.message));
       })
    ;

    $scope.restart = () => core.restart();
});
 
