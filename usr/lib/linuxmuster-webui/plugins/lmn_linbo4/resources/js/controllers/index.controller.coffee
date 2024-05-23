angular.module('lmn.linbo4').config ($routeProvider) ->
    $routeProvider.when '/view/lmn/linbo4',
        controller: 'LMLINBO4Controller'
        templateUrl: '/lmn_linbo4:resources/partial/index.html'

angular.module('lmn.linbo4').controller 'LMImportDevicesApplyModalController', ($scope, $http, $uibModalInstance, $route, gettext, notify) ->
    $scope.logVisible = true
    $scope.isWorking = true
    $scope.showLog = () ->
        $scope.logVisible = !$scope.logVisible

    $http.post('/api/lmn/devices/import').then (resp) ->
        $scope.isWorking = false
        notify.success gettext('Import complete')
    .catch (resp) ->
        notify.error gettext('Import failed'), resp.data.message
        $scope.isWorking = false
        $scope.showLog()

    $scope.close = () ->
        $uibModalInstance.close()
        $route.reload()

angular.module('lmn.linbo4').controller 'LMLINBO4AcceptModalController', ($scope, $uibModalInstance, $http, partition, disk) ->
    $scope.partition = partition
    $scope.disk = disk

    $scope.save = () ->
        $uibModalInstance.close(response: 'accept')

    $scope.close = () ->
        $uibModalInstance.dismiss()

angular.module('lmn.linbo4').controller 'LMLINBO4PartitionModalController', ($scope, $uibModalInstance, $http, partition, messagebox, os) ->
    $scope.partition = partition
    $scope.os = os

    $http.get('/api/lmn/linbo4/icons').then (resp) ->
        $scope.icons = resp.data
        $scope.image_extension = 'svg'
        $scope.show_png_warning = false
        if $scope.os != null
            if $scope.os.IconName.endsWith('png')
                $scope.show_png_warning = true

    $http.get('/api/lmn/linbo4/images').then (resp) ->
        $scope.images = []
        oses = resp.data
        for os in oses
            $scope.images.push os.name + '.qcow2'
        if $scope.os != null
            if $scope.images.indexOf($scope.os.BaseImage) < 0
                $scope.images.push $scope.os.BaseImage

    $scope.addNewImage = () ->
       messagebox.prompt('New image name', '').then (msg) ->
            $scope.images.push(msg.value)

    $scope.save = () ->
        $uibModalInstance.close(partition: $scope.partition, os: $scope.os)

    $scope.close = () ->
        $uibModalInstance.dismiss()


angular.module('lmn.linbo4').controller 'LMLINBO4BackupsModalController', ($scope, $uibModal, $uibModalInstance, $http, gettext, messagebox, image) ->
    $scope.image = image

    $scope.close = () ->
        $uibModalInstance.dismiss()

angular.module('lmn.linbo4').controller 'LMLINBO4ImageModalController', ($scope, $uibModal, $uibModalInstance, $http, gettext, filesystem, messagebox, image, images) ->
    $scope.image = image
    console.log(image)
    $scope.desc_textarea_rows = if $scope.image.desc then $scope.image.desc.split(/\r\n|\r|\n/).length + 1 else 1
    $scope.info_textarea_rows = if $scope.image.info then $scope.image.info.split(/\r\n|\r|\n/).length + 1 else 1
    $scope.imagesWithReg = (x for x in images when x.reg)
    $scope.imagesWithPostsync = (x for x in images when x.postsync)
    $scope.imagesWithPrestart = (x for x in images when x.prestart)

    $http.get('/api/lmn/linbo4/examples/reg').then (resp) ->
        $scope.exampleRegs = resp.data

    $scope.setExampleReg = (name) ->
        filesystem.read("/srv/linbo/examples/#{name}").then (content) ->
            $scope.image.reg = content

    $http.get('/api/lmn/linbo4/examples/postsync').then (resp) ->
        $scope.examplePostsyncs = resp.data

    $http.get('/api/lmn/linbo4/examples/prestart').then (resp) ->
        $scope.examplePrestarts = resp.data

    $scope.setExamplePostsync = (name) ->
        filesystem.read("/srv/linbo/examples/#{name}").then (content) ->
            $scope.image.postsync = content

    $scope.setExamplePrestart = (name) ->
        filesystem.read("/srv/linbo/examples/#{name}").then (content) ->
            $scope.image.prestart = content

    $scope.save = () ->
        $uibModalInstance.close(image)

    $scope.close = () ->
        $uibModalInstance.dismiss()


