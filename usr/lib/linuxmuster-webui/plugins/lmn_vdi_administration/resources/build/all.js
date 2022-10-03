'use strict';

// the module should depend on 'core' to use the stock services & components
angular.module('lmn.vdi_administration', ['core']);


'use strict';

angular.module('lmn.vdi_administration').config(function ($routeProvider) {
    $routeProvider.when('/view/lmn_vdi_administration', {
        templateUrl: '/lmn_vdi_administration:resources/partial/index.html',
        controller: 'Lmn_vdi_administrationIndexController'
    });
});


'use strict';

angular.module('lmn.vdi_administration').controller('Lmn_vdi_administrationIndexController', function ($scope, $uibModal, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_vdi_administration'));

    $http.get('/api/lmn/vdi/administration/masterVMs').then(function (resp) {
        if (resp.data.status == "success") {
            $scope.masterVmGroupStates = resp.data.data;
        } else {
            notify.error(resp.data.message);
            $scope.masterVmGroupStates = {};
        }
    });

    $scope.getClones = function () {
        $http.get('/api/lmn/vdi/administration/clones').then(function (resp) {
            if (resp.data.status == "success") {
                var vdiCloneGroups = resp.data.data;

                var vdiCloneArray = {};
                var _iteratorNormalCompletion = true;
                var _didIteratorError = false;
                var _iteratorError = undefined;

                try {
                    for (var _iterator = Object.entries(vdiCloneGroups)[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                        var _step$value = babelHelpers.slicedToArray(_step.value, 2),
                            key = _step$value[0],
                            value = _step$value[1];

                        var _iteratorNormalCompletion2 = true;
                        var _didIteratorError2 = false;
                        var _iteratorError2 = undefined;

                        try {
                            for (var _iterator2 = Object.entries(value.clone_vms)[Symbol.iterator](), _step2; !(_iteratorNormalCompletion2 = (_step2 = _iterator2.next()).done); _iteratorNormalCompletion2 = true) {
                                var _step2$value = babelHelpers.slicedToArray(_step2.value, 2),
                                    jkey = _step2$value[0],
                                    jvalue = _step2$value[1];

                                vdiCloneArray[jkey] = jvalue;
                            }
                        } catch (err) {
                            _didIteratorError2 = true;
                            _iteratorError2 = err;
                        } finally {
                            try {
                                if (!_iteratorNormalCompletion2 && _iterator2.return) {
                                    _iterator2.return();
                                }
                            } finally {
                                if (_didIteratorError2) {
                                    throw _iteratorError2;
                                }
                            }
                        }

                        ;
                    }
                } catch (err) {
                    _didIteratorError = true;
                    _iteratorError = err;
                } finally {
                    try {
                        if (!_iteratorNormalCompletion && _iterator.return) {
                            _iterator.return();
                        }
                    } finally {
                        if (_didIteratorError) {
                            throw _iteratorError;
                        }
                    }
                }

                ;

                $scope.vdiClones = vdiCloneArray;
            } else {
                notify.error(resp.data.message);
                $scope.vdiClones = {};
            }
        });
    };

    $scope.showGroupInfo = function (_masterGroupData) {
        $uibModal.open({
            templateUrl: '/lmn_vdi_administration:resources/partial/groupinfo.modal.html',
            controller: 'LMGroupInfoModalController',
            resolve: {
                masterGroupData: function masterGroupData() {
                    return _masterGroupData;
                }
            }
        });
    };

    $scope.showMasterInfo = function (_masterVM, _masterVMData) {
        $uibModal.open({
            templateUrl: '/lmn_vdi_administration:resources/partial/masterinfo.modal.html',
            controller: 'LMMasterInfoModalController',
            resolve: {
                masterVM: function masterVM() {
                    return _masterVM;
                },
                masterVMData: function masterVMData() {
                    return _masterVMData;
                }
            }
        });
    };
});

angular.module('lmn.vdi_administration').controller('LMGroupInfoModalController', function ($scope, $uibModalInstance, $http, masterGroupData) {
    $scope.masterGroupData = masterGroupData;

    $scope.close = function () {
        $uibModalInstance.dismiss();
    };
});

angular.module('lmn.vdi_administration').controller('LMMasterInfoModalController', function ($scope, $uibModalInstance, $http, masterVM, masterVMData) {
    $scope.masterVM = masterVM;
    $scope.masterVMData = masterVMData;

    $scope.close = function () {
        $uibModalInstance.dismiss();
    };
});


