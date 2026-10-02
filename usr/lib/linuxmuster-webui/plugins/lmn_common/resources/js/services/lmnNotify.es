angular.module('lmn.common').service('lmnNotify', function(toaster) {
    // Unlike core notify, these toasts stay until the user closes them,
    // so long messages (e.g. password policy violations) can be read.

    this.permanent_error = (title, text) => {
        toaster.pop({
            type:'error',
            title: title,
            body: text,
            timeout: 0
        });
    }

    this.permanent_success = (title, text) => {
        toaster.pop({
            type:'success',
            title: title,
            body: text,
            timeout: 0
        });
    }
});
