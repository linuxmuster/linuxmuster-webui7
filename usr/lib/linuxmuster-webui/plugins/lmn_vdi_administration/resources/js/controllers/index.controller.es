angular.module('lmn.vdi_administration').controller('Lmn_vdi_administrationIndexController', function ($scope, $uibModal, $http, pageTitle, gettext, notify) {
    pageTitle.set(gettext('Lmn_vdi_administration'));

    $http.get('/api/lmn/vdi/administration/masterVMs').then((resp) => {
        if(resp.data.status == "success") {
            $scope.masterVmGroupStates = resp.data.data;
        }
        else {
            notify.error(resp.data.message);
            $scope.masterVmGroupStates = {};
        }
    });

    $scope.getClones = () => {
        $http.get('/api/lmn/vdi/administration/clones').then((resp) => {
            if(resp.data.status == "success") {
                var vdiCloneGroups = resp.data.data;

                var vdiCloneArray={};
                for (let [key, value] of Object.entries(vdiCloneGroups)) {
                    for (let [jkey, jvalue] of Object.entries(value.clone_vms)) {
                        vdiCloneArray[jkey]=jvalue;
                    };                
                };
        
                $scope.vdiClones=vdiCloneArray;
            }
            else {
                notify.error(resp.data.message);
                $scope.vdiClones = {};
            }

        });

    }

    $scope.showGroupInfo = (masterGroupData) => {
        $uibModal.open({
            templateUrl: '/lmn_vdi_administration:resources/partial/groupinfo.modal.html',
            controller: 'LMGroupInfoModalController',
            resolve: {
                masterGroupData: () => masterGroupData
            }
        });
    }

    $scope.showMasterInfo = (masterVM, masterVMData) => {
        $uibModal.open({
            templateUrl: '/lmn_vdi_administration:resources/partial/masterinfo.modal.html',
            controller: 'LMMasterInfoModalController',
            resolve: {
                masterVM: () => masterVM,
                masterVMData: () => masterVMData,
            }
        });
    }

});

angular.module('lmn.vdi_administration').controller('LMGroupInfoModalController', function ($scope, $uibModalInstance, $http, masterGroupData) {
    $scope.masterGroupData = masterGroupData;

    $scope.close = () => {
        $uibModalInstance.dismiss()
    }
});

angular.module('lmn.vdi_administration').controller('LMMasterInfoModalController', function ($scope, $uibModalInstance, $http, masterVM, masterVMData) {
    $scope.masterVM = masterVM;
    $scope.masterVMData = masterVMData;

    $scope.close = () => {
        $uibModalInstance.dismiss()
    }
});
