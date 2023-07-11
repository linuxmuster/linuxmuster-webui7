angular.module('lmn.session_new').service('lmnSession', function($http, $uibModal, $q, $location, messagebox, validation, notify, gettext) {

    this.sessions = [];

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
            if (resp.data.length == 0) {
                this.info.message = gettext("There are no sessions yet. Create a session using the 'New Session' button at the top!");
            }
        }));

        return $q.all(promiseList).then(() => {return [this.schoolclasses, this.projects, this.sessions]});
    }

    this.start = (session) => {
        this.current = session;
        $http.post('/api/lmn/session/userinfo', {'users': this.current.members}).then((resp) => {
            this.current.members = resp.data;
            this.current.generated = false;
            this.current.type = 'session';
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
        $location.path('/view/lmn/session');
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

    this.getParticipants = () => {
        // TODO : URL does not exist anymore
        return $http.get(`/api/lmn/session/sessions/${this.current.sid}`).then((resp) => {
            return resp.data;
        });
    }

    return this;
});
