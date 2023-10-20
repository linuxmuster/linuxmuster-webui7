angular.module('lmn.common').service 'validation', (gettext) ->

    this.externVar = {}

    # Filter specific value from dict
    this.findval = (attr, val) ->
        return (dict) ->
            dict[attr] == val

    # User passwords must contain at least one lower, one upper,
    # one digit or special char, and more than 7 chars 
    this.isStrongPwd = (password) ->
        error_msg = gettext('Passwords must contain at least one lowercase, one uppercase, one special char or number, and at least 7 chars')
        regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[?!@#§+\-$%&*{}()]|(?=.*\d)).{7,}/
        validPassword = regExp.test(password)
        if !validPassword
            return error_msg
        return true

    # Valid chars for user passwords
    this.validCharPwd = (password) ->
        error_msg = gettext('Password is not valid. Password can only contains a-zA-Z0-9?!@#§+\-$%&*{}()\]\[')
        regExp = /^[a-zA-Z0-9?!@#§+\-$%&*{}()\]\[]+$/
        validPassword = regExp.test(password)
        if !validPassword
            return error_msg
        return true

    # Test both valid chars and strong password
    this.isValidPassword = (password) ->
        valid = this.validCharPwd(password)
        strong = this.isStrongPwd(password)
        if (valid == true) && (strong == true)
            return true
        else if (strong != true)
            return strong
        else
            return valid

    # Project names can only have lowercase and digits
    this.isValidProjectName = (name) ->
        error_msg = name + gettext(' can only contain lowercase chars or numbers')
        regExp =  /^[a-z0-9_\-]*$/
        validName = regExp.test(name)
        if !validName
            return error_msg
        return true

    # Linbo start.conf names or group names can only have alphanumeric chars ( lowercase or uppercase ) or _+-
    this.isValidLinboConf = (name) ->
        error_msg = name + gettext(' can only contain alphanumeric chars or _+-')
        regExp =  /^[a-z0-9\+\-_]*$/i
        validName = regExp.test(name)
        if !validName
            return error_msg
        return true

    # Login can only have alphanumeric chars ( lowercase or uppercase ) or -
    this.isValidLogin = (name) ->
        error_msg = name + gettext(' can only contain alphanumeric chars or -')
        regExp =  /^[a-z0-9\-_]*$/i
        validName = regExp.test(name)
        if !validName
            return error_msg
        return true

    # Comments can only have alphanumeric chars ( lowercase or uppercase ) or -, space and _
    this.isValidComment = (comment) ->
        error_msg = comment + gettext(' can only contain alphanumeric chars or -, space and _')
        regExp =  /^[a-z0-9\-_ ]*$/i
        validName = regExp.test(comment)
        if !validName
            return error_msg
        return true

    # Config names can only have alphanumeric chars ( lowercase or uppercase )
    this.isValidAlphaNum = (name) ->
        error_msg = name + gettext(' can only contain alphanumeric chars')
        regExp =  /^[a-z0-9]*$/i
        validName = regExp.test(name)
        if !validName
            return error_msg
        return true

    # Valid number ( number of course for extra-course )
    this.isValidCount = (count) ->
        error_msg = count + gettext(' is not a valid number')
        regExp = /^([0-9]*)$/
        validCount = regExp.test(count)
        if !validCount
            return error_msg
        return true

    # Test a valid date
    # Not perfect : allows 31.02.1920, but not so important
    # Does not test if student birthday is in correct range
    this.isValidDate = (date) ->
        error_msg = date + gettext(' is not a valid date')
        regExp = /^([1-9]|0[1-9]|[12][0-9]|3[01])[.]([1-9]|0[1-9]|1[012])[.](19|20)\d\d$/
        validDate = regExp.test(date)
        if !validDate
            return error_msg
        return true

    # Regexp for mac address, and tests if no duplicate
    this.isValidMac = (mac, idx) ->
        # idx is the position of the mac address in devices
        error_msg = mac + gettext(' is not valid or duplicated')
        # Allow ':', '-' or nothing as separator
        regExp  = /^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$/
        regExp2 = /^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$/
        regExp3 = /^[0-9A-Fa-f]{12}$/

        validMac = false

        # Convert mac address if necessary
        if regExp.test(mac)
            validMac = true
        else if regExp2.test(mac)
            validMac = true
            mac = mac.replaceAll('-', ':')
            this.externVar['devices'][idx]['mac'] = mac
        else if regExp3.test(mac)
            validMac = true
            mac = mac.match(/.{1,2}/g).join(':')
            this.externVar['devices'][idx]['mac'] = mac

        validMac = validMac && (this.externVar['devices'].filter(this.findval('mac', mac)).length < 2)

        if !validMac
            return error_msg
        return true

    # Regexp for ip address, and tests if no duplicate
    this.isValidIP = (ip) ->
        error_msg = ip + gettext(' is not valid or duplicated')
        regExp = /^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[1-9])$/
        validIP = regExp.test(ip) && (this.externVar['devices'].filter(this.findval('ip', ip)).length < 2)
        if !validIP
            return error_msg
        return true

    # Hostnames not empty, only with alphanumeric chars and "-", and tests if no duplicate
    this.isValidHost = (hostname, test_length = true) ->
        error_msg = hostname + gettext(' does not contain valid chars, is duplicated or too long (>15 chars)')
        regExp = /^[a-zA-Z0-9\-]+$/
        validHostname = regExp.test(hostname) && (this.externVar['devices'].filter(this.findval('hostname', hostname)).length < 2)
        if test_length
            validHostname = validHostname && hostname.length < 16
        if !validHostname
            return error_msg
        return true

    # Image names for linbo not empty, only with alphanumeric chars and "-" or "_"
    this.isValidImage = (name) ->
        error_msg = name + gettext(' does not contain valid chars or is duplicated')
        regExp = /^[a-zA-Z0-9_\-]+$/
        validImageName = regExp.test(name)
        if !validImageName
            return error_msg
        return true

    # Roomnames same as hostnames
    this.isValidRoom =(room) ->
        return this.isValidHost(room);

    # List of valid sophomorix roles
    this.isValidRole =(role) ->
        error_msg = role + gettext(' is not a valid role')
        validRole = [
            'switch',
            'addc',
            'wlan',
            'staffcomputer',
            'mobile',
            'printer',
            'classroom-teachercomputer',
            'server',
            'iponly',
            'faculty-teachercomputer',
            'voip',
            'byod',
            'classroom-studentcomputer',
            'thinclient',
            'router'
            ]
        if validRole.indexOf(role) == -1
            return error_msg
        return true

    this.isValidDomain = (domain) ->
        error_msg = domain + gettext(' is not a valid domain')
        regExp = /^[a-zA-Z0-9\-.]*$/
        validDomain = regExp.test(domain)
        if !validDomain
            return error_msg
        return true

    # Get local $scope var from controller
    this.set = (data, name) ->
        this.externVar[name] = data

    return this
