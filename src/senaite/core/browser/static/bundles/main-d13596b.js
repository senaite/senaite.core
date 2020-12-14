/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId]) {
/******/ 			return installedModules[moduleId].exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, { enumerable: true, get: getter });
/******/ 		}
/******/ 	};
/******/
/******/ 	// define __esModule on exports
/******/ 	__webpack_require__.r = function(exports) {
/******/ 		if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 			Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 		}
/******/ 		Object.defineProperty(exports, '__esModule', { value: true });
/******/ 	};
/******/
/******/ 	// create a fake namespace object
/******/ 	// mode & 1: value is a module id, require it
/******/ 	// mode & 2: merge all properties of value into the ns
/******/ 	// mode & 4: return value when already ns object
/******/ 	// mode & 8|1: behave like require
/******/ 	__webpack_require__.t = function(value, mode) {
/******/ 		if(mode & 1) value = __webpack_require__(value);
/******/ 		if(mode & 8) return value;
/******/ 		if((mode & 4) && typeof value === 'object' && value && value.__esModule) return value;
/******/ 		var ns = Object.create(null);
/******/ 		__webpack_require__.r(ns);
/******/ 		Object.defineProperty(ns, 'default', { enumerable: true, value: value });
/******/ 		if(mode & 2 && typeof value != 'string') for(var key in value) __webpack_require__.d(ns, key, function(key) { return value[key]; }.bind(null, key));
/******/ 		return ns;
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "/++plone++senaite.core.static/bundles";
/******/
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 2);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports) {

module.exports = jQuery;

/***/ }),
/* 1 */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
/* WEBPACK VAR INJECTION */(function($) {/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c site.coffee
 */
var Site,
    bind = function bind(fn, me) {
  return function () {
    return fn.apply(me, arguments);
  };
};

Site = function () {
  /**
   * Creates a new instance of Site
   */
  function Site() {
    this.set_cookie = bind(this.set_cookie, this);
    this.read_cookie = bind(this.read_cookie, this);
    this.authenticator = bind(this.authenticator, this); // console.debug("Site::init");
  }
  /**
   * Returns the authenticator value
   */


  Site.prototype.authenticator = function () {
    var auth, url_params;
    auth = $("input[name='_authenticator']").val();

    if (!auth) {
      url_params = new URLSearchParams(window.location.search);
      auth = url_params.get("_authenticator");
    }

    return auth;
  };
  /**
   * Reads a cookie value
   * @param {name} the name of the cookie
   */


  Site.prototype.read_cookie = function (name) {
    var c, ca, i; // console.debug("Site::read_cookie:" + name);

    name = name + '=';
    ca = document.cookie.split(';');
    i = 0;

    while (i < ca.length) {
      c = ca[i];

      while (c.charAt(0) === ' ') {
        c = c.substring(1);
      }

      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }

      i++;
    }

    return null;
  };
  /**
   * Sets a cookie value
   * @param {name} the name of the cookie
   * @param {value} the value of the cookie
   */


  Site.prototype.set_cookie = function (name, value) {
    var d, expires; // console.debug("Site::set_cookie:name=" + name + ", value=" + value);

    d = new Date();
    d.setTime(d.getTime() + 1 * 24 * 60 * 60 * 1000);
    expires = 'expires=' + d.toUTCString();
    document.cookie = name + '=' + value + ';' + expires + ';path=/';
  };

  return Site;
}();

/* harmony default export */ __webpack_exports__["a"] = (Site);
/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(0)))

/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(4);
module.exports = __webpack_require__(3);


/***/ }),
/* 3 */
/***/ (function(module, exports, __webpack_require__) {

// extracted by mini-css-extract-plugin

/***/ }),
/* 4 */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
// ESM COMPAT FLAG
__webpack_require__.r(__webpack_exports__);

// EXTERNAL MODULE: external "jQuery"
var external_jQuery_ = __webpack_require__(0);
var external_jQuery_default = /*#__PURE__*/__webpack_require__.n(external_jQuery_);

// CONCATENATED MODULE: ./components/i18n.js
/* i18n integration. This is forked from jarn.jsi18n
 *
 * This is a singleton.
 * Configuration is done on the body tag data-i18ncatalogurl attribute
 *     <body data-i18ncatalogurl="/plonejsi18n">
 *
 *  Or, it'll default to "/plonejsi18n"
 */


