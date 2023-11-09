angular.module('lmn.websession').service('webSession', function($http, $window, notify, gettext, identity) {

    this.websessionIsRunning = false;

    this.getWebConferenceEnabled = () => {
        $http.get('/api/lmn/websession/webConferenceEnabled').then((resp) => {
            if (resp.data == true) {
                this.websessionEnabled = true;
                this.websessionGetStatus();
            } else {
                this.websessionEnabled = false;
            }
        });
    }

    this.status = (session) => {
        sessionname = session.name + "-" + session.sid;
        $http.get("/api/lmn/websession/webConference/#{sessionname}").then((resp) => {
            if (resp.data["status"] == "SUCCESS") {
                if (resp.data["data"]["status"] == "started") {
                    this.websessionIsRunning = true;
                } else {
                    this.websessionIsRunning = false;
                }
                this.websessionID = resp.data["data"]["id"];
                this.websessionAttendeePW = resp.data["data"]["attendeepw"];
                this.websessionModeratorPW = resp.data["data"]["moderatorpw"];
            } else {
                this.websessionIsRunning = false;
            }
        });
    }

    this.toggle = () => {
        if (this.websessionIsRunning == false) {
            this.start();
        } else {
            this.stop();
        }
    }

    this.stop = () => {
        $http.post('/api/lmn/websession/endWebConference', {id: this.websessionID, moderatorpw: this.websessionModeratorPW}).then( (resp) => {
            $http.delete("/api/lmn/websession/webConference/#{this.websessionID}").then((resp) => {
                if (resp.data["status"] == "SUCCESS") {
                    notify.success(gettext("Successfully stopped!"));
                    this.websessionIsRunning = false;
                } else {
                    notify.error(gettext('Cannot stop entry!'));
                }
            });
        });
    }

    this.start = (session) => {
        tempparticipants = [];
        for (participant of session.members) {
            tempparticipants.push(participant.sAMAccountName);
        };

        sessionname = session.name + "-" + session.sid ;

        $http.post('/api/lmn/websession/webConferences', {sessionname: sessionname, sessiontype: "private", sessionpassword: "", participants: tempparticipants}).then((resp) => {
            if (resp.data["status"] == "SUCCESS") {
                this.websessionID = resp.data["id"];
                this.websessionAttendeePW = resp.data["attendeepw"];
                this.websessionModeratorPW = resp.data["moderatorpw"];
                $http.post('/api/lmn/websession/startWebConference', {sessionname: sessionname, id: this.websessionID, attendeepw: this.websessionAttendeePW, moderatorpw: this.websessionModeratorPW}).then((resp) => {
                    if (resp.data["returncode"] == "SUCCESS") {
                        $http.post('/api/lmn/websession/joinWebConference', {id: this.websessionID, password: this.websessionModeratorPW, name: this.identity.profile.sn + ", " + this.identity.profile.givenName}).then( (resp) => {
                            this.websessionIsRunning = true;
                            window.open(resp.data, '_blank');
                        });
                    } else {
                        notify.error(gettext('Cannot start websession! Try to reload page!'));
                    }
                });
            } else {
                notify.error(gettext("Create session failed! Try again later!"));
            }
        });
    }

    return this;
});