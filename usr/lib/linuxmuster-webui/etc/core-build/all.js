"use strict";

Array.prototype.remove = function () {
    var output = [];

    for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
        args[_key] = arguments[_key];
    }

    for (var i = 0; i < args.length; i++) {
        var arg = args[i];
        var index = this.indexOf(arg);
        if (index !== -1) {
            output.push(this.splice(index, 1));
        }
    }
    if (args.length === 1) {
        output = output[0];
    }
    return output;
};

Array.prototype.contains = function (v) {
    return this.indexOf(v) > -1;
};

Array.prototype.toggleItem = function (v) {
    if (this.contains(v)) {
        this.remove(v);
    } else {
        this.push(v);
    }
};

String.prototype.lpad = function (padString, length) {
    var str = this;
    while (str.length < length) {
        str = padString + str;
    }
    return str;
};


(function (global) {
  var babelHelpers = global.babelHelpers = {};
  babelHelpers.typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) {
    return typeof obj;
  } : function (obj) {
    return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj;
  };

  babelHelpers.jsx = function () {
    var REACT_ELEMENT_TYPE = typeof Symbol === "function" && Symbol.for && Symbol.for("react.element") || 0xeac7;
    return function createRawReactElement(type, props, key, children) {
      var defaultProps = type && type.defaultProps;
      var childrenLength = arguments.length - 3;

      if (!props && childrenLength !== 0) {
        props = {};
      }

      if (props && defaultProps) {
        for (var propName in defaultProps) {
          if (props[propName] === void 0) {
            props[propName] = defaultProps[propName];
          }
        }
      } else if (!props) {
        props = defaultProps || {};
      }

      if (childrenLength === 1) {
        props.children = children;
      } else if (childrenLength > 1) {
        var childArray = Array(childrenLength);

        for (var i = 0; i < childrenLength; i++) {
          childArray[i] = arguments[i + 3];
        }

        props.children = childArray;
      }

      return {
        $$typeof: REACT_ELEMENT_TYPE,
        type: type,
        key: key === undefined ? null : '' + key,
        ref: null,
        props: props,
        _owner: null
      };
    };
  }();

  babelHelpers.asyncIterator = function (iterable) {
    if (typeof Symbol === "function") {
      if (Symbol.asyncIterator) {
        var method = iterable[Symbol.asyncIterator];
        if (method != null) return method.call(iterable);
      }

      if (Symbol.iterator) {
        return iterable[Symbol.iterator]();
      }
    }

    throw new TypeError("Object is not async iterable");
  };

  babelHelpers.asyncGenerator = function () {
    function AwaitValue(value) {
      this.value = value;
    }

    function AsyncGenerator(gen) {
      var front, back;

      function send(key, arg) {
        return new Promise(function (resolve, reject) {
          var request = {
            key: key,
            arg: arg,
            resolve: resolve,
            reject: reject,
            next: null
          };

          if (back) {
            back = back.next = request;
          } else {
            front = back = request;
            resume(key, arg);
          }
        });
      }

      function resume(key, arg) {
        try {
          var result = gen[key](arg);
          var value = result.value;

          if (value instanceof AwaitValue) {
            Promise.resolve(value.value).then(function (arg) {
              resume("next", arg);
            }, function (arg) {
              resume("throw", arg);
            });
          } else {
            settle(result.done ? "return" : "normal", result.value);
          }
        } catch (err) {
          settle("throw", err);
        }
      }

      function settle(type, value) {
        switch (type) {
          case "return":
            front.resolve({
              value: value,
              done: true
            });
            break;

          case "throw":
            front.reject(value);
            break;

          default:
            front.resolve({
              value: value,
              done: false
            });
            break;
        }

        front = front.next;

        if (front) {
          resume(front.key, front.arg);
        } else {
          back = null;
        }
      }

      this._invoke = send;

      if (typeof gen.return !== "function") {
        this.return = undefined;
      }
    }

    if (typeof Symbol === "function" && Symbol.asyncIterator) {
      AsyncGenerator.prototype[Symbol.asyncIterator] = function () {
        return this;
      };
    }

    AsyncGenerator.prototype.next = function (arg) {
      return this._invoke("next", arg);
    };

    AsyncGenerator.prototype.throw = function (arg) {
      return this._invoke("throw", arg);
    };

    AsyncGenerator.prototype.return = function (arg) {
      return this._invoke("return", arg);
    };

    return {
      wrap: function (fn) {
        return function () {
          return new AsyncGenerator(fn.apply(this, arguments));
        };
      },
      await: function (value) {
        return new AwaitValue(value);
      }
    };
  }();

  babelHelpers.asyncGeneratorDelegate = function (inner, awaitWrap) {
    var iter = {},
        waiting = false;

    function pump(key, value) {
      waiting = true;
      value = new Promise(function (resolve) {
        resolve(inner[key](value));
      });
      return {
        done: false,
        value: awaitWrap(value)
      };
    }

    ;

    if (typeof Symbol === "function" && Symbol.iterator) {
      iter[Symbol.iterator] = function () {
        return this;
      };
    }

    iter.next = function (value) {
      if (waiting) {
        waiting = false;
        return value;
      }

      return pump("next", value);
    };

    if (typeof inner.throw === "function") {
      iter.throw = function (value) {
        if (waiting) {
          waiting = false;
          throw value;
        }

        return pump("throw", value);
      };
    }

    if (typeof inner.return === "function") {
      iter.return = function (value) {
        return pump("return", value);
      };
    }

    return iter;
  };

  babelHelpers.asyncToGenerator = function (fn) {
    return function () {
      var gen = fn.apply(this, arguments);
      return new Promise(function (resolve, reject) {
        function step(key, arg) {
          try {
            var info = gen[key](arg);
            var value = info.value;
          } catch (error) {
            reject(error);
            return;
          }

          if (info.done) {
            resolve(value);
          } else {
            return Promise.resolve(value).then(function (value) {
              step("next", value);
            }, function (err) {
              step("throw", err);
            });
          }
        }

        return step("next");
      });
    };
  };

  babelHelpers.classCallCheck = function (instance, Constructor) {
    if (!(instance instanceof Constructor)) {
      throw new TypeError("Cannot call a class as a function");
    }
  };

  babelHelpers.createClass = function () {
    function defineProperties(target, props) {
      for (var i = 0; i < props.length; i++) {
        var descriptor = props[i];
        descriptor.enumerable = descriptor.enumerable || false;
        descriptor.configurable = true;
        if ("value" in descriptor) descriptor.writable = true;
        Object.defineProperty(target, descriptor.key, descriptor);
      }
    }

    return function (Constructor, protoProps, staticProps) {
      if (protoProps) defineProperties(Constructor.prototype, protoProps);
      if (staticProps) defineProperties(Constructor, staticProps);
      return Constructor;
    };
  }();

  babelHelpers.defineEnumerableProperties = function (obj, descs) {
    for (var key in descs) {
      var desc = descs[key];
      desc.configurable = desc.enumerable = true;
      if ("value" in desc) desc.writable = true;
      Object.defineProperty(obj, key, desc);
    }

    return obj;
  };

  babelHelpers.defaults = function (obj, defaults) {
    var keys = Object.getOwnPropertyNames(defaults);

    for (var i = 0; i < keys.length; i++) {
      var key = keys[i];
      var value = Object.getOwnPropertyDescriptor(defaults, key);

      if (value && value.configurable && obj[key] === undefined) {
        Object.defineProperty(obj, key, value);
      }
    }

    return obj;
  };

  babelHelpers.defineProperty = function (obj, key, value) {
    if (key in obj) {
      Object.defineProperty(obj, key, {
        value: value,
        enumerable: true,
        configurable: true,
        writable: true
      });
    } else {
      obj[key] = value;
    }

    return obj;
  };

  babelHelpers.extends = Object.assign || function (target) {
    for (var i = 1; i < arguments.length; i++) {
      var source = arguments[i];

      for (var key in source) {
        if (Object.prototype.hasOwnProperty.call(source, key)) {
          target[key] = source[key];
        }
      }
    }

    return target;
  };

  babelHelpers.get = function get(object, property, receiver) {
    if (object === null) object = Function.prototype;
    var desc = Object.getOwnPropertyDescriptor(object, property);

    if (desc === undefined) {
      var parent = Object.getPrototypeOf(object);

      if (parent === null) {
        return undefined;
      } else {
        return get(parent, property, receiver);
      }
    } else if ("value" in desc) {
      return desc.value;
    } else {
      var getter = desc.get;

      if (getter === undefined) {
        return undefined;
      }

      return getter.call(receiver);
    }
  };

  babelHelpers.inherits = function (subClass, superClass) {
    if (typeof superClass !== "function" && superClass !== null) {
      throw new TypeError("Super expression must either be null or a function, not " + typeof superClass);
    }

    subClass.prototype = Object.create(superClass && superClass.prototype, {
      constructor: {
        value: subClass,
        enumerable: false,
        writable: true,
        configurable: true
      }
    });
    if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass;
  };

  babelHelpers.instanceof = function (left, right) {
    if (right != null && typeof Symbol !== "undefined" && right[Symbol.hasInstance]) {
      return right[Symbol.hasInstance](left);
    } else {
      return left instanceof right;
    }
  };

  babelHelpers.interopRequireDefault = function (obj) {
    return obj && obj.__esModule ? obj : {
      default: obj
    };
  };

  babelHelpers.interopRequireWildcard = function (obj) {
    if (obj && obj.__esModule) {
      return obj;
    } else {
      var newObj = {};

      if (obj != null) {
        for (var key in obj) {
          if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key];
        }
      }

      newObj.default = obj;
      return newObj;
    }
  };

  babelHelpers.newArrowCheck = function (innerThis, boundThis) {
    if (innerThis !== boundThis) {
      throw new TypeError("Cannot instantiate an arrow function");
    }
  };

  babelHelpers.objectDestructuringEmpty = function (obj) {
    if (obj == null) throw new TypeError("Cannot destructure undefined");
  };

  babelHelpers.objectWithoutProperties = function (obj, keys) {
    var target = {};

    for (var i in obj) {
      if (keys.indexOf(i) >= 0) continue;
      if (!Object.prototype.hasOwnProperty.call(obj, i)) continue;
      target[i] = obj[i];
    }

    return target;
  };

  babelHelpers.possibleConstructorReturn = function (self, call) {
    if (!self) {
      throw new ReferenceError("this hasn't been initialised - super() hasn't been called");
    }

    return call && (typeof call === "object" || typeof call === "function") ? call : self;
  };

  babelHelpers.selfGlobal = typeof global === "undefined" ? self : global;

  babelHelpers.set = function set(object, property, value, receiver) {
    var desc = Object.getOwnPropertyDescriptor(object, property);

    if (desc === undefined) {
      var parent = Object.getPrototypeOf(object);

      if (parent !== null) {
        set(parent, property, value, receiver);
      }
    } else if ("value" in desc && desc.writable) {
      desc.value = value;
    } else {
      var setter = desc.set;

      if (setter !== undefined) {
        setter.call(receiver, value);
      }
    }

    return value;
  };

  babelHelpers.slicedToArray = function () {
    function sliceIterator(arr, i) {
      var _arr = [];
      var _n = true;
      var _d = false;
      var _e = undefined;

      try {
        for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) {
          _arr.push(_s.value);

          if (i && _arr.length === i) break;
        }
      } catch (err) {
        _d = true;
        _e = err;
      } finally {
        try {
          if (!_n && _i["return"]) _i["return"]();
        } finally {
          if (_d) throw _e;
        }
      }

      return _arr;
    }

    return function (arr, i) {
      if (Array.isArray(arr)) {
        return arr;
      } else if (Symbol.iterator in Object(arr)) {
        return sliceIterator(arr, i);
      } else {
        throw new TypeError("Invalid attempt to destructure non-iterable instance");
      }
    };
  }();

  babelHelpers.slicedToArrayLoose = function (arr, i) {
    if (Array.isArray(arr)) {
      return arr;
    } else if (Symbol.iterator in Object(arr)) {
      var _arr = [];

      for (var _iterator = arr[Symbol.iterator](), _step; !(_step = _iterator.next()).done;) {
        _arr.push(_step.value);

        if (i && _arr.length === i) break;
      }

      return _arr;
    } else {
      throw new TypeError("Invalid attempt to destructure non-iterable instance");
    }
  };

  babelHelpers.taggedTemplateLiteral = function (strings, raw) {
    return Object.freeze(Object.defineProperties(strings, {
      raw: {
        value: Object.freeze(raw)
      }
    }));
  };

  babelHelpers.taggedTemplateLiteralLoose = function (strings, raw) {
    strings.raw = raw;
    return strings;
  };

  babelHelpers.temporalRef = function (val, name, undef) {
    if (val === undef) {
      throw new ReferenceError(name + " is not defined - temporal dead zone");
    } else {
      return val;
    }
  };

  babelHelpers.temporalUndefined = {};

  babelHelpers.toArray = function (arr) {
    return Array.isArray(arr) ? arr : Array.from(arr);
  };

  babelHelpers.toConsumableArray = function (arr) {
    if (Array.isArray(arr)) {
      for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) arr2[i] = arr[i];

      return arr2;
    } else {
      return Array.from(arr);
    }
  };
})(typeof global === "undefined" ? self : global);