var i18n_I18N = function I18N() {
  var self = this;
  self.baseUrl = external_jQuery_default()('body').attr('data-i18ncatalogurl');
  self.currentLanguage = external_jQuery_default()('html').attr('lang') || 'en'; // Fix for country specific languages

  if (self.currentLanguage.split('-').length > 1) {
    self.currentLanguage = self.currentLanguage.split('-')[0] + '_' + self.currentLanguage.split('-')[1].toUpperCase();
  }

  self.storage = null;
  self.catalogs = {};
  self.ttl = 24 * 3600 * 1000; // Internet Explorer 8 does not know Date.now() which is used in e.g. loadCatalog, so we "define" it

  if (!Date.now) {
    Date.now = function () {
      return new Date().valueOf();
    };
  }

  try {
    if ('localStorage' in window && window.localStorage !== null && 'JSON' in window && window.JSON !== null) {
      self.storage = window.localStorage;
    }
  } catch (e) {}

  self.configure = function (config) {
    for (var key in config) {
      self[key] = config[key];
    }
  };

  self._setCatalog = function (domain, language, catalog) {
    if (domain in self.catalogs) {
      self.catalogs[domain][language] = catalog;
    } else {
      self.catalogs[domain] = {};
      self.catalogs[domain][language] = catalog;
    }
  };

  self._storeCatalog = function (domain, language, catalog) {
    var key = domain + '-' + language;

    if (self.storage !== null && catalog !== null) {
      self.storage.setItem(key, JSON.stringify(catalog));
      self.storage.setItem(key + '-updated', Date.now());
    }
  };

  self.getUrl = function (domain, language) {
    return self.baseUrl + '?domain=' + domain + '&language=' + language;
  };

  self.loadCatalog = function (domain, language) {
    if (language === undefined) {
      language = self.currentLanguage;
    }

    if (self.storage !== null) {
      var key = domain + '-' + language;

      if (key in self.storage) {
        if (Date.now() - parseInt(self.storage.getItem(key + '-updated'), 10) < self.ttl) {
          var catalog = JSON.parse(self.storage.getItem(key));

          self._setCatalog(domain, language, catalog);

          return;
        }
      }
    }

    if (!self.baseUrl) {
      return;
    }

    external_jQuery_default.a.getJSON(self.getUrl(domain, language), function (catalog) {
      if (catalog === null) {
        return;
      }

      self._setCatalog(domain, language, catalog);

      self._storeCatalog(domain, language, catalog);
    });
  };

  self.MessageFactory = function (domain, language) {
    language = language || self.currentLanguage;
    return function translate(msgid, keywords) {
      var msgstr;

      if (domain in self.catalogs && language in self.catalogs[domain] && msgid in self.catalogs[domain][language]) {
        msgstr = self.catalogs[domain][language][msgid];
      } else {
        msgstr = msgid;
      }

      if (keywords) {
        var regexp, keyword;

        for (keyword in keywords) {
          if (keywords.hasOwnProperty(keyword)) {
            regexp = new RegExp('\\$\\{' + keyword + '\\}', 'g');
            msgstr = msgstr.replace(regexp, keywords[keyword]);
          }
        }
      }

      return msgstr;
    };
  };
};

/* harmony default export */ var components_i18n = (i18n_I18N);
// CONCATENATED MODULE: ./i18n-wrapper.js
 // SENAITE message factory

var t = null;
var i18n_wrapper_t = function _t(msgid, keywords) {
  if (t === null) {
    var i18n = new components_i18n();
    console.debug("*** Loading `senaite.core` i18n MessageFactory ***");
    i18n.loadCatalog("senaite.core");
    t = i18n.MessageFactory("senaite.core");
  }

  return t(msgid, keywords);
}; // Plone message factory

var p = null;
var i18n_wrapper_p = function _p(msgid, keywords) {
  if (p === null) {
    var i18n = new components_i18n();
    console.debug("*** Loading `plone` i18n MessageFactory ***");
    i18n.loadCatalog("plone");
    p = i18n.MessageFactory("plone");
  }

  return p(msgid, keywords);
};
// EXTERNAL MODULE: ./components/site.js
var site = __webpack_require__(1);

// CONCATENATED MODULE: ./components/sidebar.js
function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

/* SENAITE Sidebar
 *
 * The sidebar shows when the mouse enters and hides when the mouse leaves the
 * HTML element.
 *
 * It keeps open when the toggle button was clicked.
 */