angular.module('lmn.linbo4').controller 'LMLINBO4ConfigModalController', ($scope, $uibModal, $uibModalInstance, $timeout, $http, $log, gettext, messagebox, config, lmFileBackups, identity, vdiconfig) ->
    $scope.config = config
    $scope.vdiconfig = vdiconfig
    $scope.expert = false
    $scope.privateConf = false

    if  'School' of config.config.LINBO
        if config.config.LINBO.School != 'default-school'
            $scope.privateConf = true

    $scope.togglePrivateConf = () ->
        if $scope.privateConf
            $scope.privateConf = false
            config.config.LINBO.School = 'default-school'
        else
            $scope.privateConf = true
            config.config.LINBO.School = $scope.identity.profile.activeSchool 

    $scope.toggleExpert = () ->
        if $scope.expert
            $scope.expert = false
        else
            $scope.expert = true

    if $scope.config.config.LINBO.BackgroundColor
       $scope.config.config.LINBO.BackgroundColor = '#' + $scope.config.config.LINBO.BackgroundColor

    $scope.kernelOptions = [
        'quiet'
        'splash'
        'acpi=noirq'
        'acpi=off'
        'irqpoll'
        'dhcpretry=9'
    ]

    $scope.colors = [
        'white'
        'black'
        'lightCyan'
        'cyan'
        'darkCyan'
        'orange'
        'red'
        'darkRed'
        'pink'
        'magenta'
        'darkMagenta'
        'lightGreen'
        'green'
        'darkGreen'
        'lightYellow'
        'yellow'
        'gold'
        'lightBlue'
        'blue'
        'darkBlue'
        'lightGray'
        'gray'
        'darkGray'
    ]

    $scope.disks = []

    diskMap = {}

    $http.get('/api/lmn/linbo4/images').then (resp) ->
        $scope.oses = resp.data

    for _partition in $scope.config.partitions
        # Determine the position of the partition integer.
        # Different devices have it on a different position
        if _partition['Dev'].indexOf("nvme") != -1
            _device = _partition.Dev.substring(0, '/dev/nvme0n1p'.length)
        if _partition['Dev'].indexOf("mmcblk") != -1
            _device = _partition.Dev.substring(0, '/dev/mmcblk0p'.length)
        if _partition['Dev'].indexOf("sd") != -1
            _device = _partition.Dev.substring(0, '/dev/sdX'.length)

        if not diskMap[_device]
            if _device.indexOf("sd") != -1
                DiskType = 'sata'
            if _device.indexOf("mmcblk") != -1
                DiskType = 'mmc'
            if _device.indexOf("nvme") != -1
                DiskType = 'nvme'
            diskMap[_device] = {
                name: _device
                partitions: []
                DiskType: DiskType
            }
            $scope.disks.push diskMap[_device]
        diskMap[_device].partitions.push _partition
        _partition._isCache = _partition.Dev == $scope.config.config.LINBO.Cache

    $scope.config_backup = angular.copy($scope.config)

    for disk in $scope.disks
        disk.partitions.sort (a, b) -> if a.Dev > b.Dev then 1 else -1

    $scope.getAllInfo = () ->
    $scope.updateDiskType = (disk) ->
        oldDiskName = disk.name
        newDiskType = disk.DiskType

        if newDiskType  == 'sata'
            disk.name = 'a'
            while true
                if diskMap["/dev/sd#{disk.name}"]
                    disk.name = String.fromCharCode(disk.name.charCodeAt(0) + 1)
                    continue
                break
            disk.name = "/dev/sd#{disk.name}"

        if newDiskType == 'mmc'
            disk.name = '0'
            while true
                if diskMap["/dev/mmcblk#{disk.name}p"]
                    disk.name = String.fromCharCode(disk.name.charCodeAt(0) + 1)
                    continue
                break
            disk.name = "/dev/mmcblk#{disk.name}p"

        if newDiskType == 'nvme'
            disk.name = '0'
            while true
                if diskMap["/dev/nvme#{disk.name}n1p"]
                    disk.name = String.fromCharCode(disk.name.charCodeAt(0) + 1)
                    continue
                break
            disk.name = "/dev/nvme#{disk.name}n1p"

        #diskMap
        $scope.rebuildDisks()
        # create new object with the actual diskname
        diskMap[disk.name] = disk

        # remove the old diskname
        delete diskMap[oldDiskName]


    $scope.addDisk = () ->
        disk = 'a'
        while true
            if diskMap["/dev/sd#{disk}"]
                disk = String.fromCharCode(disk.charCodeAt(0) + 1)
                continue
            break
        disk = "/dev/sd#{disk}"

        diskMap[disk] = {
            name: disk
            partitions: []
            DiskType: 'sata'
        }
        $scope.disks.push diskMap[disk]

    $scope.removeDisk = (disk) ->
        delete diskMap[disk.name]
        $scope.disks.remove(disk)

    $scope.getSize = (partition) ->
        if not partition.Size or not partition.Size.toLowerCase
            return
        ps = partition.Size.toLowerCase()
        s = parseInt(ps) * 1024
        if ps[ps.length - 1] == 'm'
            s *= 1024
        if ps[ps.length - 1] == 'g'
            s *= 1024 * 1024
        if ps[ps.length - 1] == 't'
            s *= 1024 * 1024 * 1024
        return s

    $scope.isSwapPartition = (partition) ->
        return partition.FSType == 'swap'

    $scope.isCachePartition = (partition) ->
        return partition.Dev == $scope.config.config.LINBO.Cache

    $scope.getOS = (partition) ->
        for os in $scope.config.os
            if os.Root == partition.Dev
                return os
        return null

    $scope.getName = (partition) ->
        if $scope.getOS(partition) and $scope.getOS(partition).Name
            return $scope.getOS(partition).Name
        if partition.Label
            return partition.Label
        if $scope.isSwapPartition(partition)
            return gettext('Swap')
        if partition._isCache
            return gettext('LINBO Cache')
        if partition.Id == 'ef'
            return 'EFI'
        if partition.Id == '0c01'
            return 'MSR'
        if partition.Label
            return partition.Label
        return 'Partition'

    $scope.addSwap = (disk) ->
        disk.partitions.push {
            Bootable: false
            FSType: 'swap'
            Id: '82'
            Size: '4G'
            Label: ''
        }
        $scope.rebuildDisks()

    $scope.addData = (disk) ->
        disk.partitions.push {
            Bootable: false
            FSType: 'ntfs'
            Id: '7'
            Size: '10G'
            Label: ''
        }
        $scope.rebuildDisks()

    $scope.addEFI = (disk) ->
        disk.partitions.splice 0, 0, {
            Bootable: true
            FSType: 'vfat'
            Id: 'ef'
            Size: 1024 * 200
            Label: ''
        }
        $scope.rebuildDisks()

    $scope.addMSR = (disk) ->
        disk.partitions.splice 1, 0, {
            Bootable: false
            FSType: ''
            Id: '0c01'
            Size: 1024 * 128
            Label: ''
        }
        $scope.rebuildDisks()

    $scope.addExtended = (disk) ->
        disk.partitions.push {
            Bootable: false
            FSType: ''
            Id: '5'
            Size: ''
            Label: ''
        }
        $scope.rebuildDisks()

    $scope.addCache = (disk) ->
        disk.partitions.push {
            Bootable: yes
            FSType: 'ext4'
            Id: '83'
            Size: ''
            Label: ''
            _isCache: true
        }
        $scope.rebuildDisks()

    $scope.addWindows = (disk) ->
        partition = {
            Bootable: yes
            FSType: 'ntfs'
            Id: '7'
            Size: '40G'
            Label: ''
        }
        disk.partitions.push partition
        $scope.rebuildDisks()
        $scope.config.os.push {
            Name: 'Windows 10'
            Version: ''
            Description: 'Windows 10'
            IconName: 'win10.' + $scope.image_extension
            Image: ''
            BaseImage: ''
            Root: partition.Dev
            Boot: partition.Dev
            Kernel: 'auto'
            Initrd: ''
            Append: ''
            StartEnabled: true
            SyncEnabled: true
            NewEnabled: true
            Hidden: true
            Autostart: false
            AutostartTimeout: 5
            DefaultAction: 'sync'
        }

    $scope.addLinux = (disk) ->
        partition = {
            Bootable: yes
            FSType: 'ext4'
            Id: '83'
            Size: '20G'
            Label: ''
        }
        disk.partitions.push partition
        $scope.rebuildDisks()
        $scope.config.os.push {
            Name: 'Ubuntu'
            Version: ''
            Description: 'Ubuntu 16.04'
            IconName: 'ubuntu.' + $scope.image_extension
            Image: ''
            BaseImage: ''
            Root: partition.Dev
            Boot: partition.Dev
            Kernel: 'vmlinuz'
            Initrd: 'initrd.img'
            Append: 'ro splash'
            StartEnabled: true
            SyncEnabled: true
            NewEnabled: true
            Hidden: true
            Autostart: false
            AutostartTimeout: 5
            DefaultAction: 'sync'
        }


    $scope.removePartition = (partition, disk) ->
        $uibModal.open(
            templateUrl: '/lmn_linbo4:resources/partial/accept.modal.html'
            controller: 'LMLINBO4AcceptModalController'
            resolve:
                partition: () -> angular.copy(partition.Dev)
                disk: () -> angular.copy(disk)
        ).result.then (result) ->
            if result.response is 'accept'
                disk.partitions.remove(partition)
                $scope.rebuildDisks()


    $scope.rebuildDisks = () ->
        remap = {}
        for disk in $scope.disks
            partitionIndex = 1
            for partition in disk.partitions
                newDev = "#{disk.name}#{partitionIndex}"
                if partition.Dev
                    remap[partition.Dev] = newDev
                partition.Dev = newDev
                partitionIndex++

                if partition._isCache
                    $scope.config.config.LINBO.Cache = partition.Dev

        $log.log 'Remapping OSes', remap

        for os in $scope.config.os
            if os.Boot
                os.Boot = remap[os.Boot]
            if os.Root
                os.Root = remap[os.Root]

    $scope.getBorderColor = (partition) ->
        if $scope.isCachePartition(partition)
            return '#F3E000'
        if $scope.isSwapPartition(partition)
            return '#E09305'
        if partition.Id == 'ef'
            return '#737373'
        if partition.Id == '0c01'
            return '#737373'
        if $scope.getOS(partition)
            return '#3232B7'
        return '#58B158'

    $scope.addKernelOption = (option) ->
        $scope.config.config.LINBO.KernelOptions += ' ' + option

    $scope.editPartition = (partition) ->
        os = $scope.getOS(partition)
        $uibModal.open(
            templateUrl: '/lmn_linbo4:resources/partial/partition.modal.html'
            controller: 'LMLINBO4PartitionModalController'
            resolve:
                partition: () -> angular.copy(partition)
                os: () -> angular.copy(os)
        ).result.then (result) ->
            angular.copy(result.partition, partition)
            if os
                angular.copy(result.os, os)
            $scope.rebuildDisks()

    $scope.addVDIMasterVMID = (vmid) ->
        $scope.vdiconfig["vmids"].push(vmid)

    $scope.removeVDIMasterVMID = (index) ->
        $scope.vdiconfig["vmids"].splice(index, 1)


    $scope.save = () ->
        $scope.config.partitions = []
        for disk in $scope.disks
            for partition in disk.partitions
                $scope.config.partitions.push partition

        config_change = !angular.equals(angular.toJson($scope.config), angular.toJson($scope.config_backup))

	    # Remove # from background color
        if $scope.config.config.LINBO.BackgroundColor
            $scope.config.config.LINBO.BackgroundColor = $scope.config.config.LINBO.BackgroundColor.substring(1)

        $uibModalInstance.close([$scope.config, $scope.vdiconfig, config_change])

    $scope.backups = () ->
        lmFileBackups.show('/srv/linbo/start.conf.' + $scope.config.config.LINBO.Group).then () ->
            $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()



