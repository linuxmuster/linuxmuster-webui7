angular.module('lmn.common').service 'sophComment', (gettext) ->

    this.sophomorixCommentsKeys = {
            "ADDUSER" : gettext("Adding user %s."),
            "UPDATEUSER" : gettext("Updating user %s."),
            "KILLUSER" : gettext("Deleting user %s."),
            "ADDEXAMUSER" : gettext("Adding examuser %s."),
            "KILLEXAMUSER" : gettext("Deleting examuser %s."),
            "ADDCOMPUTER" : gettext("Adding computer %s."),
            "KILLCOMPUTER" : gettext("Deleting computer %s."),
            "COLLECTCOPY" : gettext("Collecting data (copy): %s."),
            "COLLECTMOVE" : gettext("Collecting data (move): %s."),
            "MPUTFILES" : gettext("Copying files to user %s."),
            "SCOPY_FILES" : gettext("Copying files: %s."),
        }

    ## Use in controller (gettext must be done in frontend):
    # gettext(sophComment.get("ADDUSER")).replace(/%s/, value)

    this.get = (key) ->
        if key of this.sophomorixCommentsKeys
            return this.sophomorixCommentsKeys[key]
        else
            return ''

    return this