(function (global) {
  var babelHelpers = global.babelHelpers

  var createClass = babelHelpers.createClass
  babelHelpers.createClass = (Constructor, protoProps, staticProps) => {
    var cls = createClass(Constructor, protoProps, staticProps)
    cls.__babelClass = true

    cls.inject = () => {
      var fx = function () {
        var args = Array.prototype.slice.apply(arguments)
        var instance = new (cls.bind.apply(cls, [null].concat(args)))()
        angular.extend(instance, this)
        return instance
      }
      fx.$inject = cls.$inject
      return fx
    }

    return cls
  }

  babelHelpers.classCallCheck = function () {}

  const functionToString = Function.prototype.toString

  Function.prototype.toString = function () { // eslint-disable-line
    if (this && this.__signatureOverride) {
      return this.__signatureOverride
    }
    if (this && this.__babelClass) {
      var s = functionToString.apply(this)
      return s.replace(/^function/, 'class')
    }
    return functionToString.apply(this)
  }
})(typeof global === 'undefined' ? self : global)

'use strict';

var __ngBootstrap = function __ngBootstrap(exclude) {
    exclude = exclude || [];
    var modules = [];
    for (var pluginName in window.__ngModules) {
        if (exclude.contains(pluginName)) continue;
        modules = modules.concat(window.__ngModules[pluginName]);
    }

    var id = 'app__' + Date.now();
    angular.module(id, modules);
    angular.bootstrap(document, [id]);
};

