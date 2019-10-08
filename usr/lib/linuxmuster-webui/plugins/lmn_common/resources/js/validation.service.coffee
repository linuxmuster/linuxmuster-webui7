angular.module('lm.common').service 'validation', (gettext) ->

    this.externVar = {}

    # Filter specific value from dict
    this.findval = (attr, val) ->
        return (dict) ->
            dict[attr] == val

    # User passwords must contain at least one lower, one upper,
    # one digit or special char, and more than 7 chars 
    this.isStrongPwd = (password) ->
        error_msg = password + gettext(' must contain at least one lowercase, one uppercase, one special char or number, and at least 7 chars')
        regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/
        validPassword = regExp.test(password)
        if !validPassword
            return error_msg
        return true

    # Valid chars for user passwords
    this.validCharPwd = (password) ->
        error_msg = password + gettext(' is not valid. Password can only contains a-zA-Z0-9!@#§+\-$%&*{}()\]\[')
        regExp = /^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$/
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
        regExp =  /^[a-z0-9]*$/
        validName = regExp.test(name)
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
        regExp = /^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)\d\d$/
        validDate = regExp.test(date)
        if !validDate
            return error_msg
        return true

    # Regexp for mac address, and tests if no duplicate
    this.isValidMac = (mac) ->
        error_msg = mac + gettext(' is not valid or duplicated')
        regExp = /^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$/
        validMac = regExp.test(mac) && (this.externVar['devices'].filter(this.findval('mac', mac)).length < 2)
        if !validMac
            return error_msg
        return true

    # Regexp for ip address, and tests if no duplicate
    this.isValidIP = (ip) ->
        error_msg = ip + gettext(' is not valid or duplicated')
        regExp = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/ ## TODO all IPs allowed, and 010.1.1.1
        validIP = regExp.test(ip) && (this.externVar['devices'].filter(this.findval('ip', ip)).length < 2)
        if !validIP
            return error_msg
        return true

    # Hostnames not empty, only with alphanumeric chars and "-", and tests if no duplicate
    this.isValidHost =(hostname) ->
        error_msg = hostname + gettext(' does not contain valid chars or is duplicated')
        regExp = /^[a-zA-Z0-9\-]+$/
        validHostname = regExp.test(hostname) && (this.externVar['devices'].filter(this.findval('hostname', hostname)).length < 2)
        if !validHostname
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

    # Get local $scope var from controller
    this.set = (data, name) ->
        this.externVar[name] = data

    return this
