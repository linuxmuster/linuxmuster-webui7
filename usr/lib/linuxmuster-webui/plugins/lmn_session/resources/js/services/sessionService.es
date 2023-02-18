angular.module('lmn.session').service('lmnSession', function($http, $uibModal, $q, $location, messagebox, validation, notify, gettext) {

    this.sessions = [];

    this.current = {
        'id': '',
        'comment': '',
        'participants': []
    };

    this.load = () => {
        var promiseList = [];
        promiseList.push($http.get('/api/lmn/groupmembership/groups').then((resp) => {
            var groups = resp.data[0];
            this.classes = groups.filter((elt) => {return elt.type == 'schoolclass'});
            this.classes = this.classes.filter((elt) => {return elt.membership == true});
        }));

        promiseList.push($http.get('/api/lmn/session/sessions').then((resp) => {
            if (resp.data.length == 0) {
                this.sessions = resp.data;
                this.info.message = gettext("There are no sessions yet. Create a session using the 'New Session' button at the top!");
            } else {
                    this.sessions = resp.data;
            }
        }));

        return $q.all(promiseList).then(() => {return [this.classes, this.sessions]});
    }

    this.start = (session) => {
        this.current = session;console.warn(this.current);
        $location.path('/view/lmn/session');
    }

    this.new = () => {
        return messagebox.prompt(gettext('Session Name'), '').then((msg) => {
            if (!msg.value) {return}

            testChar = validation.isValidLinboConf(msg.value);
            if (testChar != true) {
                notify.error(gettext(testChar));
                return
            }

            return $http.put(`/api/lmn/session/sessions/${msg.value}`, {}).then((resp) => {
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

    this.getParticipants = (session) => {
        return $http.get(`/api/lmn/session/sessions/${session}`).then((resp) => {
            return resp.data;
        });
    }

    return this;
});
