angular.module('core').directive('teacherAccess', identity =>
    ({
        restrict: 'A',
        link($scope, element, attr) {
            let template = `
                <div class="text-center root-access-blocker">
                    <h1>
                        <i class="fas fa-exclamation-triangle"></i>
                    </h1>
                    <h4 class="alert alert-danger" translate>
                        This page is restricted to teachers!
                    </h4>
                </div>`;
            identity.promise.then(() => {
                if (identity.profile.sophomorixRole == 'student') {
                    element.empty().append($(template));
                }
            });
        }
    })
);
