angular.module('lmn.crontab').controller('CrontabIndexController', function($scope, $http, $log, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Cron'));

    $scope.title = gettext('Cron');
    $scope.crontab_user_selected = 'globaladministrator';
    $scope.modifyJob = null;
    $scope.new = {
        'normal_tasks': {
            'minute':'*',
            'hour':'*',
            'day_of_month':'*',
            'month':'*',
            'day_of_week':'*',
            'command':'',
            'comment':'',
            'new': true
        },
        'special_tasks': {
            'special': '@reboot',
            'command': '',
            'comment': '',
            'new': true
        },
        'env_settings': {
            'name': '',
            'value': '',
            'comment': '',
            'new': true
        }
    };

    $scope.translate = {
        'normal_tasks': gettext('normal task'),
        'special_tasks': gettext('special task'),
        'env_settings': gettext('environment variable')
    }
    $scope.special = ['@reboot', '@yearly', '@annually', '@monthly', '@weekly', '@daily', '@hourly']

    $scope.switchCrontab = () => {
        if ($scope.crontab_user_selected == 'root') {
           $scope.crontabs['globaladministrator'] = $scope.crontab;
        } else {
           $scope.crontabs['root'] = $scope.crontab;
        }
        $scope.crontab = $scope.crontabs[$scope.crontab_user_selected];
    }

    $scope.add = (type) => {
        job = angular.copy($scope.new[type]);
        job.school = $scope.school;
        $scope.modify(type, job);
    }

    $scope.remove = (type, values) => {
        position = $scope.crontab[type].indexOf(values);
        $scope.crontab[type].splice(position, 1);
    }

    $http.get('/api/lmn/crontab').then( (resp) => {
        $scope.crontabs = {
            'globaladministrator': resp.data[0],
            'root': resp.data[1],
        };
        $scope.school = resp.data[2];

        $scope.crontab = $scope.crontabs.globaladministrator;
    });

    $scope.modify = (type, job) => {
        $scope.modifyJob={'type':type,'job':job};
    }

    $scope.closeDialog = (type, job) => {
        if (job.new) {
            delete job.new;
            $scope.crontab[type].push(job);
        }
        $scope.modifyJob = null;
    }

    $scope.reset = () => {
        $scope.modifyJob = null;
    }

    $scope.save = () => {
        $http.post('/api/lmn/crontab', {
            'globaladministrator': $scope.crontabs.globaladministrator,
            'root': $scope.crontabs.root
        }).then((resp) => {
            notify.success(gettext('Crontab successfully saved !'));
        }, error => {
            $log.log('Failed to save crontab', error);
            notify.error(gettext('Failed to save crontab'));
        });
    };

});