var Sidebar = /*#__PURE__*/function () {
  function Sidebar(config) {
    _classCallCheck(this, Sidebar);

    this.config = Object.assign({
      "el": "sidebar",
      "toggle_el": "sidebar-header",
      "cookie_key": "sidebar-toggle",
      "timeout": 1000
    }, config); // Timer ID

    this.tid = null; // Bind "this" context when called

    this.maximize = this.maximize.bind(this);
    this.minimize = this.minimize.bind(this);
    this.on_click = this.on_click.bind(this);
    this.on_mouseenter = this.on_mouseenter.bind(this);
    this.on_mouseleave = this.on_mouseleave.bind(this); // toggle button handler

    this.toggle_el = document.getElementById(this.config.toggle_el);
    this.toggle_el.addEventListener("click", this.on_click); // sidebar view/hide handler

    this.el = document.getElementById(this.config.el);
    this.el.addEventListener("mouseenter", this.on_mouseenter);
    this.el.addEventListener("mouseleave", this.on_mouseleave);

    if (this.is_toggled()) {
      this.el.classList.remove("minimized");
      this.el.classList.add("toggled");
    }

    return this;
  }

  _createClass(Sidebar, [{
    key: "is_toggled",
    value: function is_toggled() {
      return window.site.read_cookie(this.config.cookie_key) == "true";
    }
  }, {
    key: "toggle",
    value: function toggle() {
      var _toggle = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;

      window.site.set_cookie(this.config.cookie_key, _toggle);

      if (_toggle) {
        this.el.classList.add("toggled");
        this.maximize();
      } else {
        this.el.classList.remove("toggled");
        this.minimize();
      }
    }
  }, {
    key: "minimize",
    value: function minimize() {
      this.el.classList.add("minimized");
    }
  }, {
    key: "maximize",
    value: function maximize() {
      this.el.classList.remove("minimized");
    }
  }, {
    key: "on_click",
    value: function on_click(event) {
      // console.debug("Sidebar::on_click:event=", event)
      clearTimeout(this.tid);
      this.toggle(!this.is_toggled());
    }
  }, {
    key: "on_mouseenter",
    value: function on_mouseenter(event) {
      // console.debug("Sidebar::on_mouseenter:event=", event)
      clearTimeout(this.tid);
      if (this.is_toggled()) return;
      this.tid = setTimeout(this.maximize, this.config.timeout);
    }
  }, {
    key: "on_mouseleave",
    value: function on_mouseleave(event) {
      // console.debug("Sidebar::on_mouseleave:event=", event)
      clearTimeout(this.tid);
      if (this.is_toggled()) return;
      this.minimize(); // console.debug("Clearing sidebar timeout", this.tid);
    }
  }]);

  return Sidebar;
}();

/* harmony default export */ var sidebar = (Sidebar);
// CONCATENATED MODULE: ./senaite.core.js





document.addEventListener("DOMContentLoaded", function () {
  console.debug("*** SENAITE CORE JS LOADED ***"); // Initialize i18n message factories

  window.i18n = new components_i18n();
  window._t = i18n_wrapper_t;
  window._p = i18n_wrapper_p; // BBB: set global `portal_url` variable

  window.portal_url = document.body.dataset.portalUrl; // TinyMCE

  tinymce.init({
    height: 300,
    selector: "textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text'],textarea.richTextWidget",
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    content_css: "/++plone++senaite.core.static/bundles/main.css"
  }); // /TinyMCE
  // Initialize Site

  window.site = new site["a" /* default */](); // Initialize Sidebar

  window.sidebar = new sidebar({
    "el": "sidebar"
  }); // Tooltips

  external_jQuery_default()(function () {
    external_jQuery_default()("[data-toggle='tooltip']").tooltip();
  }); // /Tooltips
  // Auto LogOff

  var logoff = document.body.dataset.autoLogoff || 0;
  var logged = document.body.classList.contains("userrole-authenticated"); // Max value for setTimeout is a 32 bit integer

  var max_timeout = Math.pow(2, 31) - 1;

  if (logoff > 0 && logged) {
    var logoff_ms = logoff * 60 * 1000;

    if (logoff_ms > max_timeout) {
      console.warn("Setting logoff_ms to max value ".concat(max_timeout, "ms"));
      logoff_ms = max_timeout;
    }

    setTimeout(function () {
      location.href = window.portal_url + "/logout";
    }, logoff_ms);
  } // /Auto LogOff

});

/***/ })
/******/ ]);