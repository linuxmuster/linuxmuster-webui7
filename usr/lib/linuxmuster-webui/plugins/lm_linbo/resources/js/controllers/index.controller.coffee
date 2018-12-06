isValidName = (name) ->
        regExp =  /^[a-z0-9]*$/i
        validName = regExp.test(name)
        return validName

angular.module('lm.linbo').config ($routeProvider) ->
    $routeProvider.when '/view/lm/linbo',
        controller: 'LMLINBOController'
        templateUrl: '/lm_linbo:resources/partial/index.html'


angular.module('lm.linbo').controller 'LMLINBOAcceptModalController', ($scope, $uibModalInstance, $http, partition, disk) ->
    $scope.partition = partition
    $scope.disk = disk

    $scope.save = () ->
        $uibModalInstance.close(response: 'accept')

    $scope.close = () ->
        $uibModalInstance.dismiss()

angular.module('lm.linbo').controller 'LMLINBOPartitionModalController', ($scope, $uibModalInstance, $http, partition, os) ->
    $scope.partition = partition
    $scope.os = os

    $http.get('/api/lm/linbo/icons').then (resp) ->
        $scope.icons = resp.data

    $http.get('/api/lm/linbo/images').then (resp) ->
        $scope.images = []
        $scope.diffImages = []
        oses = resp.data
        for os in oses
            if os.cloop
                $scope.images.push os.name
            if os.rsync
                $scope.diffImages.push os.name

    $scope.save = () ->
        $uibModalInstance.close(partition: $scope.partition, os: $scope.os)

    $scope.close = () ->
        $uibModalInstance.dismiss()


angular.module('lm.linbo').controller 'LMLINBOImageModalController', ($scope, $uibModal, $uibModalInstance, $http, gettext, filesystem, messagebox, image, images) ->
    $scope.image = image
    $scope.imagesWithReg = (x for x in images when x.reg)
    $scope.imagesWithPostsync = (x for x in images when x.postsync)

    $http.get('/api/lm/linbo/examples-regs').then (resp) ->
        $scope.exampleRegs = resp.data

    $scope.setExampleReg = (name) ->
        filesystem.read("/srv/linbo/examples/#{name}").then (content) ->
            $scope.image.reg = content

    $http.get('/api/lm/linbo/examples-postsyncs').then (resp) ->
        $scope.examplePostsyncs = resp.data

    $scope.setExamplePostsync = (name) ->
        filesystem.read("/srv/linbo/examples/#{name}").then (content) ->
            $scope.image.postsync = content

    $scope.save = () ->
        $uibModalInstance.close(image)

    $scope.close = () ->
        $uibModalInstance.dismiss()


angular.module('lm.linbo').controller 'LMLINBOConfigModalController', ($scope, $uibModal, $uibModalInstance, $timeout, $http, $log, gettext, messagebox, config, lmFileBackups) ->
    $scope.config = config

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
    console.log($scope.disks)

    $http.get('/api/lm/linbo/images').then (resp) ->
        $scope.oses = resp.data
        console.log($scope.disks)
        console.log(diskMap)

    for _partition in config.partitions
        # Determine the position of the partition integer.
        # Different devices have it on a different position
        if _partition['Dev'].indexOf("nvme") != -1
            _device = _partition.Dev.substring(0, '/dev/nvme0p'.length)
        if _partition['Dev'].indexOf("mmcblk") != -1
            _device = _partition.Dev.substring(0, '/dev/mmcblk0p'.length)
        if _partition['Dev'].indexOf("sd") != -1
            _device = _partition.Dev.substring(0, '/dev/sdX'.length)


        if not diskMap[_device]
            diskMap[_device] = {
                name: _device
                partitions: []
            }
            $scope.disks.push diskMap[_device]
        diskMap[_device].partitions.push _partition
        _partition._isCache = _partition.Dev == config.config.LINBO.Cache

    for disk in $scope.disks
        disk.partitions.sort (a, b) -> if a.Dev > b.Dev then 1 else -1


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
        return partition.Dev == config.config.LINBO.Cache

    $scope.getOS = (partition) ->
        for os in config.os
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
            IconName: 'win10.png'
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
            IconName: 'ubuntu.png'
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
            templateUrl: '/lm_linbo:resources/partial/accept.modal.html'
            controller: 'LMLINBOAcceptModalController'
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
                    config.config.LINBO.Cache = partition.Dev

        $log.log 'Remapping OSes', remap

        for os in config.os
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
            templateUrl: '/lm_linbo:resources/partial/partition.modal.html'
            controller: 'LMLINBOPartitionModalController'
            resolve:
                partition: () -> angular.copy(partition)
                os: () -> angular.copy(os)
        ).result.then (result) ->
            angular.copy(result.partition, partition)
            if os
                angular.copy(result.os, os)
            $scope.rebuildDisks()

    $scope.save = () ->
        config.partitions = []
        for disk in $scope.disks
            for partition in disk.partitions
                config.partitions.push partition
        $uibModalInstance.close(config)

    $scope.backups = () ->
        lmFileBackups.show('/srv/linbo/start.conf.' + $scope.config.config.LINBO.Group).then () ->
            $uibModalInstance.dismiss()

    $scope.close = () ->
        $uibModalInstance.dismiss()