var __ngShowBootstrapError = function __ngShowBootstrapError() {
    $('.global-bootstrap-error').show();
    console.error('Angular bootstrap has failed');
    console.warn('Consider sending the following error to https://github.com/ajenti/ajenti/issues/new');
};

var __ngShowBootstrapRecovered = function __ngShowBootstrapRecovered(plugin) {
    $('.global-bootstrap-recovered').removeClass('hidden');
    $('.global-bootstrap-recovered .plugin-name').text(plugin);
    $('.global-bootstrap-recovered .btn-close').click(function () {
        $('.global-bootstrap-recovered').remove();
    });
};

window.ajentiBootstrap = function () {
    try {
        __ngBootstrap();
    } catch (e) {
        console.warn('Well, this is awkward');
        console.group('Angular bootstrap has failed:');
        console.error(e);

        for (var pluginName in window.__ngModules) {
            try {
                __ngBootstrap([pluginName]);
                console.log('Worked with ' + pluginName + ' disabled!');
                console.groupEnd();
                __ngShowBootstrapRecovered(pluginName);
                return;
            } catch (e) {
                console.warn('Still failing with ' + pluginName + ' disabled:', e);
            }
        }

        console.groupEnd();
        window.__ngShowBootstrapError();
        throw e;
    }
};


'use strict';

angular.module('core', ['ngAnimate', 'ngRoute', 'ngStorage', 'ngTouch', 'angular-loading-bar', 'btford.socket-io', 'toaster', 'ui.bootstrap', 'angular-sortable-view', 'base64', 'gettext']);

angular.module('core').config(function ($httpProvider, $animateProvider, $compileProvider) {
    $httpProvider.interceptors.push('urlPrefixInterceptor');
    $httpProvider.interceptors.push('unauthenticatedInterceptor');
    $animateProvider.classNameFilter(/animate.+/);
    $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|data|file):/);
});

angular.module('core').run(function () {
    return FastClick.attach(document.body);
});

angular.module('core').factory('$exceptionHandler', function ($injector, $log, gettext) {
    return function (exception, cause) {
        var str = exception.toString();
        if (str && str.indexOf('Possibly unhandled rejection') != 0) {
            $injector.get('notify').warning(gettext('Unhanded error occured'), gettext('Please see browser console'));
        } else {
            $log.debug.apply($log, arguments);
            return;
        }

        console.group('Unhandled exception occured');
        console.warn('Consider sending this error to https://github.com/ajenti/ajenti/issues/new');
        $log.error.apply($log, arguments);
        console.groupEnd();
    };
});


'use strict';

angular.module('core').filter('bytes', function (gettext) {
    return function (bytes, precision) {
        if (isNaN(parseFloat(bytes)) || !isFinite(bytes)) {
            return '-';
        }
        if (bytes === 0) {
            return gettext('0 bytes');
        }
        if (typeof precision === 'undefined') {
            precision = 1;
        }
        var units = [gettext('bytes'), gettext('KB'), gettext('MB'), gettext('GB'), gettext('TB'), gettext('PB')];
        var number = Math.floor(Math.log(bytes) / Math.log(1024));

        var x = bytes / Math.pow(1024, Math.floor(number));
        if (number === 0) {
            x = Math.floor(x);
        } else {
            x = x.toFixed(precision);
        }

        return x + ' ' + units[number];
    };
});

angular.module('core').filter('ordinal', function (gettext) {
    return function (input) {
        if (isNaN(input) || input === null) {
            return input;
        }

        var s = [gettext('th'), gettext('st'), gettext('nd'), gettext('rd')];
        var v = input % 100;
        return input + (s[(v - 20) % 10] || s[v] || s[0]);
    };
});

angular.module('core').filter('page', function () {
    return function (list, page, pageSize) {
        if (list && pageSize) {
            return list.slice((page - 1) * pageSize, page * pageSize);
        }
    };
});