angular.module('lmn.linbo4').controller 'LMLINBO4Controller', ($q, $scope, $http, $uibModal, $log, $route, $location, gettext, notify, pageTitle, tasks, messagebox, validation, toaster, identity) ->
    pageTitle.set(gettext('LINBO 4'))

    $scope.tabs = ['groups', 'images']
    $scope.config_change = false

    tag = $location.$$url.split("#")[1]
    if tag and tag in $scope.tabs
        $scope.activetab = $scope.tabs.indexOf(tag)
    else
        $scope.activetab = 0

    $scope.images_selected = []

    $scope.$on("$locationChangeStart", (event) ->
        if ($scope.config_change && !confirm(gettext('You should call an import devices process to apply the new changes, quit this page anyway ?')))
            event.preventDefault()
    )

    $http.get('/api/lmn/linbo4/configs').then (resp) ->
        allConfigNames = resp.data
        $scope.configs = []
        for configName in allConfigNames
            if  'School' not of configName.settings || configName.settings.School in [identity.profile.activeSchool, 'default-school']
                $scope.configs.push configName

        $http.get('/api/lmn/linbo4/images').then (resp) ->
            $scope.images = resp.data
            for image in $scope.images
                image.backups_list = []
                for date,backup of image.backups
                    backup.date = date
                    image.backups_list.push(backup)
                image.used_in = []
                for config in $scope.configs
                    if config.images.indexOf(image.name + '.qcow2') > -1
                            image.used_in.push(config.file.split('.').slice(-1)[0])

    $http.get('/api/lmn/linbo4/examples/config').then (resp) ->
        $scope.examples = resp.data

    $scope.importDevices = () ->
        $uibModal.open(
            templateUrl: '/lmn_linbo4:resources/partial/apply.modal.html'
            controller: 'LMImportDevicesApplyModalController'
            size: 'lg'

            backdrop: 'static'
        )
        $scope.config_change = false

    $scope.createConfig = (example) ->
        messagebox.prompt('New name', '').then (msg) ->
            newName = msg.value
            test = validation.isValidLinboConf(newName)
            if test != true
                notify.error gettext(test)
                return
            if newName
                for config in $scope.configs
                    if "start.conf."+newName == config.file
                        notify.error gettext('A config file with this name already exists!')
                        return
                if example
                    $http.get("/api/lmn/linbo4/config/examples/#{example}").then (resp) ->
                        resp.data['config']['LINBO']['Group'] = newName
                        $http.get("/api/lmn/read-config-setup").then (setup) ->
                            resp.data['config']['LINBO']['Server'] = setup.data['setup']['serverip']
                            $http.post("/api/lmn/linbo4/config/start.conf.#{newName}", resp.data).then () ->
                                $scope.config_change = true
                                $scope.configs.push({'file': "start.conf."+newName, 'images':[]})
                else
                    $http.post("/api/lmn/linbo4/config/start.conf.#{newName}", {
                        config:
                            LINBO:
                                Group: newName
                        os: []
                        partitions: []
                    }).then () ->
                        $scope.config_change = true
                        $scope.configs.push({'file': "start.conf."+newName, 'images':[]})

    $scope.deleteConfig = (configName) ->
        messagebox.show(
            title: "Delete '#{configName}' ?",
            text: "Delete the file '#{configName}'? This will also delete the associated grub config file located in /srv/linbo/boot/grub.",
            positive: 'Delete', negative: 'Cancel'
        ).then () ->
            $http.delete("/api/lmn/linbo4/config/#{configName}").then () ->
                $scope.config_change = true
                for config, index in $scope.configs
                    if configName == config.file
                        $scope.configs.splice(index, 1)
                        return

    $scope.duplicateConfig = (configName, deleteOriginal=false) ->
        newName = configName.substring('start.conf.'.length)
        messagebox.prompt('New name', newName).then (msg) ->
            newName = msg.value
            if newName
                $http.get("/api/lmn/linbo4/config/#{configName}").then (resp) ->
                    resp.data.config.LINBO.Group = newName
                    $http.post("/api/lmn/linbo4/config/start.conf.#{newName}", resp.data).then () ->
                        if deleteOriginal
                            $http.delete("/api/lmn/linbo4/config/#{configName}").then () ->
                                $scope.config_change = true
                        else
                            $scope.config_change = true
                        for config, index in $scope.configs
                            if configName == config.file
                                newConfig = angular.copy(config)
                                newConfig.file = "start.conf.#{newName}"
                                $scope.configs.push(newConfig)

    $scope.showBackups = (image) ->
        $uibModal.open(
            templateUrl: '/lmn_linbo4:resources/partial/image.backups.modal.html'
            controller: 'LMLINBO4BackupsModalController'
            scope: $scope
            size: 'lg'
            resolve:
                image: () -> image
        )

    $scope.editConfig = (configName) ->
        $http.get("/api/lmn/linbo4/config/#{configName}").then (resp) ->
            config = resp.data
            $http.get("/api/lmn/linbo4/vdi/#{configName}.vdi").then (resp) ->
                vdiconfig = resp.data

                $uibModal.open(
                    templateUrl: '/lmn_linbo4:resources/partial/config.modal.html'
                    controller: 'LMLINBO4ConfigModalController'
                    size: 'lg'
                    resolve:
                        config: () -> config
                        vdiconfig:() -> vdiconfig
                ).result.then (result) ->
                    # result = [config, vdiconfig, config_change]
                    # Config changed ?
                    if result[2] == true
                        $http.post("/api/lmn/linbo4/config/#{configName}", result[0]).then (resp) ->
                            notify.success("#{configName} " + gettext('saved'))
                            $scope.config_change = true
                    $http.post("/api/lmn/linbo4/vdi/#{configName}.vdi", result[1]).then (resp) ->
                        notify.success((gettext('VDI config saved')))


    $scope.restartServices = () ->
        # Restart torrent and multicast services and redirect to images tab
        toaster.pop('info', gettext("Restarting multicast and torrent services, please wait ..."), '', 7000)
        $http.get('/api/lmn/linbo4/restart-services').then (resp) ->
            notify.success(gettext('Multicast and torrent services restarted'))
            $location.hash("images")
            $route.reload()
        .catch (err) ->
            notify.error(gettext("Failed to restart multicast and torrent services. Please see the log files"))

    $scope.deleteImage = (image) ->
        messagebox.show(text: "Delete the full image '#{image.name}'?", positive: 'Delete', negative: 'Cancel').then () ->
            $http.delete("/api/lmn/linbo4/images/#{image.name}").then () ->
                $scope.restartServices()
                $location.hash("images")
            .catch (err) ->
                notify.error(gettext("Failed to delete image :") + err.data.message)

    $scope.deleteBackupImage = (image, date) ->
        messagebox.show(text: "Delete the backup '#{image.name}'?", positive: 'Delete', negative: 'Cancel').then () ->
            $http.post("/api/lmn/linbo4/deleteBackupImage/#{image.name}", {date: date}).then () ->
                $scope.restartServices()
            .catch (err) ->
                notify.error(gettext("Failed to delete backup :") + err.data.message)

    $scope.deleteDiffImage = (image) ->
        messagebox.show(text: "Delete '#{image.name}' differential image?", positive: 'Delete', negative: 'Cancel').then () ->
            $http.delete("/api/lmn/linbo4/deleteDiffImage/#{image.name}").then () ->
                $scope.restartServices()
            .catch (err) ->
                notify.error(gettext("Failed to delete backup :") + err.data.message)

    $scope.deleteImages = () ->
        name_list = (image.name for image in $scope.images_selected).toString()
        messagebox.show(text: "Delete '#{name_list}'?", positive: 'Delete', negative: 'Cancel').then () ->
            promises = []
            for image in $scope.images_selected
                promises.push($http.delete("/api/lmn/linbo4/images/#{image.name}"))
            $q.all(promises).then () ->
                $scope.restartServices()
                $location.hash("images")
            .catch (err) ->
                notify.error(gettext("Failed to delete image :") + err.data.message)

    $scope.toggleSelected = (image) ->
        position = $scope.images_selected.indexOf(image)
        if position > -1
            $scope.images_selected.splice(position, 1)
        else
            $scope.images_selected.push(image)

    $scope.renameImage = (image) ->
       messagebox.prompt('New name', image.name).then (msg) ->
            new_name = msg.value
            validName = validation.isValidImage(new_name)
            if validName == true
                $http.post("/api/lmn/linbo4/renameImage/#{image.name}", {new_name:new_name}).then (resp) ->
                    $scope.restartServices()
            else
                notify.error(gettext(new_name + " is not a valid name for a linbo image."))

    $scope.duplicateImage = (image) ->
        messagebox.prompt('New name', image.name).then (msg) ->
            new_name = msg.value
            validName = validation.isValidImage(new_name)
            if validName == true
                $http.post("/api/lmn/linbo4/duplicateImage/#{image.name}", {new_name:new_name}).then (resp) ->
                    $scope.restartServices()
            else
                notify.error(gettext(new_name + " is not a valid name for a linbo image."))

    $scope.restoreBackup = (image, date) ->
        messagebox.show(text: "Do you really want to restore the backup at '#{date}'? This will move the actual image to a backup.", positive: 'Restore', negative: 'Cancel').then () ->
            $http.post("/api/lmn/linbo4/restoreBackupImage/#{image.name}", {date: date}).then (resp) ->
                $scope.restartServices()
            .catch (err) ->
                notify.error(gettext("Failed to restore backup! ") + err.data.message)

    $scope.editImage = (image) ->
        $uibModal.open(
            templateUrl: '/lmn_linbo4:resources/partial/image.modal.html'
            controller: 'LMLINBO4ImageModalController'
            scope: $scope
            resolve:
                image: () -> angular.copy(image)
                images: () -> $scope.images
        ).result.then (result) ->
            angular.copy(result, image)
            if image.backup
                $http.post("/api/lmn/linbo4/saveBackupImage/#{image.name}", {data: result, timestamp:image.timestamp}).then (resp) ->
                    notify.success gettext('Backup saved')
                    $scope.restartServices()
            else
                $http.post("/api/lmn/linbo4/images/#{image.name}", {data: result, diff: image.diff}).then (resp) ->
                    notify.success gettext('Saved')
                    $scope.restartServices()

    $scope.downloadIso = () ->
        location.href = '/lmn/download/linbo.iso'
