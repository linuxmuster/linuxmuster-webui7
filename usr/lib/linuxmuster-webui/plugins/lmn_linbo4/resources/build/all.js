// Generated by CoffeeScript 2.6.1
(function() {
  angular.module('lmn.linbo4', ['core', 'lmn.common', 'angular-sortable-view', 'colorpicker.module']);

}).call(this);

// Generated by CoffeeScript 2.6.1
(function() {
  var indexOf = [].indexOf;

  angular.module('lmn.linbo4').config(function($routeProvider) {
    return $routeProvider.when('/view/lmn/linbo4', {
      controller: 'LMLINBO4Controller',
      templateUrl: '/lmn_linbo4:resources/partial/index.html'
    });
  });

  angular.module('lmn.linbo4').controller('LMImportDevicesApplyModalController', function($scope, $http, $uibModalInstance, $route, gettext, notify) {
    $scope.logVisible = true;
    $scope.isWorking = true;
    $scope.showLog = function() {
      return $scope.logVisible = !$scope.logVisible;
    };
    $http.post('/api/lmn/devices/import').then(function(resp) {
      $scope.isWorking = false;
      return notify.success(gettext('Import complete'));
    }).catch(function(resp) {
      notify.error(gettext('Import failed'), resp.data.message);
      $scope.isWorking = false;
      return $scope.showLog();
    });
    return $scope.close = function() {
      $uibModalInstance.close();
      return $route.reload();
    };
  });

  angular.module('lmn.linbo4').controller('LMLINBO4AcceptModalController', function($scope, $uibModalInstance, $http, partition, disk) {
    $scope.partition = partition;
    $scope.disk = disk;
    $scope.save = function() {
      return $uibModalInstance.close({
        response: 'accept'
      });
    };
    return $scope.close = function() {
      return $uibModalInstance.dismiss();
    };
  });

  angular.module('lmn.linbo4').controller('LMLINBO4PartitionModalController', function($scope, $uibModalInstance, $http, partition, messagebox, os) {
    $scope.partition = partition;
    $scope.os = os;
    $http.get('/api/lmn/linbo4/icons').then(function(resp) {
      $scope.icons = resp.data;
      $scope.image_extension = 'svg';
      $scope.show_png_warning = false;
      if ($scope.os !== null) {
        if ($scope.os.IconName.endsWith('png')) {
          return $scope.show_png_warning = true;
        }
      }
    });
    $http.get('/api/lmn/linbo4/images').then(function(resp) {
      var i, len, oses;
      $scope.images = [];
      oses = resp.data;
      for (i = 0, len = oses.length; i < len; i++) {
        os = oses[i];
        $scope.images.push(os.name + '.qcow2');
      }
      if ($scope.os !== null) {
        if ($scope.images.indexOf($scope.os.BaseImage) < 0) {
          return $scope.images.push($scope.os.BaseImage);
        }
      }
    });
    $scope.addNewImage = function() {
      return messagebox.prompt('New image name', '').then(function(msg) {
        return $scope.images.push(msg.value);
      });
    };
    $scope.save = function() {
      return $uibModalInstance.close({
        partition: $scope.partition,
        os: $scope.os
      });
    };
    return $scope.close = function() {
      return $uibModalInstance.dismiss();
    };
  });

  angular.module('lmn.linbo4').controller('LMLINBO4BackupsModalController', function($scope, $uibModal, $uibModalInstance, $http, gettext, messagebox, image) {
    $scope.image = image;
    return $scope.close = function() {
      return $uibModalInstance.dismiss();
    };
  });

  angular.module('lmn.linbo4').controller('LMLINBO4ImageModalController', function($scope, $uibModal, $uibModalInstance, $http, gettext, filesystem, messagebox, image, images) {
    var x;
    $scope.image = image;
    console.log(image);
    $scope.desc_textarea_rows = $scope.image.desc ? $scope.image.desc.split(/\r\n|\r|\n/).length + 1 : 1;
    $scope.info_textarea_rows = $scope.image.info ? $scope.image.info.split(/\r\n|\r|\n/).length + 1 : 1;
    $scope.imagesWithReg = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = images.length; i < len; i++) {
        x = images[i];
        if (x.reg) {
          results.push(x);
        }
      }
      return results;
    })();
    $scope.imagesWithPostsync = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = images.length; i < len; i++) {
        x = images[i];
        if (x.postsync) {
          results.push(x);
        }
      }
      return results;
    })();
    $scope.imagesWithPrestart = (function() {
      var i, len, results;
      results = [];
      for (i = 0, len = images.length; i < len; i++) {
        x = images[i];
        if (x.prestart) {
          results.push(x);
        }
      }
      return results;
    })();
    $http.get('/api/lmn/linbo4/examples/reg').then(function(resp) {
      return $scope.exampleRegs = resp.data;
    });
    $scope.setExampleReg = function(name) {
      return filesystem.read(`/srv/linbo/examples/${name}`).then(function(content) {
        return $scope.image.reg = content;
      });
    };
    $http.get('/api/lmn/linbo4/examples/postsync').then(function(resp) {
      return $scope.examplePostsyncs = resp.data;
    });
    $http.get('/api/lmn/linbo4/examples/prestart').then(function(resp) {
      return $scope.examplePrestarts = resp.data;
    });
    $scope.setExamplePostsync = function(name) {
      return filesystem.read(`/srv/linbo/examples/${name}`).then(function(content) {
        return $scope.image.postsync = content;
      });
    };
    $scope.setExamplePrestart = function(name) {
      return filesystem.read(`/srv/linbo/examples/${name}`).then(function(content) {
        return $scope.image.prestart = content;
      });
    };
    $scope.save = function() {
      return $uibModalInstance.close(image);
    };
    return $scope.close = function() {
      return $uibModalInstance.dismiss();
    };
  });

  angular.module('lmn.linbo4').controller('LMLINBO4ConfigModalController', function($scope, $uibModal, $uibModalInstance, $timeout, $http, $log, gettext, messagebox, config, lmFileBackups, identity, vdiconfig) {
    var DiskType, _device, _partition, disk, diskMap, i, j, len, len1, ref, ref1;
    $scope.config = config;
    $scope.vdiconfig = vdiconfig;
    $scope.expert = false;
    $scope.privateConf = false;
    if ('School' in config.config.LINBO) {
      if (config.config.LINBO.School !== 'default-school') {
        $scope.privateConf = true;
      }
    }
    $scope.togglePrivateConf = function() {
      if ($scope.privateConf) {
        $scope.privateConf = false;
        return config.config.LINBO.School = 'default-school';
      } else {
        $scope.privateConf = true;
        return config.config.LINBO.School = $scope.identity.profile.activeSchool;
      }
    };
    $scope.toggleExpert = function() {
      if ($scope.expert) {
        return $scope.expert = false;
      } else {
        return $scope.expert = true;
      }
    };
    if ($scope.config.config.LINBO.BackgroundColor) {
      $scope.config.config.LINBO.BackgroundColor = '#' + $scope.config.config.LINBO.BackgroundColor;
    }
    $scope.kernelOptions = ['quiet', 'splash', 'acpi=noirq', 'acpi=off', 'irqpoll', 'dhcpretry=9'];
    $scope.colors = ['white', 'black', 'lightCyan', 'cyan', 'darkCyan', 'orange', 'red', 'darkRed', 'pink', 'magenta', 'darkMagenta', 'lightGreen', 'green', 'darkGreen', 'lightYellow', 'yellow', 'gold', 'lightBlue', 'blue', 'darkBlue', 'lightGray', 'gray', 'darkGray'];
    $scope.disks = [];
    diskMap = {};
    $http.get('/api/lmn/linbo4/images').then(function(resp) {
      return $scope.oses = resp.data;
    });
    ref = $scope.config.partitions;
    for (i = 0, len = ref.length; i < len; i++) {
      _partition = ref[i];
      // Determine the position of the partition integer.
      // Different devices have it on a different position
      if (_partition['Dev'].indexOf("nvme") !== -1) {
        _device = _partition.Dev.substring(0, '/dev/nvme0n1p'.length);
      }
      if (_partition['Dev'].indexOf("mmcblk") !== -1) {
        _device = _partition.Dev.substring(0, '/dev/mmcblk0p'.length);
      }
      if (_partition['Dev'].indexOf("sd") !== -1) {
        _device = _partition.Dev.substring(0, '/dev/sdX'.length);
      }
      if (!diskMap[_device]) {
        if (_device.indexOf("sd") !== -1) {
          DiskType = 'sata';
        }
        if (_device.indexOf("mmcblk") !== -1) {
          DiskType = 'mmc';
        }
        if (_device.indexOf("nvme") !== -1) {
          DiskType = 'nvme';
        }
        diskMap[_device] = {
          name: _device,
          partitions: [],
          DiskType: DiskType
        };
        $scope.disks.push(diskMap[_device]);
      }
      diskMap[_device].partitions.push(_partition);
      _partition._isCache = _partition.Dev === $scope.config.config.LINBO.Cache;
    }
    $scope.config_backup = angular.copy($scope.config);
    ref1 = $scope.disks;
    for (j = 0, len1 = ref1.length; j < len1; j++) {
      disk = ref1[j];
      disk.partitions.sort(function(a, b) {
        if (a.Dev > b.Dev) {
          return 1;
        } else {
          return -1;
        }
      });
    }
    $scope.getAllInfo = function() {};
    $scope.updateDiskType = function(disk) {
      var newDiskType, oldDiskName;
      oldDiskName = disk.name;
      newDiskType = disk.DiskType;
      if (newDiskType === 'sata') {
        disk.name = 'a';
        while (true) {
          if (diskMap[`/dev/sd${disk.name}`]) {
            disk.name = String.fromCharCode(disk.name.charCodeAt(0) + 1);
            continue;
          }
          break;
        }
        disk.name = `/dev/sd${disk.name}`;
      }
      if (newDiskType === 'mmc') {
        disk.name = '0';
        while (true) {
          if (diskMap[`/dev/mmcblk${disk.name}p`]) {
            disk.name = String.fromCharCode(disk.name.charCodeAt(0) + 1);
            continue;
          }
          break;
        }
        disk.name = `/dev/mmcblk${disk.name}p`;
      }
      if (newDiskType === 'nvme') {
        disk.name = '0';
        while (true) {
          if (diskMap[`/dev/nvme${disk.name}n1p`]) {
            disk.name = String.fromCharCode(disk.name.charCodeAt(0) + 1);
            continue;
          }
          break;
        }
        disk.name = `/dev/nvme${disk.name}n1p`;
      }
      //diskMap
      $scope.rebuildDisks();
      // create new object with the actual diskname
      diskMap[disk.name] = disk;
      // remove the old diskname
      return delete diskMap[oldDiskName];
    };
    $scope.addDisk = function() {
      disk = 'a';
      while (true) {
        if (diskMap[`/dev/sd${disk}`]) {
          disk = String.fromCharCode(disk.charCodeAt(0) + 1);
          continue;
        }
        break;
      }
      disk = `/dev/sd${disk}`;
      diskMap[disk] = {
        name: disk,
        partitions: [],
        DiskType: 'sata'
      };
      return $scope.disks.push(diskMap[disk]);
    };
    $scope.removeDisk = function(disk) {
      delete diskMap[disk.name];
      return $scope.disks.remove(disk);
    };
    $scope.getSize = function(partition) {
      var ps, s;
      if (!partition.Size || !partition.Size.toLowerCase) {
        return;
      }
      ps = partition.Size.toLowerCase();
      s = parseInt(ps) * 1024;
      if (ps[ps.length - 1] === 'm') {
        s *= 1024;
      }
      if (ps[ps.length - 1] === 'g') {
        s *= 1024 * 1024;
      }
      if (ps[ps.length - 1] === 't') {
        s *= 1024 * 1024 * 1024;
      }
      return s;
    };
    $scope.isSwapPartition = function(partition) {
      return partition.FSType === 'swap';
    };
    $scope.isCachePartition = function(partition) {
      return partition.Dev === $scope.config.config.LINBO.Cache;
    };
    $scope.getOS = function(partition) {
      var k, len2, os, ref2;
      ref2 = $scope.config.os;
      for (k = 0, len2 = ref2.length; k < len2; k++) {
        os = ref2[k];
        if (os.Root === partition.Dev) {
          return os;
        }
      }
      return null;
    };
    $scope.getName = function(partition) {
      if ($scope.getOS(partition) && $scope.getOS(partition).Name) {
        return $scope.getOS(partition).Name;
      }
      if (partition.Label) {
        return partition.Label;
      }
      if ($scope.isSwapPartition(partition)) {
        return gettext('Swap');
      }
      if (partition._isCache) {
        return gettext('LINBO Cache');
      }
      if (partition.Id === 'ef') {
        return 'EFI';
      }
      if (partition.Id === '0c01') {
        return 'MSR';
      }
      if (partition.Label) {
        return partition.Label;
      }
      return 'Partition';
    };
    $scope.addSwap = function(disk) {
      disk.partitions.push({
        Bootable: false,
        FSType: 'swap',
        Id: '82',
        Size: '4G',
        Label: ''
      });
      return $scope.rebuildDisks();
    };
    $scope.addData = function(disk) {
      disk.partitions.push({
        Bootable: false,
        FSType: 'ntfs',
        Id: '7',
        Size: '10G',
        Label: ''
      });
      return $scope.rebuildDisks();
    };
    $scope.addEFI = function(disk) {
      disk.partitions.splice(0, 0, {
        Bootable: true,
        FSType: 'vfat',
        Id: 'ef',
        Size: 1024 * 200,
        Label: ''
      });
      return $scope.rebuildDisks();
    };
    $scope.addMSR = function(disk) {
      disk.partitions.splice(1, 0, {
        Bootable: false,
        FSType: '',
        Id: '0c01',
        Size: 1024 * 128,
        Label: ''
      });
      return $scope.rebuildDisks();
    };
    $scope.addExtended = function(disk) {
      disk.partitions.push({
        Bootable: false,
        FSType: '',
        Id: '5',
        Size: '',
        Label: ''
      });
      return $scope.rebuildDisks();
    };
    $scope.addCache = function(disk) {
      disk.partitions.push({
        Bootable: true,
        FSType: 'ext4',
        Id: '83',
        Size: '',
        Label: '',
        _isCache: true
      });
      return $scope.rebuildDisks();
    };
    $scope.addWindows = function(disk) {
      var partition;
      partition = {
        Bootable: true,
        FSType: 'ntfs',
        Id: '7',
        Size: '40G',
        Label: ''
      };
      disk.partitions.push(partition);
      $scope.rebuildDisks();
      return $scope.config.os.push({
        Name: 'Windows 10',
        Version: '',
        Description: 'Windows 10',
        IconName: 'win10.' + $scope.image_extension,
        Image: '',
        BaseImage: '',
        Root: partition.Dev,
        Boot: partition.Dev,
        Kernel: 'auto',
        Initrd: '',
        Append: '',
        StartEnabled: true,
        SyncEnabled: true,
        NewEnabled: true,
        Hidden: true,
        Autostart: false,
        AutostartTimeout: 5,
        DefaultAction: 'sync'
      });
    };
    $scope.addLinux = function(disk) {
      var partition;
      partition = {
        Bootable: true,
        FSType: 'ext4',
        Id: '83',
        Size: '20G',
        Label: ''
      };
      disk.partitions.push(partition);
      $scope.rebuildDisks();
      return $scope.config.os.push({
        Name: 'Ubuntu',
        Version: '',
        Description: 'Ubuntu 16.04',
        IconName: 'ubuntu.' + $scope.image_extension,
        Image: '',
        BaseImage: '',
        Root: partition.Dev,
        Boot: partition.Dev,
        Kernel: 'vmlinuz',
        Initrd: 'initrd.img',
        Append: 'ro splash',
        StartEnabled: true,
        SyncEnabled: true,
        NewEnabled: true,
        Hidden: true,
        Autostart: false,
        AutostartTimeout: 5,
        DefaultAction: 'sync'
      });
    };
    $scope.removePartition = function(partition, disk) {
      return $uibModal.open({
        templateUrl: '/lmn_linbo4:resources/partial/accept.modal.html',
        controller: 'LMLINBO4AcceptModalController',
        resolve: {
          partition: function() {
            return angular.copy(partition.Dev);
          },
          disk: function() {
            return angular.copy(disk);
          }
        }
      }).result.then(function(result) {
        if (result.response === 'accept') {
          disk.partitions.remove(partition);
          return $scope.rebuildDisks();
        }
      });
    };
    $scope.rebuildDisks = function() {
      var k, l, len2, len3, len4, m, newDev, os, partition, partitionIndex, ref2, ref3, ref4, remap, results;
      remap = {};
      ref2 = $scope.disks;
      for (k = 0, len2 = ref2.length; k < len2; k++) {
        disk = ref2[k];
        partitionIndex = 1;
        ref3 = disk.partitions;
        for (l = 0, len3 = ref3.length; l < len3; l++) {
          partition = ref3[l];
          newDev = `${disk.name}${partitionIndex}`;
          if (partition.Dev) {
            remap[partition.Dev] = newDev;
          }
          partition.Dev = newDev;
          partitionIndex++;
          if (partition._isCache) {
            $scope.config.config.LINBO.Cache = partition.Dev;
          }
        }
      }
      $log.log('Remapping OSes', remap);
      ref4 = $scope.config.os;
      results = [];
      for (m = 0, len4 = ref4.length; m < len4; m++) {
        os = ref4[m];
        if (os.Boot) {
          os.Boot = remap[os.Boot];
        }
        if (os.Root) {
          results.push(os.Root = remap[os.Root]);
        } else {
          results.push(void 0);
        }
      }
      return results;
    };
    $scope.getBorderColor = function(partition) {
      if ($scope.isCachePartition(partition)) {
        return '#F3E000';
      }
      if ($scope.isSwapPartition(partition)) {
        return '#E09305';
      }
      if (partition.Id === 'ef') {
        return '#737373';
      }
      if (partition.Id === '0c01') {
        return '#737373';
      }
      if ($scope.getOS(partition)) {
        return '#3232B7';
      }
      return '#58B158';
    };
    $scope.addKernelOption = function(option) {
      return $scope.config.config.LINBO.KernelOptions += ' ' + option;
    };
    $scope.editPartition = function(partition) {
      var os;
      os = $scope.getOS(partition);
      return $uibModal.open({
        templateUrl: '/lmn_linbo4:resources/partial/partition.modal.html',
        controller: 'LMLINBO4PartitionModalController',
        resolve: {
          partition: function() {
            return angular.copy(partition);
          },
          os: function() {
            return angular.copy(os);
          }
        }
      }).result.then(function(result) {
        angular.copy(result.partition, partition);
        if (os) {
          angular.copy(result.os, os);
        }
        return $scope.rebuildDisks();
      });
    };
    $scope.save = function() {
      var config_change, k, l, len2, len3, partition, ref2, ref3;
      $scope.config.partitions = [];
      ref2 = $scope.disks;
      for (k = 0, len2 = ref2.length; k < len2; k++) {
        disk = ref2[k];
        ref3 = disk.partitions;
        for (l = 0, len3 = ref3.length; l < len3; l++) {
          partition = ref3[l];
          $scope.config.partitions.push(partition);
        }
      }
      config_change = !angular.equals(angular.toJson($scope.config), angular.toJson($scope.config_backup));
      // Remove # from background color
      if ($scope.config.config.LINBO.BackgroundColor) {
        $scope.config.config.LINBO.BackgroundColor = $scope.config.config.LINBO.BackgroundColor.substring(1);
      }
      return $uibModalInstance.close([$scope.config, vdiconfig, config_change]);
    };
    $scope.backups = function() {
      return lmFileBackups.show('/srv/linbo/start.conf.' + $scope.config.config.LINBO.Group).then(function() {
        return $uibModalInstance.dismiss();
      });
    };
    return $scope.close = function() {
      return $uibModalInstance.dismiss();
    };
  });

  angular.module('lmn.linbo4').controller('LMLINBO4Controller', function($q, $scope, $http, $uibModal, $log, $route, $location, gettext, notify, pageTitle, tasks, messagebox, validation, toaster, identity) {
    var tag;
    pageTitle.set(gettext('LINBO 4'));
    $scope.tabs = ['groups', 'images'];
    $scope.config_change = false;
    tag = $location.$$url.split("#")[1];
    if (tag && indexOf.call($scope.tabs, tag) >= 0) {
      $scope.activetab = $scope.tabs.indexOf(tag);
    } else {
      $scope.activetab = 0;
    }
    $scope.images_selected = [];
    $scope.$on("$locationChangeStart", function(event) {
      if ($scope.config_change && !confirm(gettext('You should call an import devices process to apply the new changes, quit this page anyway ?'))) {
        return event.preventDefault();
      }
    });
    $http.get('/api/lmn/linbo4/configs').then(function(resp) {
      var allConfigNames, configName, i, len, ref;
      allConfigNames = resp.data;
      $scope.configs = [];
      for (i = 0, len = allConfigNames.length; i < len; i++) {
        configName = allConfigNames[i];
        if (!('School' in configName.settings) || ((ref = configName.settings.School) === identity.profile.activeSchool || ref === 'default-school')) {
          $scope.configs.push(configName);
        }
      }
      return $http.get('/api/lmn/linbo4/images').then(function(resp) {
        var backup, config, date, image, j, len1, ref1, ref2, results;
        $scope.images = resp.data;
        ref1 = $scope.images;
        results = [];
        for (j = 0, len1 = ref1.length; j < len1; j++) {
          image = ref1[j];
          image.backups_list = [];
          ref2 = image.backups;
          for (date in ref2) {
            backup = ref2[date];
            backup.date = date;
            image.backups_list.push(backup);
          }
          image.used_in = [];
          results.push((function() {
            var k, len2, ref3, results1;
            ref3 = $scope.configs;
            results1 = [];
            for (k = 0, len2 = ref3.length; k < len2; k++) {
              config = ref3[k];
              if (config.images.indexOf(image.name + '.qcow2') > -1) {
                results1.push(image.used_in.push(config.file.split('.').slice(-1)[0]));
              } else {
                results1.push(void 0);
              }
            }
            return results1;
          })());
        }
        return results;
      });
    });
    $http.get('/api/lmn/linbo4/examples/config').then(function(resp) {
      return $scope.examples = resp.data;
    });
    $scope.importDevices = function() {
      $uibModal.open({
        templateUrl: '/lmn_linbo4:resources/partial/apply.modal.html',
        controller: 'LMImportDevicesApplyModalController',
        size: 'lg',
        backdrop: 'static'
      });
      return $scope.config_change = false;
    };
    $scope.createConfig = function(example) {
      return messagebox.prompt('New name', '').then(function(msg) {
        var config, i, len, newName, ref, test;
        newName = msg.value;
        test = validation.isValidLinboConf(newName);
        if (test !== true) {
          notify.error(gettext(test));
          return;
        }
        if (newName) {
          ref = $scope.configs;
          for (i = 0, len = ref.length; i < len; i++) {
            config = ref[i];
            if ("start.conf." + newName === config.file) {
              notify.error(gettext('A config file with this name already exists!'));
              return;
            }
          }
          if (example) {
            return $http.get(`/api/lmn/linbo4/config/examples/${example}`).then(function(resp) {
              resp.data['config']['LINBO']['Group'] = newName;
              return $http.get("/api/lmn/read-config-setup").then(function(setup) {
                resp.data['config']['LINBO']['Server'] = setup.data['setup']['serverip'];
                return $http.post(`/api/lmn/linbo4/config/start.conf.${newName}`, resp.data).then(function() {
                  $scope.config_change = true;
                  return $scope.configs.push({
                    'file': "start.conf." + newName,
                    'images': []
                  });
                });
              });
            });
          } else {
            return $http.post(`/api/lmn/linbo4/config/start.conf.${newName}`, {
              config: {
                LINBO: {
                  Group: newName
                }
              },
              os: [],
              partitions: []
            }).then(function() {
              $scope.config_change = true;
              return $scope.configs.push({
                'file': "start.conf." + newName,
                'images': []
              });
            });
          }
        }
      });
    };
    $scope.deleteConfig = function(configName) {
      return messagebox.show({
        title: `Delete '${configName}' ?`,
        text: `Delete the file '${configName}'? This will also delete the associated grub config file located in /srv/linbo/boot/grub.`,
        positive: 'Delete',
        negative: 'Cancel'
      }).then(function() {
        return $http.delete(`/api/lmn/linbo4/config/${configName}`).then(function() {
          var config, i, index, len, ref;
          $scope.config_change = true;
          ref = $scope.configs;
          for (index = i = 0, len = ref.length; i < len; index = ++i) {
            config = ref[index];
            if (configName === config.file) {
              $scope.configs.splice(index, 1);
              return;
            }
          }
        });
      });
    };
    $scope.duplicateConfig = function(configName, deleteOriginal = false) {
      var newName;
      newName = configName.substring('start.conf.'.length);
      return messagebox.prompt('New name', newName).then(function(msg) {
        newName = msg.value;
        if (newName) {
          return $http.get(`/api/lmn/linbo4/config/${configName}`).then(function(resp) {
            resp.data.config.LINBO.Group = newName;
            return $http.post(`/api/lmn/linbo4/config/start.conf.${newName}`, resp.data).then(function() {
              var config, i, index, len, newConfig, ref, results;
              if (deleteOriginal) {
                $http.delete(`/api/lmn/linbo4/config/${configName}`).then(function() {
                  return $scope.config_change = true;
                });
              } else {
                $scope.config_change = true;
              }
              ref = $scope.configs;
              results = [];
              for (index = i = 0, len = ref.length; i < len; index = ++i) {
                config = ref[index];
                if (configName === config.file) {
                  newConfig = angular.copy(config);
                  newConfig.file = `start.conf.${newName}`;
                  results.push($scope.configs.push(newConfig));
                } else {
                  results.push(void 0);
                }
              }
              return results;
            });
          });
        }
      });
    };
    $scope.showBackups = function(image) {
      return $uibModal.open({
        templateUrl: '/lmn_linbo4:resources/partial/image.backups.modal.html',
        controller: 'LMLINBO4BackupsModalController',
        scope: $scope,
        size: 'lg',
        resolve: {
          image: function() {
            return image;
          }
        }
      });
    };
    $scope.editConfig = function(configName) {
      return $http.get(`/api/lmn/linbo4/config/${configName}`).then(function(resp) {
        var config;
        config = resp.data;
        return $http.get(`/api/lmn/linbo4/vdi/${configName}.vdi`).then(function(resp) {
          var vdiconfig;
          vdiconfig = resp.data;
          return $uibModal.open({
            templateUrl: '/lmn_linbo4:resources/partial/config.modal.html',
            controller: 'LMLINBO4ConfigModalController',
            size: 'lg',
            resolve: {
              config: function() {
                return config;
              },
              vdiconfig: function() {
                return vdiconfig;
              }
            }
          }).result.then(function(result) {
            // result = [config, vdiconfig, config_change]
            // Config changed ?
            if (result[2] === true) {
              $http.post(`/api/lmn/linbo4/config/${configName}`, result[0]).then(function(resp) {
                notify.success(`${configName} ` + gettext('saved'));
                return $scope.config_change = true;
              });
            }
            return $http.post(`/api/lmn/linbo4/vdi/${configName}.vdi`, result[1]).then(function(resp) {
              return notify.success(gettext('VDI config saved'));
            });
          });
        });
      });
    };
    $scope.restartServices = function() {
      // Restart torrent and multicast services and redirect to images tab
      toaster.pop('info', gettext("Restarting multicast and torrent services, please wait ..."), '', 7000);
      return $http.get('/api/lmn/linbo4/restart-services').then(function(resp) {
        notify.success(gettext('Multicast and torrent services restarted'));
        $location.hash("images");
        return $route.reload();
      }).catch(function(err) {
        return notify.error(gettext("Failed to restart multicast and torrent services. Please see the log files"));
      });
    };
    $scope.deleteImage = function(image) {
      return messagebox.show({
        text: `Delete the full image '${image.name}'?`,
        positive: 'Delete',
        negative: 'Cancel'
      }).then(function() {
        return $http.delete(`/api/lmn/linbo4/images/${image.name}`).then(function() {
          $scope.restartServices();
          return $location.hash("images");
        }).catch(function(err) {
          return notify.error(gettext("Failed to delete image :") + err.data.message);
        });
      });
    };
    $scope.deleteBackupImage = function(image, date) {
      return messagebox.show({
        text: `Delete the backup '${image.name}'?`,
        positive: 'Delete',
        negative: 'Cancel'
      }).then(function() {
        return $http.post(`/api/lmn/linbo4/deleteBackupImage/${image.name}`, {
          date: date
        }).then(function() {
          return $scope.restartServices();
        }).catch(function(err) {
          return notify.error(gettext("Failed to delete backup :") + err.data.message);
        });
      });
    };
    $scope.deleteDiffImage = function(image) {
      return messagebox.show({
        text: `Delete '${image.name}' differential image?`,
        positive: 'Delete',
        negative: 'Cancel'
      }).then(function() {
        return $http.delete(`/api/lmn/linbo4/deleteDiffImage/${image.name}`).then(function() {
          return $scope.restartServices();
        }).catch(function(err) {
          return notify.error(gettext("Failed to delete backup :") + err.data.message);
        });
      });
    };
    $scope.deleteImages = function() {
      var image, name_list;
      name_list = ((function() {
        var i, len, ref, results;
        ref = $scope.images_selected;
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
          image = ref[i];
          results.push(image.name);
        }
        return results;
      })()).toString();
      return messagebox.show({
        text: `Delete '${name_list}'?`,
        positive: 'Delete',
        negative: 'Cancel'
      }).then(function() {
        var i, len, promises, ref;
        promises = [];
        ref = $scope.images_selected;
        for (i = 0, len = ref.length; i < len; i++) {
          image = ref[i];
          promises.push($http.delete(`/api/lmn/linbo4/images/${image.name}`));
        }
        return $q.all(promises).then(function() {
          $scope.restartServices();
          return $location.hash("images");
        }).catch(function(err) {
          return notify.error(gettext("Failed to delete image :") + err.data.message);
        });
      });
    };
    $scope.toggleSelected = function(image) {
      var position;
      position = $scope.images_selected.indexOf(image);
      if (position > -1) {
        return $scope.images_selected.splice(position, 1);
      } else {
        return $scope.images_selected.push(image);
      }
    };
    $scope.renameImage = function(image) {
      return messagebox.prompt('New name', image.name).then(function(msg) {
        var new_name, validName;
        new_name = msg.value;
        validName = validation.isValidImage(new_name);
        if (validName === true) {
          return $http.post(`/api/lmn/linbo4/renameImage/${image.name}`, {
            new_name: new_name
          }).then(function(resp) {
            return $scope.restartServices();
          });
        } else {
          return notify.error(gettext(new_name + " is not a valid name for a linbo image."));
        }
      });
    };
    $scope.restoreBackup = function(image, date) {
      return messagebox.show({
        text: `Do you really want to restore the backup at '${date}'? This will move the actual image to a backup.`,
        positive: 'Restore',
        negative: 'Cancel'
      }).then(function() {
        return $http.post(`/api/lmn/linbo4/restoreBackupImage/${image.name}`, {
          date: date
        }).then(function(resp) {
          return $scope.restartServices();
        }).catch(function(err) {
          return notify.error(gettext("Failed to restore backup! ") + err.data.message);
        });
      });
    };
    $scope.editImage = function(image) {
      return $uibModal.open({
        templateUrl: '/lmn_linbo4:resources/partial/image.modal.html',
        controller: 'LMLINBO4ImageModalController',
        scope: $scope,
        resolve: {
          image: function() {
            return angular.copy(image);
          },
          images: function() {
            return $scope.images;
          }
        }
      }).result.then(function(result) {
        angular.copy(result, image);
        if (image.backup) {
          return $http.post(`/api/lmn/linbo4/saveBackupImage/${image.name}`, {
            data: result,
            timestamp: image.timestamp
          }).then(function(resp) {
            notify.success(gettext('Backup saved'));
            return $scope.restartServices();
          });
        } else {
          return $http.post(`/api/lmn/linbo4/images/${image.name}`, {
            data: result,
            diff: image.diff
          }).then(function(resp) {
            notify.success(gettext('Saved'));
            return $scope.restartServices();
          });
        }
      });
    };
    return $scope.downloadIso = function() {
      return location.href = '/lmn/download/linbo.iso';
    };
  });

}).call(this);

