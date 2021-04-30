// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common', ['core', 'ajenti.ace', 'ajenti.filesystem']);

  angular.module('lm.common').run(function(customization) {
    customization.plugins.core.startupURL = '/view/lmn/landingpage';
    customization.plugins.core.loginredir = '/';
    // customization.plugins.core.bodyClass = 'customized'
    customization.plugins.core.title = ' ';
    customization.plugins.core.faviconURL = '/resources/lmn_common/resources/img/favicon.png';
    customization.plugins.core.logoURL = '/resources/lmn_common/resources/img/logo-text-white.png';
    customization.plugins.core.bigLogoURL = '/resources/lmn_common/resources/img/logo-full.png';
    customization.plugins.core.hidePersonaLogin = true;
    return customization.plugins.core.enableMixpanel = false;
  });

  angular.module('lm.common').constant('lmEncodingMap', {
    '': 'utf-8',
    'ascii': 'ascii',
    'utf8': 'utf-8',
    '8859-1': 'ISO8859-1',
    '8859-15': 'ISO8859-15',
    'win1252': 'cp1252'
  });

  $(function() {
    return $('body').addClass('customized');
  });

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common').directive('lmLog', function($http, $interval, $timeout) {
    return {
      restrict: 'E',
      scope: {
        path: '=',
        lines: '=?'
      },
      template: `<pre style="max-height: 300px; overflow-y: scroll" ng:bind="visibleContent"></pre>
<div class="form-group">
   <label translate>Options</label>
      <br>
         <span checkbox ng:model="autoscroll" text="{{'Autoscroll'|translate}}"></span>
         </div>
         {{options}}
         `,
      link: function($scope, element) {
        var i;
        $scope.content = '';
        $scope.autoscroll = true;
        i = $interval(function() {
          return $http.get(`/api/lm/log${$scope.path}?offset=${$scope.content.length}`).then(function(resp) {
            var lines;
            // console.log ($scope)
            $scope.content += resp.data;
            $scope.visibleContent = $scope.content;
            if ($scope.lines) {
              lines = $scope.content.split('\n');
              // console.log lines, lines[lines.length - 1]
              if (lines[lines.length - 1] === '') {
                lines = lines.slice(0, -1);
              }
              lines = lines.slice(-$scope.lines);
              // console.log lines
              $scope.visibleContent = lines.join('\n');
            }
            if ($scope.autoscroll) {
              return $timeout(function() {
                var e;
                e = $(element).find('pre')[0];
                return e.scrollTop = e.scrollHeight;
              });
            }
          });
        }, 1000);
        return $scope.$on('$destroy', function() {
          return $interval.cancel(i);
        });
      }
    };
  });

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common').directive('lmDragUpload', function($http, notify, messagebox, filesystem, gettext) {
    return {
      restrict: 'E',
      scope: {
        uploadpath: '=',
        refresh: '=',
        subdir: '=?',
        movetohome: '=?',
        owner: '=?',
        group: '=?'
      },
      replace: true,
      template: function(attrs) {
        var target;
        if (!attrs.target) {
          target = "'/api/filesystem/upload'";
        } else {
          target = attrs.target;
        }
        return `<div> <div    flow-init=\"{target: ${target}, chunkSize: 1024 * 1024, singleFile: true}\" flow-files-submitted=\"onUploadBegin($flow)\" flow-drag-enter=\"class='dragdroparea-enter'\" flow-drag-leave=\"class='dragdroparea'\" ng-style=\"style\"> <div class=\"dragdroparea\" flow-drop  ng-class=\"class\"> <span class=\"btn btn-default\" flow-btn translate>Upload file</span> <span translate> or drag And Drop your file here</span> </div> </div> </div>`;
      },
      link: function($scope, attrs) {
        return $scope.onUploadBegin = function($flow) {
          var msg;
          msg = messagebox.show({
            progress: true
          });
          return filesystem.startFlowUpload($flow, $scope.uploadpath).then(function() {
            var filename, filepath;
            if ($scope.owner && $scope.group) {
              filename = $flow.files[0].name;
              filepath = $scope.uploadpath + filename;
              $http.post('/api/lm/chown', {
                filepath: $scope.uploadpath + $flow.files[0].name,
                owner: $scope.owner,
                group: $scope.group
              }).then(function() {
                if ($scope.movetohome) {
                  return $http.post('/api/lmn/session/moveFileToHome', {
                    user: $scope.owner,
                    filepath: $scope.uploadpath,
                    subdir: $scope.subdir
                  }).then(function(resp) {
                    console.log('return');
                    console.log(resp.data);
                    return $http.post('/api/lm/remove-file', {
                      filepath: filepath
                    }).then(function() {
                      notify.success(gettext('Uploaded'));
                      return $scope.refresh();
                    });
                  });
                }
              });
            } else {
              notify.success(gettext('Uploaded'));
            }
            $scope.refresh();
            return msg.close();
          }, null, function(progress) {
            return msg.messagebox.title = 'Uploading: ' + Math.floor(100 * progress) + ' %';
          });
        };
      }
    };
  });

  angular.module('lm.common').directive('lmSelectUpload', function($http, notify, messagebox, filesystem, gettext) {
    return {
      restrict: 'E',
      scope: {
        uploadpath: '=',
        refresh: '=',
        subdir: '=?',
        movetohome: '=?',
        owner: '=?',
        group: '=?'
      },
      template: function(attrs) {
        var target;
        if (!attrs.target) {
          target = "'/api/filesystem/upload'";
        } else {
          target = attrs.target;
        }
        return `<div> <div    flow-init=\"{target: ${target}, chunkSize: 1024 * 1024, singleFile: true}\" flow-files-submitted=\"onUploadBegin($flow)\" ng-style=\"style\"> <input type=\"file\" flow-btn/> </div> </div>`;
      },
      link: function($scope) {
        return $scope.onUploadBegin = function($flow) {
          var msg;
          msg = messagebox.show({
            progress: true
          });
          return filesystem.startFlowUpload($flow, $scope.uploadpath).then(function() {
            var filename, filepath;
            if ($scope.owner && $scope.group) {
              filename = $flow.files[0].name;
              filepath = $scope.uploadpath + filename;
              $http.post('/api/lm/chown', {
                filepath: $scope.uploadpath + $flow.files[0].name,
                owner: $scope.owner,
                group: $scope.group
              }).then(function() {
                if ($scope.movetohome) {
                  return $http.post('/api/lmn/session/moveFileToHome', {
                    user: $scope.owner,
                    filepath: $scope.uploadpath,
                    subdir: $scope.subdir
                  }).then(function(resp) {
                    return $http.post('/api/lm/remove-file', {
                      filepath: filepath
                    }).then(function() {
                      notify.success(gettext('Uploaded'));
                      return $scope.refresh();
                    });
                  });
                }
              });
            } else {
              notify.success(gettext('Uploaded'));
            }
            $scope.refresh();
            return msg.close();
          }, null, function(progress) {
            return msg.messagebox.title = 'Uploading: ' + Math.floor(100 * progress) + ' %';
          });
        };
      }
    };
  });

  angular.module('lm.common').directive('lmButtonUpload', function($http, notify, messagebox, filesystem, gettext) {
    return {
      restrict: 'E',
      scope: {
        uploadpath: '=',
        btnlabel: '=',
        refresh: '=',
        subdir: '=?',
        movetohome: '=?',
        owner: '=?',
        group: '=?'
      },
      template: function(attrs) {
        var target;
        if (!attrs.target) {
          target = "'/api/filesystem/upload'";
        } else {
          target = attrs.target;
        }
        return `<div> <div    flow-init=\"{target: ${target}, chunkSize: 1024 * 1024, singleFile: true}\" flow-files-submitted=\"onUploadBegin($flow)\" ng-style=\"style\"> <span type=\"file\" flow-btn translate>{{btnlabel}}</span> </div> </div>`;
      },
      link: function($scope) {
        return $scope.onUploadBegin = function($flow) {
          var msg;
          msg = messagebox.show({
            progress: true
          });
          return filesystem.startFlowUpload($flow, $scope.uploadpath).then(function() {
            var filename, filepath;
            if ($scope.owner && $scope.group) {
              filename = $flow.files[0].name;
              filepath = $scope.uploadpath + filename;
              $http.post('/api/lm/chown', {
                filepath: $scope.uploadpath + $flow.files[0].name,
                owner: $scope.owner,
                group: $scope.group
              }).then(function() {
                if ($scope.movetohome) {
                  return $http.post('/api/lmn/session/moveFileToHome', {
                    user: $scope.owner,
                    filepath: $scope.uploadpath,
                    subdir: $scope.subdir
                  }).then(function(resp) {
                    return $http.post('/api/lm/remove-file', {
                      filepath: filepath
                    }).then(function() {
                      notify.success(gettext('Uploaded'));
                      return $scope.refresh();
                    });
                  });
                }
              });
            } else {
              notify.success(gettext('Uploaded'));
            }
            $scope.refresh();
            return msg.close();
          }, null, function(progress) {
            return msg.messagebox.title = 'Uploading: ' + Math.floor(100 * progress) + ' %';
          });
        };
      }
    };
  });

  /* Examples in templates :

    <lm-drag-upload uploadpath="'/srv/'"></lm-drag-upload>
    <lm-button-upload uploadpath="'/root/'" btnlabel="'Upload SSH KEYS'"></lm-button-upload>
    <lm-select-upload uploadpath="'/home/toto'"></lm-select-upload>
*/
// TODO handle multiple files
// TODO test translations

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common').service('lmFileEditor', function($uibModal) {
    this.show = function(path, encoding) {
      return $uibModal.open({
        templateUrl: '/lmn_common:resources/js/lmFileEditor.modal.html',
        controller: 'lmFileEditorModalController',
        size: 'lg',
        resolve: {
          path: function() {
            return path;
          },
          encoding: function() {
            return encoding;
          }
        }
      }).result;
    };
    return this;
  });

  angular.module('lm.common').controller('lmFileEditorModalController', function($scope, $uibModalInstance, $timeout, filesystem, path, encoding) {
    $scope.path = path;
    filesystem.read(path, encoding).then(function(data) {
      return $scope.content = data;
    });
    $scope.save = function() {
      return filesystem.write(path, $scope.content, encoding).then(function() {
        return $uibModalInstance.close($scope.content);
      });
    };
    $scope.cancel = function() {
      return $uibModalInstance.dismiss();
    };
    $timeout(function() {
      var dropZone;
      dropZone = $('.lm-file-editor-drop-target')[0];
      dropZone.addEventListener('dragover', function(e) {
        e.stopPropagation();
        e.preventDefault();
        return e.dataTransfer.dropEffect = 'copy';
      });
      return dropZone.addEventListener('drop', function(e) {
        var file, files, i, len, results;
        e.stopPropagation();
        e.preventDefault();
        files = e.dataTransfer.files;
        results = [];
        for (i = 0, len = files.length; i < len; i++) {
          file = files[i];
          results.push((function(file) {
            var reader;
            reader = new FileReader();
            reader.onload = function(e) {
              return $scope.$apply(function() {
                return $scope.content = e.target.result;
              });
            };
            return reader.readAsText(file, encoding);
          })(file));
        }
        return results;
      });
    });
    return $scope.download = function() {
      var tokens;
      tokens = path.split('/');
      return filesystem.downloadBlob($scope.content, 'text/csv', tokens[tokens.length - 1]);
    };
  });

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common').service('validation', function(gettext) {
    this.externVar = {};
    // Filter specific value from dict
    this.findval = function(attr, val) {
      return function(dict) {
        return dict[attr] === val;
      };
    };
    // User passwords must contain at least one lower, one upper,
    // one digit or special char, and more than 7 chars 
    this.isStrongPwd = function(password) {
      var error_msg, regExp, validPassword;
      error_msg = gettext('Passwords must contain at least one lowercase, one uppercase, one special char or number, and at least 7 chars');
      regExp = /(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%&*()]|(?=.*\d)).{7,}/;
      validPassword = regExp.test(password);
      if (!validPassword) {
        return error_msg;
      }
      return true;
    };
    // Valid chars for user passwords
    this.validCharPwd = function(password) {
      var error_msg, regExp, validPassword;
      error_msg = gettext('Password is not valid. Password can only contains a-zA-Z0-9!@#§+\-$%&*{}()\]\[');
      regExp = /^[a-zA-Z0-9!@#§+\-$%&*{}()\]\[]+$/;
      validPassword = regExp.test(password);
      if (!validPassword) {
        return error_msg;
      }
      return true;
    };
    // Test both valid chars and strong password
    this.isValidPassword = function(password) {
      var strong, valid;
      valid = this.validCharPwd(password);
      strong = this.isStrongPwd(password);
      if ((valid === true) && (strong === true)) {
        return true;
      } else if (strong !== true) {
        return strong;
      } else {
        return valid;
      }
    };
    // Project names can only have lowercase and digits
    this.isValidProjectName = function(name) {
      var error_msg, regExp, validName;
      error_msg = name + gettext(' can only contain lowercase chars or numbers');
      regExp = /^[a-z0-9]*$/;
      validName = regExp.test(name);
      if (!validName) {
        return error_msg;
      }
      return true;
    };
    // Linbo start.conf names or group names can only have alphanumeric chars ( lowercase or uppercase ) or _+-
    this.isValidLinboConf = function(name) {
      var error_msg, regExp, validName;
      error_msg = name + gettext(' can only contain alphanumeric chars or _+-');
      regExp = /^[a-z0-9\+\-_]*$/i;
      validName = regExp.test(name);
      if (!validName) {
        return error_msg;
      }
      return true;
    };
    // Login can only have alphanumeric chars ( lowercase or uppercase ) or -
    this.isValidLogin = function(name) {
      var error_msg, regExp, validName;
      error_msg = name + gettext(' can only contain alphanumeric chars or -');
      regExp = /^[a-z0-9\-]*$/i;
      validName = regExp.test(name);
      if (!validName) {
        return error_msg;
      }
      return true;
    };
    // Comments can only have alphanumeric chars ( lowercase or uppercase ) or -, space and _
    this.isValidComment = function(comment) {
      var error_msg, regExp, validName;
      error_msg = comment + gettext(' can only contain alphanumeric chars or -, space and _');
      regExp = /^[a-z0-9\-_ ]*$/i;
      validName = regExp.test(comment);
      if (!validName) {
        return error_msg;
      }
      return true;
    };
    // Config names can only have alphanumeric chars ( lowercase or uppercase )
    this.isValidAlphaNum = function(name) {
      var error_msg, regExp, validName;
      error_msg = name + gettext(' can only contain alphanumeric chars');
      regExp = /^[a-z0-9]*$/i;
      validName = regExp.test(name);
      if (!validName) {
        return error_msg;
      }
      return true;
    };
    // Valid number ( number of course for extra-course )
    this.isValidCount = function(count) {
      var error_msg, regExp, validCount;
      error_msg = count + gettext(' is not a valid number');
      regExp = /^([0-9]*)$/;
      validCount = regExp.test(count);
      if (!validCount) {
        return error_msg;
      }
      return true;
    };
    // Test a valid date
    // Not perfect : allows 31.02.1920, but not so important
    // Does not test if student birthday is in correct range
    this.isValidDate = function(date) {
      var error_msg, regExp, validDate;
      error_msg = date + gettext(' is not a valid date');
      regExp = /^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)\d\d$/;
      validDate = regExp.test(date);
      if (!validDate) {
        return error_msg;
      }
      return true;
    };
    // Regexp for mac address, and tests if no duplicate
    this.isValidMac = function(mac, idx) {
      var error_msg, regExp, regExp2, regExp3, validMac;
      // idx is the position of the mac address in devices
      error_msg = mac + gettext(' is not valid or duplicated');
      // Allow ':', '-' or nothing as separator
      regExp = /^([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})$/;
      regExp2 = /^([0-9A-Fa-f]{2}[-]){5}([0-9A-Fa-f]{2})$/;
      regExp3 = /^[0-9A-Fa-f]{12}$/;
      validMac = false;
      // Convert mac address if necessary
      if (regExp.test(mac)) {
        validMac = true;
      } else if (regExp2.test(mac)) {
        validMac = true;
        mac = mac.replaceAll('-', ':');
        this.externVar['devices'][idx]['mac'] = mac;
      } else if (regExp3.test(mac)) {
        validMac = true;
        mac = mac.match(/.{1,2}/g).join(':');
        this.externVar['devices'][idx]['mac'] = mac;
      }
      validMac = validMac && (this.externVar['devices'].filter(this.findval('mac', mac)).length < 2);
      if (!validMac) {
        return error_msg;
      }
      return true;
    };
    // Regexp for ip address, and tests if no duplicate
    this.isValidIP = function(ip) {
      var error_msg, regExp, validIP;
      error_msg = ip + gettext(' is not valid or duplicated');
      regExp = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/; //# TODO all IPs allowed, and 010.1.1.1
      validIP = regExp.test(ip) && (this.externVar['devices'].filter(this.findval('ip', ip)).length < 2);
      if (!validIP) {
        return error_msg;
      }
      return true;
    };
    // Hostnames not empty, only with alphanumeric chars and "-", and tests if no duplicate
    this.isValidHost = function(hostname) {
      var error_msg, regExp, validHostname;
      error_msg = hostname + gettext(' does not contain valid chars or is duplicated');
      regExp = /^[a-zA-Z0-9\-]+$/;
      validHostname = regExp.test(hostname) && (this.externVar['devices'].filter(this.findval('hostname', hostname)).length < 2);
      if (!validHostname) {
        return error_msg;
      }
      return true;
    };
    // Roomnames same as hostnames
    this.isValidRoom = function(room) {
      return this.isValidHost(room);
    };
    // List of valid sophomorix roles
    this.isValidRole = function(role) {
      var error_msg, validRole;
      error_msg = role + gettext(' is not a valid role');
      validRole = ['switch', 'addc', 'wlan', 'staffcomputer', 'mobile', 'printer', 'classroom-teachercomputer', 'server', 'iponly', 'faculty-teachercomputer', 'voip', 'byod', 'classroom-studentcomputer', 'thinclient', 'router'];
      if (validRole.indexOf(role) === -1) {
        return error_msg;
      }
      return true;
    };
    // Get local $scope var from controller
    this.set = function(data, name) {
      return this.externVar[name] = data;
    };
    return this;
  });

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common').controller('lmWaitController', function($scope, $rootScope, $uibModalInstance, status, style) {
    $scope.status = status;
    $scope.style = style;
    return $rootScope.$on('updateWaiting', function(event, data) {
      if (data === 'done') {
        return $uibModalInstance.dismiss();
      }
    });
  });

  angular.module('lm.common').service('wait', function($uibModal) {
    this.modal = function(status, style) {
      return $uibModal.open({
        template: `<div class=\"modal-header\">
    <h4 translate>{{status}}</h4>
</div>

<div class=\"modal-body\">
    <div ng:show=\"style == 'spinner'\"><progress-spinner></progress-spinner></div>
    <div ng:show=\"style == 'progressbar'\">
        <uib-progressbar style=\"height: 10px;\" type=\"warning\" max=\"100\" value=\"100 * value / max\" ng:class=\"{indeterminate: !max}\">
    </uib-progressbar>
    </div>
</div>`,
        controller: 'lmWaitController',
        backdrop: 'static',
        keyboard: false,
        size: 'mg',
        resolve: {
          status: function() {
            return status;
          },
          style: function() {
            return style;
          }
        }
      });
    };
    return this;
  });

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common').service('sophComment', function(gettext) {
    this.sophomorixCommentsKeys = {
      "ADDUSER": gettext("Adding user %s."),
      "UPDATEUSER": gettext("Updating user %s."),
      "KILLUSER": gettext("Deleting user %s."),
      "ADDEXAMUSER": gettext("Adding examuser %s."),
      "KILLEXAMUSER": gettext("Deleting examuser %s."),
      "ADDCOMPUTER": gettext("Adding computer %s."),
      "KILLCOMPUTER": gettext("Deleting computer %s."),
      "COLLECTCOPY": gettext("Collecting data (copy): %s."),
      "COLLECTMOVE": gettext("Collecting data (move): %s."),
      "MPUTFILES": gettext("Copying files to user %s."),
      "SCOPY_FILES": gettext("Copying files: %s.")
    };
    //# Use in controller (gettext must be done in frontend):
    // gettext(sophComment.get("ADDUSER")).replace(/%s/, value)
    this.get = function(key) {
      if (key in this.sophomorixCommentsKeys) {
        return this.sophomorixCommentsKeys[key];
      } else {
        return '';
      }
    };
    return this;
  });

}).call(this);

