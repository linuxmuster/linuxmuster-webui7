angular.module('lm.common').service 'validation', () ->

    this.externVar = {}

    # Filter specific value from dict
    this.findval = (attr, val) ->
        return (dict) ->
            dict[attr] == val

    # User passwords must contain at least one lower, one upper,
    # one digit or special char, and more than 7 chars 
    this.isStrongPwd = (password) ->
        regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/
        validPassword = regExp.test(password)
        return validPassword

    # Valid chars for user passwords
    this.validCharPwd = (password) ->
        regExp = /^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$/
        validPassword = regExp.test(password)
        return validPassword

    # Test both valid chars and strong password
    this.isValidPassword = (password) ->
        return this.validCharPwd(password) && this.isStrongPwd(password)

    # Project names can only have lowercase and digits
    this.isValidProjectName = (name) ->
        regExp =  /^[a-z0-9]*$/
        validName = regExp.test(name)
        return validName

    # Config names can only have alphanumeric chars ( lowercase or uppercase )
    this.isValidAlphaNum = (name) ->
        regExp =  /^[a-z0-9]*$/i
        validName = regExp.test(name)
        return validName

    # Valid number ( number of course for extra-course )
    this.isValidCount = (count) ->
        regExp = /^([0-9]*)$/
        validCount = regExp.test(count)
        return validCount

    # Test a valid date
    # Not perfect : allows 31.02.1920, but not so important
    # Does not test if student birthday is in correct range
    this.isValidDate = (date) ->
        regExp = /^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)\d\d$/
        validDate = regExp.test(date)
        return validDate

    # Regexp for mac address, and tests if no duplicate
    this.isValidMac = (mac) ->
        regExp = /^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$/
        validMac = regExp.test(mac) && (this.externVar['devices'].filter(this.findval('mac', mac)).length < 2)
        return validMac

    # Regexp for ip address, and tests if no duplicate
    this.isValidIP = (ip) ->
        regExp = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/ ## TODO all IPs allowed, and 010.1.1.1
        validIP = regExp.test(ip) && (this.externVar['devices'].filter(this.findval('ip', ip)).length < 2)
        return validIP

    # Hostnames not empty, only with alphanumeric chars and "-", and tests if no duplicate
    this.isValidHost =(hostname) ->
        regExp = /^[a-zA-Z0-9\-]+$/
        validHostname = regExp.test(hostname) && (this.externVar['devices'].filter(this.findval('hostname', hostname)).length < 2)
        return validHostname;

    # Roomnames same as hostnames
    this.isValidRoom =(room) ->
        return this.isValidHost(room);

    # List of valid sophomorix roles
    this.isValidRole =(role) -> 
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
        return validRole.indexOf(role) != -1

    # Get local $scope var from controller
    this.set = (data, name) ->
        this.externVar[name] = data

    return this
