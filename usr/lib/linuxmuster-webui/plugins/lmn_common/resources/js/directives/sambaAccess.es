angular.module('core').directive('sambaAccess', identity =>
    ({
        restrict: 'A',
        link($scope, element, attr) {
            let template = `
                <div class="text-center root-access-blocker">
                    <h1>
                        <i class="fas fa-exclamation-triangle"></i>
                    </h1>
                    <h4 class="alert alert-danger" translate>
                        You should not use WebUI as root user!<br />
                        If this is your first time running WebUI, proceed through the <a href="/view/lmn/init/welcome">setup wizard</a>.<br />
                        Afterwards login using the global-admin account.
                    </h4>
                </div>`;
            identity.promise.then(() => {
                if (!identity.profile.sophomorixRole) {
                    element.empty().append($(template));
                }
            });
        }
    })
);