// Generated by CoffeeScript 2.5.1
(function() {
  angular.module('lm.common').service('lmFileBackups', function($uibModal) {
    this.show = function(path, encoding) {
      return $uibModal.open({
        templateUrl: '/lmn_common:resources/js/lmFileBackups.modal.html',
        controller: 'lmFileBackupsModalController',
        resolve: {
          path: function() {
            return path;
          },
          encoding: function() {
            return encoding;
          }
        }
      }).result;
    };
    return this;
  });

  angular.module('lm.common').controller('lmFileBackupsModalController', function($scope, $uibModalInstance, $route, $http, gettext, notify, filesystem, path, encoding, messagebox, lmFileBackups) {
    var dir, name;
    $scope.path = path;
    dir = path.substring(0, path.lastIndexOf('/'));
    name = path.substring(path.lastIndexOf('/') + 1);
    $scope.loadBackupFiles = function() {
      return filesystem.list(dir).then(function(data) {
        var i, item, len, ref, results, tokens;
        $scope.backups = [];
        ref = data.items;
        results = [];
        for (i = 0, len = ref.length; i < len; i++) {
          item = ref[i];
          if (item.name.startsWith('.' + name + '.bak.')) {
            tokens = item.name.split('.');
            results.push($scope.backups.push({
              name: item.name,
              date: new Date(1000 * parseInt(tokens[tokens.length - 1]))
            }));
          } else {
            results.push(void 0);
          }
        }
        return results;
      });
    };
    $scope.loadBackupFiles();
    $scope.restore = function(backup) {
      return filesystem.read(dir + '/' + backup.name, encoding).then(function(content) {
        return filesystem.write(path, content, encoding).then(function() {
          $scope.onlyremove(backup);
          notify.success('Backup file restored');
          $uibModalInstance.close();
          return $route.reload();
        });
      });
    };
    $scope.findbackup = function(name) {
      return function(dict) {
        return dict.name === name;
      };
    };
    $scope.onlyremove = function(backup) {
      return $http.post('/api/lm/remove-file', {
        filepath: dir + '/' + backup.name
      }).then(function(resp) {
        var pos;
        pos = $scope.backups.findIndex($scope.findbackup(backup.name));
        return delete $scope.backups[pos];
      });
    };
    $scope.removeUI = function(backup) {
      var content;
      $uibModalInstance.close();
      content = gettext('Do you really want to delete') + backup.name + ' ?';
      return messagebox.show({
        title: gettext('Confirmation'),
        text: content,
        positive: 'OK',
        negative: gettext('Cancel')
      }).then(function() {
        $scope.onlyremove(backup);
        notify.success('Backup file removed');
        return lmFileBackups.show($scope.path);
      });
    };
    return $scope.cancel = function() {
      return $uibModalInstance.dismiss();
    };
  });

}).call(this);