angular.module('lm.linbo').controller 'LMLINBOController', ($scope, $http, $uibModal, $log, $route, gettext, notify, pageTitle, tasks, messagebox) ->
    pageTitle.set(gettext('LINBO'))

    $http.get('/api/lm/linbo/configs').then (resp) ->
        $scope.configs = resp.data

    $http.get('/api/lm/linbo/examples').then (resp) ->
        $scope.examples = resp.data

    $http.get('/api/lm/linbo/images').then (resp) ->
        $scope.images = resp.data

    $scope.createConfig = (example) ->
        messagebox.prompt('New name', '').then (msg) ->
            newName = msg.value
            if not isValidName(newName)
                notify.error gettext('Not a valid name! Only alphanumeric characters are allowed!')
                return
            if newName
                if example
                    $http.get("/api/lm/linbo/config/examples/#{example}").then (resp) ->
                        resp.data['config']['LINBO']['Group'] = newName
                        $http.post("/api/lm/linbo/config/start.conf.#{newName}", resp.data).then () ->
                            $route.reload()
                else
                    $http.post("/api/lm/linbo/config/start.conf.#{newName}", {
                        config:
                            LINBO:
                                Group: newName
                        os: []
                        partitions: []
                    }).then () ->
                        $route.reload()

    $scope.deleteConfig = (configName) ->
        messagebox.prompt(text: "Delete '#{configName}'?", positive: 'Delete', negative: 'Cancel').then () ->
            $http.delete("/api/lm/linbo/config/#{configName}").then () ->
                $route.reload()

    $scope.duplicateConfig = (configName) ->
        newName = configName.substring('start.conf.'.length)
        messagebox.prompt('New name', newName).then (msg) ->
            newName = msg.value
            if newName
                $http.get("/api/lm/linbo/config/#{configName}").then (resp) ->
                    resp.data.config.LINBO.Group = newName
                    $http.post("/api/lm/linbo/config/start.conf.#{newName}", resp.data).then () ->
                        $route.reload()

    $scope.editConfig = (configName) ->
        $http.get("/api/lm/linbo/config/#{configName}").then (resp) ->
            config = resp.data

            $uibModal.open(
                templateUrl: '/lm_linbo:resources/partial/config.modal.html'
                controller: 'LMLINBOConfigModalController'
                size: 'lg'
                resolve:
                    config: () -> config
            ).result.then (result) ->
                $http.post("/api/lm/linbo/config/#{configName}", result).then (resp) ->
                    notify.success gettext('Saved')

    $scope.deleteImage = (image) ->
        messagebox.show(text: "Delete '#{image.name}'?", positive: 'Delete', negative: 'Cancel').then () ->
            $http.delete("/api/lm/linbo/image/#{image.name}").then () ->
                $route.reload()

    $scope.duplicateImage = (image) ->
        messagebox.prompt('New name', image.name).then (msg) ->
            newName = msg.value
            if newName
                newFileName = newName
                if not newFileName.endsWith('.cloop') and not newFileName.endsWith('.rsync')
                    newFileName += if image.cloop then '.cloop' else '.rsync'
                tasks.start(
                    'aj.plugins.filesystem.tasks.Transfer',
                    [],
                    destination: "/srv/linbo/#{newFileName}",
                    items: [{
                        mode: 'copy'
                        item:
                            name: image.name
                            path: "/srv/linbo/#{image.name}"
                    }]
                )

                image = angular.copy(image)
                image.name = newFileName
                $http.post("/api/lm/linbo/image/#{image.name}", image).then () ->
                    $scope.images.push image

    $scope.editImage = (image) ->
        $uibModal.open(
            templateUrl: '/lm_linbo:resources/partial/image.modal.html'
            controller: 'LMLINBOImageModalController'
            resolve:
                image: () -> angular.copy(image)
                images: () -> $scope.images
        ).result.then (result) ->
            angular.copy(result, image)
            $http.post("/api/lm/linbo/image/#{image.name}", result).then (resp) ->
                notify.success gettext('Saved')