angular.module('core').filter('rankMatch', function () {
    return function (input, field, query) {
        if (!input) {
            return input;
        }
        var rgx = new RegExp(query, 'gi');
        for (var i = 0; i < input.length; i++) {
            var item = input[i];
            var points = 0;
            var data = item[field];
            points += (data.match(rgx) || []).length;
            if (data === query) {
                points += 50;
            }
            if (data.indexOf(query) === 0) {
                points += 10;
            }
            item.rank = points;
        }
        return input;
    };
});

angular.module('core').filter('time', function () {
    return function (time, frac) {
        if (time === null || !angular.isDefined(time)) {
            return '--:--:--';
        }
        var s = '';
        if (time >= 3600 * 24) {
            s += Math.floor(time / 3600 / 24) + 'd ';
        }
        s += ('' + Math.floor(time / 60 / 60) % 24).lpad('0', 2) + ':';
        s += ('' + Math.floor(time / 60) % 60).lpad('0', 2) + ':';
        s += ('' + Math.floor(time) % 60).lpad('0', 2);
        if (frac) {
            s += '.' + ('' + Math.floor((time - Math.floor(time)) * Math.pow(10, frac))).lpad('0', frac + 0);
        }
        return s;
    };
});


'use strict';

angular.module('core').factory('unauthenticatedInterceptor', function ($q, $rootScope, $location, $window, notify, urlPrefix, messagebox, gettext) {
    return {
        responseError: function responseError(rejection) {
            if (rejection.status === 500 && rejection.data.exception === 'SecurityError') {
                notify.error(gettext('Security error'), rejection.data.message);
            } else if (rejection.status === 500 && rejection.data.exception !== 'EndpointError') {
                messagebox.show({
                    title: gettext('Server error'),
                    data: rejection,
                    template: '/core:resources/partial/serverErrorMessage.html',
                    scrollable: true,
                    negative: gettext('Close')
                });
            } else if (rejection.status === 401) {
                if ($rootScope.disableExpiredSessionInterceptor || $location.path().indexOf(urlPrefix + '/view/login') === 0) {
                    return $q.reject(rejection);
                }

                $rootScope.disableExpiredSessionInterceptor = true;
                notify.error(gettext('Your session has expired'));
                $window.location.assign(urlPrefix + '/view/login/normal/' + $location.path());
            }

            return $q.reject(rejection);
        }
    };
});

angular.module('core').factory('urlPrefixInterceptor', function ($q, $rootScope, $location, notify, urlPrefix) {
    return {
        request: function request(config) {
            if (config.url && config.url[0] === '/') {
                config.url = urlPrefix + config.url;
            }
            return config;
        }
    };
});


'use strict';

angular.module('core').config(function ($routeProvider, $locationProvider, urlPrefix) {
    $locationProvider.html5Mode({ enabled: true, requireBase: false });

    $routeProvider.originalWhen = $routeProvider.when;
    $routeProvider.when = function (url, config) {
        url = urlPrefix + url;
        return $routeProvider.originalWhen(url, config);
    };

    $routeProvider.when('/view/', {
        templateUrl: '/core:resources/partial/index.html',
        controller: 'CoreIndexController'
    });

    $routeProvider.when('/view/login/:mode', {
        templateUrl: '/core:resources/partial/login.html',
        controller: 'CoreLoginController'
    });

    $routeProvider.when('/view/login/:mode/:nextPage*', {
        templateUrl: '/core:resources/partial/login.html',
        controller: 'CoreLoginController'
    });

    $routeProvider.when('/view/ui-test', {
        templateUrl: '/core:resources/partial/index.html'
    });
});

// TODO 404

angular.module('core').run(function ($location, urlPrefix) {
    $location._oldPath = $location.path;
    return $location.path = function (path) {
        if (path) {
            path = urlPrefix + path;
        }
        return $location._oldPath(path);
    };
});


'use strict';

angular.module('core').controller('CoreIndexController', function ($scope, $location, customization, identity, urlPrefix) {
    $location.path(customization.plugins.core.startupURL || '/view/dashboard');

    identity.promise.then(function () {
        if (!identity.user) {
            location.assign(urlPrefix + '/view/login/normal');
        }
    });
});


'use strict';

angular.module('core').controller('CoreLoginController', function ($scope, $log, $rootScope, $routeParams, identity, notify, gettext) {
    $rootScope.disableExpiredSessionInterceptor = true;
    $scope.working = false;
    $scope.success = false;

    if ($routeParams.mode.indexOf('sudo:') === 0) {
        $scope.mode = 'sudo';
        $scope.username = $routeParams.mode.split(':')[1];
    } else {
        $scope.mode = $routeParams.mode;
    }

    $scope.login = function () {
        if (!$scope.username || !$scope.password) {
            return;
        }
        $scope.working = true;
        identity.auth($scope.username, $scope.password, $scope.mode).then(function (username) {
            $scope.success = true;
            location.href = $routeParams.nextPage || '/';
        }, function (error) {
            $scope.working = false;
            $log.log('Authentication failed', error);
            notify.error(gettext('Authentication failed'), error);
        });
    };
});


'use strict';