'use strict';

angular.module('lm.common').directive('messageboxContainer2', function (messagebox) {
    return {
        restrict: 'E',
        template: '\n            <dialog "ng:show="message.visible" style="z-index: 1050" ng:repeat="message in messagebox.messages">\n                <div class="modal-header">\n                    <h4>{{message.title|translate}}</h4>\n                </div>\n                <div class="modal-body" ng:class="{scrollable: message.scrollable}">\n                    <div ng:show="message.progress">\n                        <progress-spinner></progress-spinner>\n                    </div>\n                    {{message.text|translate}}\n                    <ng:include ng:if="message.template" src="message.template"></ng:include>\n                    <div ng:show="message.prompt">\n                        <label>{{message.prompt}}</label>\n                        <input type="text" ng:model="message.value" ng:enter="doPositive(message)" class="form-control" autofocus />\n                    </div>\n                </div>\n                <div class="modal-footer">\n                    <a ng:click="doPositive(message)" ng:show="message.positive" class="positive btn btn-default btn-flat">{{message.positive|translate}}</a>\n                    <a ng:click="doNegative(message)" ng:show="message.negative" class="negative btn btn-default btn-flat">{{message.negative|translate}}</a>\n                </div>\n            </dialog>',
        link: function link($scope, element, attrs) {
            $scope.messagebox = messagebox;

            $scope.doPositive = function (msg) {
                msg.q.resolve(msg);
                messagebox.close(msg);
            };

            $scope.doNegative = function (msg) {
                msg.q.reject(msg);
                messagebox.close(msg);
            };
        }
    };
});


