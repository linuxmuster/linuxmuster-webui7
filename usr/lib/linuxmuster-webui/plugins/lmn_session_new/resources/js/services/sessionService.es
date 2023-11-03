angular.module('lmn.session_new').service('lmnSession', function($http, $uibModal, $q, $location, $window, messagebox, validation, notify, gettext, identity) {

    this.sessions = [];
    this.user_missing_membership = [];

    this.load = () => {
        var promiseList = [];
        promiseList.push($http.get('/api/lmn/session/schoolclasses').then((resp) => {
            this.schoolclasses = resp.data;
        }));

        promiseList.push($http.get('/api/lmn/session/projects').then((resp) => {
            this.projects = resp.data;
        }));

        promiseList.push($http.get('/api/lmn/session/sessions').then((resp) => {
            this.sessions = resp.data;
        }));

        return $q.all(promiseList).then(() => {return [this.schoolclasses, this.projects, this.sessions]});
    }

    this.filterExamUsers = () => {
        this.extExamUsers = this.current.members.filter((user) => !['---', identity.user].includes(user.sophomorixExamMode[0]));
        this.examUsers = this.current.members.filter((user) => [identity.user].includes(user.sophomorixExamMode[0]));
    }

    this._createWorkingDirectory = (user) => {
        return $http.post('/api/lmn/smbclient/createSessionWorkingDirectory', {'user': user.cn})
            .catch(err => {
                // notify.error(err.data.message);
                if (user.sophomorixAdminClass == 'teachers') {
                    user.files = 'ERROR-teacher';
                } else {
                    user.files = 'ERROR';
                    this.user_missing_membership.push(user);
                }
            });
    }

    this.createWorkingDirectory = (users) => {
        this.user_missing_membership = [];
        var promises = [];
        for (user of users) {
            promises.push(this._createWorkingDirectory(user));
        }
        return $q.all(promises);
    }

    this.start = (session) => {
        this.current = session;
        $http.post('/api/lmn/session/userinfo', {'users': this.current.members}).then((resp) => {
            this.current.members = resp.data;
            this.current.generated = false;
            this.current.type = 'session';
            this.filterExamUsers();
            $location.path('/view/lmn/session');
        });
    }

    this.reset = () => {
       this.current = {
            'sid': '',
            'name': '',
            'generated': false,
            'members': [],
            'type': '',
        };
    }

    this.reset();

    this.startGenerated = (groupname, members, session_type) =>  {
        generatedSession = {
            'sid': Date.now(),
            'name': groupname,
            'members': members,
            'generated': true,
            'type': session_type, // May be room or schoolclass or project
        };
        this.current = generatedSession;
        this.filterExamUsers();
        $location.path('/view/lmn/session');
    }

    this.getExamUsers = () => {
       users = this.current.members.map((user) => user.cn);
       $http.post('/api/lmn/session/exam/userinfo', {'users': users}).then((resp) => {
            this.current.members = resp.data;
            this.createWorkingDirectory(this.current.members.map((user) => user.cn));
            this.filterExamUsers();
            $location.path('/view/lmn/session');
        });
    }

    this.refreshUsers = () => {
        users = this.current.members.map((user) => user.cn);
        return $http.post('/api/lmn/session/userinfo', {'users': users}).then((resp) => {
            this.current.members = resp.data;
            this.filterExamUsers();
            $location.path('/view/lmn/session');
        });
    }

    this.new = (members = []) => {
        return messagebox.prompt(gettext('Session Name'), '').then((msg) => {
            if (!msg.value) {return}

            testChar = validation.isValidLinboConf(msg.value);
            if (testChar != true) {
                notify.error(gettext(testChar));
                return
            }

            return $http.put(`/api/lmn/session/sessions/${msg.value}`, {members: members}).then((resp) => {
                notify.success(gettext('Session Created'));
            });
        });
    }

    this.rename = (sessionID, comment) => {
        if (!sessionID) {
            messagebox.show({title: gettext('No Session selected'), text: gettext('You have to select a session first.'), positive: 'OK'});
            return;
        }

        return messagebox.prompt(gettext('Session Name'), comment).then((msg) => {
            if (!msg.value) {return;}

            testChar = validation.isValidLinboConf(msg.value);
            if (testChar != true) {
                notify.error(gettext(testChar));
                return
            }
            return $http.post('/api/lmn/session/sessions', {action: 'rename-session', session: sessionID, comment: msg.value}).then((resp) => {
                notify.success(gettext('Session renamed'));
                return msg.value;
            });
        });
    }

    this.kill = (sessionID, comment) => {
        if (!sessionID) {
            messagebox.show({title: gettext('No session selected'), text: gettext('You have to select a session first.'), positive: 'OK'});
            return
        }

        return messagebox.show({text: gettext(`Delete Session: ${comment} ?`), positive: gettext('Delete'), negative: gettext('Cancel')}).then(() => {
            return $http.delete(`/api/lmn/session/sessions/${sessionID}`).then((resp) => {
                notify.success(gettext(resp.data));
            });
        });
    }

    return this;
});