angular.module('core').controller('CoreRootController', function ($scope, $rootScope, $location, $localStorage, $log, $timeout, $q, identity, customization, urlPrefix, ajentiPlugins, ajentiVersion, ajentiPlatform, ajentiPlatformUnmapped, favicon, feedback, locale, config) {
    $rootScope.identity = identity;
    $rootScope.$location = $location;
    $rootScope.location = location;
    $rootScope.urlPrefix = urlPrefix;
    $rootScope.feedback = feedback;
    $rootScope.ajentiVersion = ajentiVersion;
    $rootScope.ajentiPlugins = ajentiPlugins;
    $rootScope.customization = customization;

    // todo figure this out, used in settings template
    $rootScope.keys = function (x) {
        if (x) {
            return Object.keys(x);
        } else {
            return [];
        }
    };

    console.group('Welcome');
    console.info('Ajenti', ajentiVersion);
    console.log('Running on', ajentiPlatform, '/', ajentiPlatformUnmapped);
    if (urlPrefix) {
        console.log('URL prefix', urlPrefix);
    }
    console.log('Plugins', ajentiPlugins);
    console.groupEnd();

    $scope.navigationPresent = $location.path().indexOf('/view/login') === -1;

    feedback.init();

    // ---

    $scope.showSidebar = angular.isDefined($localStorage.showSidebar) ? $localStorage.showSidebar : true;
    $rootScope.toggleNavigation = function (state) {
        if (angular.isDefined(state)) {
            $scope.showSidebar = state;
        } else {
            $scope.showSidebar = !$scope.showSidebar;
        }
        $localStorage.showSidebar = $scope.showSidebar;
        $scope.$broadcast('navigation:toggle');
    };

    // ---
    $scope.showOverlaySidebar = false;
    $rootScope.toggleOverlayNavigation = function (state) {
        if (angular.isDefined(state)) {
            $scope.showOverlaySidebar = state;
        } else {
            $scope.showOverlaySidebar = !$scope.showOverlaySidebar;
        }
        $scope.$broadcast('navigation:toggle');
    };

    $scope.$on('$routeChangeSuccess', function () {
        $scope.toggleOverlayNavigation(false);
        feedback.emit('navigation', { url: $location.path() });
    });

    // ---

    $scope.isWidescreen = angular.isDefined($localStorage.isWidescreen) ? $localStorage.isWidescreen : false;

    $scope.toggleWidescreen = function (state) {
        if (angular.isDefined(state)) {
            $scope.isWidescreen = state;
        } else {
            $scope.isWidescreen = !$scope.isWidescreen;
        }
        $localStorage.isWidescreen = $scope.isWidescreen;
        $scope.$broadcast('widescreen:toggle');
    };

    // ---

    identity.init();
    identity.promise.then(function () {
        $log.info('Identity', identity.user);
        return $rootScope.appReady = true;
    });

    favicon.init();

    setTimeout(function () {
        return $(window).resize(function () {
            $scope.$apply(function () {
                return $rootScope.$broadcast('window:resize');
            });
        });
    });
});


'use strict';

angular.module('core').controller('CoreTasksController', function ($scope, socket, tasks, identity) {
    $scope.tasks = tasks;
});


'use strict';

angular.module('core').controller('CoreNavboxController', function ($scope, $http, $location, hotkeys) {
    $scope.results = null;

    hotkeys.on($scope, function (key, event) {
        if (key === 'P' && event.ctrlKey) {
            $scope.visible = true;
            return true;
        }
        return false;
    }, 'keydown');

    $scope.cancel = function () {
        $scope.visible = false;
        $scope.query = null;
    };

    $scope.onSearchboxKeyDown = function ($event) {
        if ($scope.results) {
            if ($event.keyCode === hotkeys.ENTER) {
                $scope.open($scope.results[0]);
            }

            var result = [];

            var len = Math.min($scope.results.length, 10);
            for (var i = 0; j < len; i++) {
                if ($event.keyCode === i.toString().charCodeAt(0) && $event.shiftKey) {
                    $scope.open($scope.results[i]);
                    $event.preventDefault();
                }
            }
        }
    };

    $scope.onSearchboxKeyUp = function ($event) {
        if ($event.keyCode === hotkeys.ESC) {
            $scope.cancel();
        }
    };

    $scope.$watch('query', function () {
        if (!$scope.query) {
            return;
        }
        $http.get('/api/core/navbox/' + $scope.query).then(function (response) {
            return $scope.results = response.data;
        });
    });

    $scope.open = function (result) {
        $location.path(result.url);
        $scope.cancel();
    };
});


'use strict';

angular.module('core').directive('autofocus', function ($timeout) {
    return {
        restrict: 'A',
        link: function link(scope, element) {
            $timeout(function () {
                return element[0].focus();
            });
        }
    };
});


'use strict';

angular.module('core').directive('checkbox', function () {
    return {
        restrict: 'EA',
        scope: {
            text: '@',
            toggle: '='
        },
        require: 'ngModel',
        template: "<i class=\"fa fa-square-o off\"></i><i class=\"fa fa-check-square on\"></i> {{text}}",
        link: function link($scope, element, attr, ngModelController) {
            var classToToggle = 'active';

            ngModelController.$render = function () {
                if (ngModelController.$viewValue) {
                    element.addClass(classToToggle);
                } else {
                    element.removeClass(classToToggle);
                }
            };

            element.bind('click', function () {
                return $scope.$apply(function () {
                    ngModelController.$setViewValue(!ngModelController.$viewValue);
                    ngModelController.$render();
                });
            });

            if ($scope.toggle) {
                ngModelController.$formatters.push(function (v) {
                    return v === $scope.toggle[1];
                });
                ngModelController.$parsers.push(function (v) {
                    return v ? $scope.toggle[1] : $scope.toggle[0];
                });
            }
        }
    };
});


'use strict';

angular.module('core').directive('datepickerPopup', function () {
    return {
        restrict: 'EAC',
        require: 'ngModel',
        link: function link(scope, element, attr, controller) {
            controller.$formatters.shift();
        }
    };
});


'use strict';

angular.module('core').directive('dialog', function ($http, $log, $timeout) {
    return {
        restrict: 'E',
        transclude: true,
        template: '\n            <div class="modal">\n                <div class="modal-dialog {{attrs.dialogClass}}">\n                    <div class="modal-content">\n                        <ng-transclude></ng-transclude>\n                    </div>\n                </div>\n            </div>',
        link: function link($scope, element, attrs) {
            element.addClass('block-element');
            $timeout(function () {
                return element.addClass('animate-modal');
            });

            $scope.attrs = attrs;
            $scope.$watch('attrs.ngShow', function () {
                if (attrs.ngShow) {
                    return setTimeout(function () {
                        return element.find('*[autofocus]').focus();
                    });
                }
            });
        }
    };
});


'use strict';

angular.module('core').directive('fitToParent', function () {
    return function ($scope, element, attrs) {
        var parent = element.parent();

        $(window).resize(function () {
            if (angular.isDefined(attrs.fitWidth)) {
                element.width(1);
                element.width(parent.width());
            }
            if (angular.isDefined(attrs.fitHeight)) {
                element.height(1);
                element.height(parent.height());
            }
        });
    };
});


'use strict';

angular.module('core').directive('floatingToolbar', function () {
    return {
        restrict: 'E',
        transclude: true,
        template: '\n            <div class="container">\n                <div class="row">\n                    <div ng:class="{\'col-md-3\': showSidebar}">\n                    </div>\n                    <div ng:class="{\'col-md-9\': showSidebar, \'col-md-12\': !showSidebar}">\n                        <div class="bar row">\n                            <ng-transclude></ng-transclude>\n                        </div>\n                    </div>\n                </div>\n            </div>'
    };
});


'use strict';

angular.module('core').directive('keyboardFocus', function () {
    return function ($scope, element, attrs) {
        return element.bind('keydown', function (event) {
            if (event.keyCode === 40) {
                element.find('*:focus').first().next().focus();
                event.preventDefault();
            }
            if (event.keyCode === 38) {
                element.find('*:focus').first().prev().focus();
                event.preventDefault();
            }
        });
    };
});


'use strict';

angular.module('core').directive('messageboxContainer', function (messagebox) {
    return {
        restrict: 'E',
        template: '\n            <dialog ng:show="message.visible" style="z-index: 1050" ng:repeat="message in messagebox.messages">\n                <div class="modal-header">\n                    <h4>{{message.title|translate}}</h4>\n                </div>\n                <div class="modal-body" ng:class="{scrollable: message.scrollable}">\n                    <div ng:show="message.progress">\n                        <progress-spinner></progress-spinner>\n                    </div>\n                    {{message.text|translate}}\n                    <ng:include ng:if="message.template" src="message.template"></ng:include>\n                    <div ng:show="message.prompt">\n                        <label>{{message.prompt}}</label>\n                        <input type="text" ng:model="message.value" ng:enter="doPositive(message)" class="form-control" autofocus />\n                    </div>\n                </div>\n                <div class="modal-footer">\n                    <a ng:click="doPositive(message)" ng:show="message.positive" class="positive btn btn-default btn-flat">{{message.positive|translate}}</a>\n                    <a ng:click="doNegative(message)" ng:show="message.negative" class="negative btn btn-default btn-flat">{{message.negative|translate}}</a>\n                </div>\n            </dialog>',
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


'use strict';

angular.module('core').directive('ngEnter', function () {
    return function ($scope, element, attrs) {
        return element.bind('keydown keypress', function (event) {
            if (event.which === 13) {
                $scope.$apply(function () {
                    return $scope.$eval(attrs.ngEnter);
                });
                event.preventDefault();
            }
        });
    };
});


'use strict';

angular.module('core').directive('progressSpinner', function () {
    return {
        restrict: 'E',
        template: '\n            <div>\n                <div class="one"></div>\n                <div class="two"></div>\n            </div>'
    };
});


'use strict';

angular.module('core').directive('rootAccess', function (identity) {
    return {
        restrict: 'A',
        link: function link($scope, element, attr) {
            var template = '\n                <div class="text-center root-access-blocker">\n                    <h1>\n                        <i class="fa fa-lock"></i>\n                    </h1>\n                    <h3 translate>\n                        Superuser access required\n                    </h3>\n                </div>';
            identity.promise.then(function () {
                if (!identity.isSuperuser) {
                    element.empty().append($(template));
                }
            });
        }
    };
});


'use strict';

angular.module('core').directive('coreSidebar', function ($http, $log) {
    return {
        restrict: 'E',
        scope: true,
        template: '\n            <div ng:bind-html="customization.plugins.core.sidebarUpperContent"></div>\n            <ng:include src="\'/core:resources/partial/sidebarItem.html\'" />\n            <div ng:bind-html="customization.plugins.core.sidebarLowerContent"></div>\n        ',
        link: function link($scope, element, attrs) {
            $http.get('/api/core/sidebar').then(function (response) {
                $scope.item = response.data.sidebar;
                $scope.item.expanded = true;
                $scope.item.isRoot = true;
                $scope.item.children.forEach(function (item) {
                    item.expanded = true;
                    item.isTopLevel = true;
                });
            });
        }
    };
});


'use strict';

angular.module('core').directive('smartProgress', function () {
    return {
        restrict: 'E',
        scope: {
            animate: '=?',
            value: '=',
            text: '=?',
            max: '=',
            maxText: '=?'
        },
        template: '\n            <div>\n                <uib-progressbar type="warning" max="100" value="100 * value / max" animate="animate" ng:class="{indeterminate: !max}">\n                </uib-progressbar>\n            </div>\n            <div class="values">\n                <span class="pull-left no-wrap">{{text}}</span>\n                <span class="pull-right no-wrap">{{maxText}}</span>\n            </div>',
        link: function link($scope, element, attr) {
            $scope.animate = angular.isDefined($scope.animate) ? $scope.animate : true;
        }
    };
});


'use strict';

angular.module('core').service('config', function ($http, $q, initialConfigContent) {
    var _this = this;

    this.load = function () {
        return $http.get("/api/core/config").then(function (response) {
            return _this.data = response.data;
        });
    };

    this.save = function () {
        return $http.post("/api/core/config", _this.data);
    };

    this.getUserConfig = function () {
        return $http.get("/api/core/user-config").then(function (response) {
            return response.data;
        });
    };

    this.setUserConfig = function (config) {
        return $http.post("/api/core/user-config", config).then(function (response) {
            return response.data;
        });
    };

    this.getAuthenticationProviders = function (config) {
        return $http.post("/api/core/authentication-providers", config).then(function (response) {
            return response.data;
        });
    };

    this.getPermissions = function (config) {
        return $http.post("/api/core/permissions", config).then(function (response) {
            return response.data;
        });
    };

    this.data = initialConfigContent;

    // For compatibility
    this.promise = $q.resolve(this.data);

    return this;
});


'use strict';

angular.module('core').service('core', function ($timeout, $q, $http, $window, messagebox, gettext) {
    var _this = this;

    this.pageReload = function () {
        return $window.location.reload();
    };

    this.restart = function () {
        return messagebox.show({
            title: gettext('Restart'),
            text: gettext('Restart the panel?'),
            positive: gettext('Yes'),
            negative: gettext('No')
        }).then(function () {
            _this.forceRestart();
        });
    };

    this.forceRestart = function () {
        var msg = messagebox.show({ progress: true, title: gettext('Restarting') });
        return $http.get('/api/core/restart-master').then(function () {
            return $timeout(function () {
                msg.close();
                messagebox.show({ title: gettext('Restarted'), text: gettext('Please wait') });
                $timeout(function () {
                    _this.pageReload();
                    return setTimeout(function () {
                        // sometimes this is not enough
                        return _this.pageReload();
                    }, 5000);
                });
            }, 5000);
        }).catch(function (err) {
            msg.close();
            notify.error(gettext('Could not restart'), err.message);
            return $q.reject(err);
        });
    };

    return this;
});


'use strict';

angular.module('core').service('customization', function () {
    this.plugins = { core: {
            extraProfileMenuItems: []
        } };
    return this;
});


'use strict';

angular.module('core').service('favicon', function ($rootScope, identity, customization) {
    var _this = this;

    this.colors = {
        red: '#F44336',
        bluegrey: '#607D8B',
        purple: '#9C27B0',
        blue: '#2196F3',
        default: '#2196F3',
        cyan: '#00BCD4',
        green: '#4CAF50',
        deeporange: '#FF5722',
        orange: '#FF9800',
        teal: '#009688'
    };

    this.set = function (color) {
        $rootScope.themeColorValue = _this.colors[color];

        var canvas = document.createElement('canvas');
        canvas.width = 16;
        canvas.height = 16;
        var context = canvas.getContext('2d');
        if (color) {
            context.fillStyle = _this.colors[color];
            //context.fillRect(4, 4, 8, 8)
            context.fillRect(4, 4, 3, 8);
            context.fillRect(4, 4, 8, 3);
            context.fillRect(9, 4, 3, 8);
            context.fillRect(4, 9, 8, 3);
        } else {
            // use this for something
            context.fillStyle = _this.colors[color];
            context.fillRect(1, 6, 4, 4);
            context.fillRect(6, 6, 4, 4);
            context.fillRect(11, 6, 4, 4);
        }

        _this.setURL(canvas.toDataURL());
    };

    this.setURL = function (url) {
        var link = $('link[rel="shortcut icon"]')[0];
        link.type = 'image/x-icon';
        link.href = url;
    };

    this.init = function () {
        var _this2 = this;

        this.scope = $rootScope.$new();
        this.scope.identity = identity;
        if (customization.plugins.core.faviconURL) {
            this.setURL(customization.plugins.core.faviconURL);
        } else {
            this.scope.$watch('identity.color', function () {
                _this2.set(identity.color);
            });
        }
    };

    return this;
});


'use strict';

angular.module('core').service('feedback', function ($log, ajentiVersion, ajentiPlatform, ajentiPlatformUnmapped) {
    var _this = this;

    this.enabled = true; // TODO
    this.token = 'df4919c7cb869910c1e188dbc2918807';

    this.init = function () {
        mixpanel.init(_this.token);
        mixpanel.register({
            version: ajentiVersion,
            platform: ajentiPlatform,
            platformUnmapped: ajentiPlatformUnmapped
        });
    };

    this.emit = function (evt, params) {
        if (_this.enabled) {
            try {
                mixpanel.track(evt, params || {});
            } catch (e) {
                $log.error(e);
            }
        }
    };

    return this;
});


'use strict';

var _ = {};

// angular-gettext defines a stub as a constant, impossible to override it with e.g. factory
angular.module('core').constant('gettext', function (str) {
    return _.gettextCatalog.getString(str);
});

angular.module('core').service('locale', function ($http, gettextCatalog) {
    _.gettextCatalog = gettextCatalog;

    this.setLanguage = function (lang) {
        return $http.get('/resources/all.locale.js?lang=' + lang).then(function (rq) {
            gettextCatalog.setStrings(lang, rq.data);
            return gettextCatalog.setCurrentLanguage(lang);
        });
    };

    return this;
});

angular.module('core').run(function (locale, config) {
    return config.promise.then(function () {
        return locale.setLanguage(config.data.language || 'en');
    });
});


'use strict';

angular.module('core').service('hotkeys', function ($timeout, $window, $rootScope) {
    this.ESC = 27;
    this.ENTER = 13;

    var handler = function handler(e, mode) {
        var isTextField = false;
        if (!e.metaKey && !e.ctrlKey) {
            if ($('input:focus').length > 0 || $('textarea:focus').length > 0) {
                isTextField = true;
            }
        }

        var char = e.which < 32 ? e.which : String.fromCharCode(e.which);
        if (!isTextField) {
            $rootScope.$broadcast(mode, char, e);
        }
        $rootScope.$broadcast(mode + ':global', char, e);
        $rootScope.$apply();
    };

    $timeout(function () {
        $(document).keydown(function (e) {
            return handler(e, 'keydown');
        });
        $(document).keyup(function (e) {
            return handler(e, 'keyup');
        });
        $(document).keypress(function (e) {
            return handler(e, 'keypress');
        });
    });

    this.on = function (scope, handler, mode) {
        return scope.$on(mode || 'keydown', function ($event, key, event) {
            if (handler(key, event)) {
                event.preventDefault();
                return event.stopPropagation();
            }
        });
    };
    return this;
});


'use strict';

angular.module('core').service('identity', function ($http, $location, $window, $timeout, $q, urlPrefix, ajentiBootstrapColor) {
    var _this = this;

    var q = $q.defer();
    this.promise = q.promise;
    this.color = ajentiBootstrapColor;

    this.init = function () {
        return $http.get('/api/core/identity').success(function (data) {
            _this.user = data.identity.user;
            _this.uid = data.identity.uid;
            _this.effective = data.identity.effective;
            _this.elevation_allowed = data.identity.elevation_allowed;
            _this.profile = data.identity.profile;
            _this.machine = data.machine;
            _this.color = data.color;
            _this.isSuperuser = _this.effective === 0;
            q.resolve();
        }).error(function () {
            return q.reject();
        });
    };

    this.auth = function (username, password, mode) {
        var data = {
            username: username,
            password: password,
            mode: mode
        };

        return $http.post('/api/core/auth', data).then(function (response) {
            if (!response.data.success) {
                return $q.reject(response.data.error);
            }
        });
    };

    this.login = function () {
        return $window.location.assign(urlPrefix + '/view/login/normal/' + $location.path());
    };

    this.elevate = function () {
        var _this2 = this;

        $http.get('/api/core/logout');
        return $timeout(function () {
            $window.location.assign(urlPrefix + '/view/login/sudo:' + _this2.user + '/' + $location.path());
        }, 1000);
    };

    this.logout = function () {
        $http.get('/api/core/logout');
        return $timeout(function () {
            $window.location.assign(urlPrefix + '/view/login/normal/' + $location.path());
        }, 1000);
    };

    return this;
});


'use strict';

angular.module('core').service('messagebox', function ($timeout, $q) {
    var _this = this;

    this.messages = [];

    this.show = function (options) {
        var q = $q.defer();
        options.visible = true;
        options.q = q;
        _this.messages.push(options);
        return {
            messagebox: options,
            then: function then(f) {
                return q.promise.then(f);
            },
            catch: function _catch(f) {
                return q.promise.catch(f);
            },
            finally: function _finally(f) {
                return q.promise.finally(f);
            },
            close: function close() {
                return _this.close(options);
            }
        };
    };

    this.prompt = function (prompt, value) {
        value = value || '';
        return _this.show({
            prompt: prompt,
            value: value,
            positive: 'OK',
            negative: 'Cancel'
        });
    };

    this.close = function (msg) {
        msg.visible = false;
        return $timeout(function () {
            _this.messages.remove(msg);
        }, 1000);
    };

    return this;
});


'use strict';

angular.module('core').service('notify', function ($location, toaster) {
    window.toaster = toaster;
    this.info = function (title, text) {
        return toaster.pop('info', title, text);
    };

    this.success = function (title, text) {
        return toaster.pop('success', title, text);
    };

    this.warning = function (title, text) {
        return toaster.pop('warning', title, text);
    };

    this.error = function (title, text) {
        return toaster.pop('error', title, text);
    };

    this.custom = function (style, title, text, url) {
        return toaster.pop(style, title, text, 5000, 'trustedHtml', function () {
            return $location.path(url);
        });
    };

    return this;
});


'use strict';

angular.module('core').service('pageTitle', function ($rootScope) {
    this.set = function (expr, scope) {
        if (!scope) {
            $rootScope.pageTitle = expr;
        } else {
            var refresh = function refresh() {
                var title = scope.$eval(expr);
                if (angular.isDefined(title)) {
                    $rootScope.pageTitle = title;
                }
            };

            scope.$watch(expr, function () {
                return refresh();
            });
            refresh();
        }
    };

    return this;
});


'use strict';

angular.module('core').service('push', function ($rootScope, $q, $log, $http, socket) {
    $rootScope.$on('socket:push', function ($event, msg) {
        $log.debug('Push message from', msg.plugin, msg.message);
        $rootScope.$broadcast('push:' + msg.plugin, msg.message);
    });

    return this;
});


'use strict';

angular.module('core').service('socket', function ($log, $location, $rootScope, $q, socketFactory, urlPrefix) {
    var _this = this;

    this.enabled = true;

    var cfg = {
        resource: (urlPrefix + '/socket.io').substring(1),
        'reconnection limit': 1,
        'max reconnection attempts': 999999
    };

    if (/Apple Computer/.test(navigator.vendor) && location.protocol === 'https:') {
        cfg.transports = ['jsonp-polling']; // Safari can go to hell
    }

    this.socket = socketFactory({
        ioSocket: io.connect('/socket', cfg)
    });

    this.socket.on('connecting', function (e) {
        return $log.log('Socket is connecting');
    });

    this.socket.on('connect_failed', function (e) {
        return $log.log('Socket is connection failed', e);
    });

    this.socket.on('reconnecting', function (e) {
        return $log.log('Socket is reconnecting');
    });

    this.socket.on('reconnect_failed', function (e) {
        return $log.log('Socket reconnection failed', e);
    });

    this.socket.on('reconnect', function (e) {
        $rootScope.socketConnectionLost = false;
        $log.log('Socket has reconnected');
    });

    this.socket.on('connect', function (e) {
        if (!_this.enabled) {
            return;
        }
        $rootScope.socketConnectionLost = false;
        $rootScope.$broadcast('socket-event:connect');
        $log.log('Socket has connected');
    });

    this.socket.on('disconnect', function (e) {
        if (!_this.enabled) {
            return;
        }
        $rootScope.socketConnectionLost = true;
        $rootScope.$broadcast('socket-event:disconnect');
        $log.error('Socket has disconnected', e);
    });

    this.socket.on('error', function (e) {
        $rootScope.socketConnectionLost = true;
        $log.error('Error', e);
    });

    this.send = function (plugin, data) {
        var q = $q.defer();
        var msg = {
            plugin: plugin,
            data: data
        };
        _this.socket.emit('message', msg, function () {
            return q.resolve();
        });
        return q.promise;
    };

    this.socket.on('message', function (msg) {
        if (!_this.enabled) {
            return;
        }
        if (msg[0] === '{') {
            msg = JSON.parse(msg);
        }
        $log.debug('Socket message from', msg.plugin, msg.data);
        $rootScope.$broadcast('socket:' + msg.plugin, msg.data);
    });

    return this;
});


'use strict';

angular.module('core').service('tasks', function ($rootScope, $q, $http, notify, push, socket, gettext) {
    var _this = this;

    this.tasks = [];
    this.deferreds = {};

    $rootScope.$on('socket-event:connect', function () {
        return $http.get('/api/core/tasks/request-update');
    });

    $rootScope.$on('push:tasks', function ($event, msg) {
        if (msg.type === 'update') {
            if (_this.tasks.length > msg.tasks.length) {
                _this.tasks.length = msg.tasks.length;
            }

            for (var i = 0; i < msg.tasks.length; i++) {
                if (_this.tasks.length <= i) {
                    _this.tasks.push({});
                }
                angular.copy(msg.tasks[i], _this.tasks[i]);
            }
        }
        if (msg.type === 'message') {
            if (msg.message.type === 'done') {
                var def = _this.deferreds[msg.message.task.id];
                if (def) {
                    def.resolve();
                }
                notify.success(gettext(msg.message.task.name), gettext('Done'));
            }
            if (msg.message.type === 'exception') {
                var def = _this.deferreds[msg.message.task.id];
                if (def) {
                    def.reject(msg.message);
                }
                return notify.error(gettext(msg.message.task.name), gettext('Failed: ' + msg.message.exception));
            }
        }
    });

    this.start = function (cls, args, kwargs) {
        args = args || [];
        kwargs = kwargs || {};

        var data = {
            cls: cls,
            args: args,
            kwargs: kwargs
        };
        return $http.post('/api/core/tasks/start', data).then(function (response) {
            var def = $q.defer();
            var taskId = response.data;
            _this.deferreds[taskId] = def;

            return { id: taskId, promise: def.promise };
        });
    };

    return this;
});


