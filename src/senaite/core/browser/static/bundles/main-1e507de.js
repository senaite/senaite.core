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
/******/ 	return __webpack_require__(__webpack_require__.s = 0);
/******/ })
/************************************************************************/
/******/ ({

/***/ "./components/i18n.js":
/*!****************************!*\
  !*** ./components/i18n.js ***!
  \****************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! jquery */ \"jquery\");\n/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(jquery__WEBPACK_IMPORTED_MODULE_0__);\n/* i18n integration. This is forked from jarn.jsi18n\n *\n * This is a singleton.\n * Configuration is done on the body tag data-i18ncatalogurl attribute\n *     <body data-i18ncatalogurl=\"/plonejsi18n\">\n *\n *  Or, it'll default to \"/plonejsi18n\"\n */\n\n\nvar I18N = function I18N() {\n  var self = this;\n  self.baseUrl = jquery__WEBPACK_IMPORTED_MODULE_0___default()('body').attr('data-i18ncatalogurl');\n  self.currentLanguage = jquery__WEBPACK_IMPORTED_MODULE_0___default()('html').attr('lang') || 'en'; // Fix for country specific languages\n\n  if (self.currentLanguage.split('-').length > 1) {\n    self.currentLanguage = self.currentLanguage.split('-')[0] + '_' + self.currentLanguage.split('-')[1].toUpperCase();\n  }\n\n  self.storage = null;\n  self.catalogs = {};\n  self.ttl = 24 * 3600 * 1000; // Internet Explorer 8 does not know Date.now() which is used in e.g. loadCatalog, so we \"define\" it\n\n  if (!Date.now) {\n    Date.now = function () {\n      return new Date().valueOf();\n    };\n  }\n\n  try {\n    if ('localStorage' in window && window.localStorage !== null && 'JSON' in window && window.JSON !== null) {\n      self.storage = window.localStorage;\n    }\n  } catch (e) {}\n\n  self.configure = function (config) {\n    for (var key in config) {\n      self[key] = config[key];\n    }\n  };\n\n  self._setCatalog = function (domain, language, catalog) {\n    if (domain in self.catalogs) {\n      self.catalogs[domain][language] = catalog;\n    } else {\n      self.catalogs[domain] = {};\n      self.catalogs[domain][language] = catalog;\n    }\n  };\n\n  self._storeCatalog = function (domain, language, catalog) {\n    var key = domain + '-' + language;\n\n    if (self.storage !== null && catalog !== null) {\n      self.storage.setItem(key, JSON.stringify(catalog));\n      self.storage.setItem(key + '-updated', Date.now());\n    }\n  };\n\n  self.getUrl = function (domain, language) {\n    return self.baseUrl + '?domain=' + domain + '&language=' + language;\n  };\n\n  self.loadCatalog = function (domain, language) {\n    if (language === undefined) {\n      language = self.currentLanguage;\n    }\n\n    if (self.storage !== null) {\n      var key = domain + '-' + language;\n\n      if (key in self.storage) {\n        if (Date.now() - parseInt(self.storage.getItem(key + '-updated'), 10) < self.ttl) {\n          var catalog = JSON.parse(self.storage.getItem(key));\n\n          self._setCatalog(domain, language, catalog);\n\n          return;\n        }\n      }\n    }\n\n    if (!self.baseUrl) {\n      return;\n    }\n\n    jquery__WEBPACK_IMPORTED_MODULE_0___default.a.getJSON(self.getUrl(domain, language), function (catalog) {\n      if (catalog === null) {\n        return;\n      }\n\n      self._setCatalog(domain, language, catalog);\n\n      self._storeCatalog(domain, language, catalog);\n    });\n  };\n\n  self.MessageFactory = function (domain, language) {\n    language = language || self.currentLanguage;\n    return function translate(msgid, keywords) {\n      var msgstr;\n\n      if (domain in self.catalogs && language in self.catalogs[domain] && msgid in self.catalogs[domain][language]) {\n        msgstr = self.catalogs[domain][language][msgid];\n      } else {\n        msgstr = msgid;\n      }\n\n      if (keywords) {\n        var regexp, keyword;\n\n        for (keyword in keywords) {\n          if (keywords.hasOwnProperty(keyword)) {\n            regexp = new RegExp('\\\\$\\\\{' + keyword + '\\\\}', 'g');\n            msgstr = msgstr.replace(regexp, keywords[keyword]);\n          }\n        }\n      }\n\n      return msgstr;\n    };\n  };\n};\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (I18N);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9jb21wb25lbnRzL2kxOG4uanMuanMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9jb21wb25lbnRzL2kxOG4uanM/ZjMxZSJdLCJzb3VyY2VzQ29udGVudCI6WyIvKiBpMThuIGludGVncmF0aW9uLiBUaGlzIGlzIGZvcmtlZCBmcm9tIGphcm4uanNpMThuXG4gKlxuICogVGhpcyBpcyBhIHNpbmdsZXRvbi5cbiAqIENvbmZpZ3VyYXRpb24gaXMgZG9uZSBvbiB0aGUgYm9keSB0YWcgZGF0YS1pMThuY2F0YWxvZ3VybCBhdHRyaWJ1dGVcbiAqICAgICA8Ym9keSBkYXRhLWkxOG5jYXRhbG9ndXJsPVwiL3Bsb25lanNpMThuXCI+XG4gKlxuICogIE9yLCBpdCdsbCBkZWZhdWx0IHRvIFwiL3Bsb25lanNpMThuXCJcbiAqL1xuXG5pbXBvcnQgJCBmcm9tIFwianF1ZXJ5XCI7XG5cblxudmFyIEkxOE4gPSBmdW5jdGlvbigpIHtcbiAgdmFyIHNlbGYgPSB0aGlzO1xuICBzZWxmLmJhc2VVcmwgPSAkKCdib2R5JykuYXR0cignZGF0YS1pMThuY2F0YWxvZ3VybCcpO1xuICBzZWxmLmN1cnJlbnRMYW5ndWFnZSA9ICQoJ2h0bWwnKS5hdHRyKCdsYW5nJykgfHwgJ2VuJztcblxuICAvLyBGaXggZm9yIGNvdW50cnkgc3BlY2lmaWMgbGFuZ3VhZ2VzXG4gIGlmIChzZWxmLmN1cnJlbnRMYW5ndWFnZS5zcGxpdCgnLScpLmxlbmd0aCA+IDEpIHtcbiAgICBzZWxmLmN1cnJlbnRMYW5ndWFnZSA9IHNlbGYuY3VycmVudExhbmd1YWdlLnNwbGl0KCctJylbMF0gKyAnXycgKyBzZWxmLmN1cnJlbnRMYW5ndWFnZS5zcGxpdCgnLScpWzFdLnRvVXBwZXJDYXNlKCk7XG4gIH1cblxuICBzZWxmLnN0b3JhZ2UgPSBudWxsO1xuICBzZWxmLmNhdGFsb2dzID0ge307XG4gIHNlbGYudHRsID0gMjQgKiAzNjAwICogMTAwMDtcblxuICAvLyBJbnRlcm5ldCBFeHBsb3JlciA4IGRvZXMgbm90IGtub3cgRGF0ZS5ub3coKSB3aGljaCBpcyB1c2VkIGluIGUuZy4gbG9hZENhdGFsb2csIHNvIHdlIFwiZGVmaW5lXCIgaXRcbiAgaWYgKCFEYXRlLm5vdykge1xuICAgIERhdGUubm93ID0gZnVuY3Rpb24oKSB7XG4gICAgICByZXR1cm4gbmV3IERhdGUoKS52YWx1ZU9mKCk7XG4gICAgfTtcbiAgfVxuXG4gIHRyeSB7XG4gICAgaWYgKCdsb2NhbFN0b3JhZ2UnIGluIHdpbmRvdyAmJiB3aW5kb3cubG9jYWxTdG9yYWdlICE9PSBudWxsICYmICdKU09OJyBpbiB3aW5kb3cgJiYgd2luZG93LkpTT04gIT09IG51bGwpIHtcbiAgICAgIHNlbGYuc3RvcmFnZSA9IHdpbmRvdy5sb2NhbFN0b3JhZ2U7XG4gICAgfVxuICB9IGNhdGNoIChlKSB7fVxuXG4gIHNlbGYuY29uZmlndXJlID0gZnVuY3Rpb24oY29uZmlnKSB7XG4gICAgZm9yICh2YXIga2V5IGluIGNvbmZpZyl7XG4gICAgICBzZWxmW2tleV0gPSBjb25maWdba2V5XTtcbiAgICB9XG4gIH07XG5cbiAgc2VsZi5fc2V0Q2F0YWxvZyA9IGZ1bmN0aW9uIChkb21haW4sIGxhbmd1YWdlLCBjYXRhbG9nKSB7XG4gICAgaWYgKGRvbWFpbiBpbiBzZWxmLmNhdGFsb2dzKSB7XG4gICAgICBzZWxmLmNhdGFsb2dzW2RvbWFpbl1bbGFuZ3VhZ2VdID0gY2F0YWxvZztcbiAgICB9IGVsc2Uge1xuICAgICAgc2VsZi5jYXRhbG9nc1tkb21haW5dID0ge307XG4gICAgICBzZWxmLmNhdGFsb2dzW2RvbWFpbl1bbGFuZ3VhZ2VdID0gY2F0YWxvZztcbiAgICB9XG4gIH07XG5cbiAgc2VsZi5fc3RvcmVDYXRhbG9nID0gZnVuY3Rpb24gKGRvbWFpbiwgbGFuZ3VhZ2UsIGNhdGFsb2cpIHtcbiAgICB2YXIga2V5ID0gZG9tYWluICsgJy0nICsgbGFuZ3VhZ2U7XG4gICAgaWYgKHNlbGYuc3RvcmFnZSAhPT0gbnVsbCAmJiBjYXRhbG9nICE9PSBudWxsKSB7XG4gICAgICBzZWxmLnN0b3JhZ2Uuc2V0SXRlbShrZXksIEpTT04uc3RyaW5naWZ5KGNhdGFsb2cpKTtcbiAgICAgIHNlbGYuc3RvcmFnZS5zZXRJdGVtKGtleSArICctdXBkYXRlZCcsIERhdGUubm93KCkpO1xuICAgIH1cbiAgfTtcblxuICBzZWxmLmdldFVybCA9IGZ1bmN0aW9uKGRvbWFpbiwgbGFuZ3VhZ2UpIHtcbiAgICByZXR1cm4gc2VsZi5iYXNlVXJsICsgJz9kb21haW49JyArIGRvbWFpbiArICcmbGFuZ3VhZ2U9JyArIGxhbmd1YWdlO1xuICB9O1xuXG4gIHNlbGYubG9hZENhdGFsb2cgPSBmdW5jdGlvbiAoZG9tYWluLCBsYW5ndWFnZSkge1xuICAgIGlmIChsYW5ndWFnZSA9PT0gdW5kZWZpbmVkKSB7XG4gICAgICBsYW5ndWFnZSA9IHNlbGYuY3VycmVudExhbmd1YWdlO1xuICAgIH1cbiAgICBpZiAoc2VsZi5zdG9yYWdlICE9PSBudWxsKSB7XG4gICAgICB2YXIga2V5ID0gZG9tYWluICsgJy0nICsgbGFuZ3VhZ2U7XG4gICAgICBpZiAoa2V5IGluIHNlbGYuc3RvcmFnZSkge1xuICAgICAgICBpZiAoKERhdGUubm93KCkgLSBwYXJzZUludChzZWxmLnN0b3JhZ2UuZ2V0SXRlbShrZXkgKyAnLXVwZGF0ZWQnKSwgMTApKSA8IHNlbGYudHRsKSB7XG4gICAgICAgICAgdmFyIGNhdGFsb2cgPSBKU09OLnBhcnNlKHNlbGYuc3RvcmFnZS5nZXRJdGVtKGtleSkpO1xuICAgICAgICAgIHNlbGYuX3NldENhdGFsb2coZG9tYWluLCBsYW5ndWFnZSwgY2F0YWxvZyk7XG4gICAgICAgICAgcmV0dXJuO1xuICAgICAgICB9XG4gICAgICB9XG4gICAgfVxuICAgIGlmICghc2VsZi5iYXNlVXJsKSB7XG4gICAgICByZXR1cm47XG4gICAgfVxuICAgICQuZ2V0SlNPTihzZWxmLmdldFVybChkb21haW4sIGxhbmd1YWdlKSwgZnVuY3Rpb24gKGNhdGFsb2cpIHtcbiAgICAgIGlmIChjYXRhbG9nID09PSBudWxsKSB7XG4gICAgICAgIHJldHVybjtcbiAgICAgIH1cbiAgICAgIHNlbGYuX3NldENhdGFsb2coZG9tYWluLCBsYW5ndWFnZSwgY2F0YWxvZyk7XG4gICAgICBzZWxmLl9zdG9yZUNhdGFsb2coZG9tYWluLCBsYW5ndWFnZSwgY2F0YWxvZyk7XG4gICAgfSk7XG4gIH07XG5cbiAgc2VsZi5NZXNzYWdlRmFjdG9yeSA9IGZ1bmN0aW9uIChkb21haW4sIGxhbmd1YWdlKSB7XG4gICAgbGFuZ3VhZ2UgPSBsYW5ndWFnZSB8fCBzZWxmLmN1cnJlbnRMYW5ndWFnZTtcbiAgICByZXR1cm4gZnVuY3Rpb24gdHJhbnNsYXRlIChtc2dpZCwga2V5d29yZHMpIHtcbiAgICAgIHZhciBtc2dzdHI7XG4gICAgICBpZiAoKGRvbWFpbiBpbiBzZWxmLmNhdGFsb2dzKSAmJiAobGFuZ3VhZ2UgaW4gc2VsZi5jYXRhbG9nc1tkb21haW5dKSAmJiAobXNnaWQgaW4gc2VsZi5jYXRhbG9nc1tkb21haW5dW2xhbmd1YWdlXSkpIHtcbiAgICAgICAgbXNnc3RyID0gc2VsZi5jYXRhbG9nc1tkb21haW5dW2xhbmd1YWdlXVttc2dpZF07XG4gICAgICB9IGVsc2Uge1xuICAgICAgICBtc2dzdHIgPSBtc2dpZDtcbiAgICAgIH1cbiAgICAgIGlmIChrZXl3b3Jkcykge1xuICAgICAgICB2YXIgcmVnZXhwLCBrZXl3b3JkO1xuICAgICAgICBmb3IgKGtleXdvcmQgaW4ga2V5d29yZHMpIHtcbiAgICAgICAgICBpZiAoa2V5d29yZHMuaGFzT3duUHJvcGVydHkoa2V5d29yZCkpIHtcbiAgICAgICAgICAgIHJlZ2V4cCA9IG5ldyBSZWdFeHAoJ1xcXFwkXFxcXHsnICsga2V5d29yZCArICdcXFxcfScsICdnJyk7XG4gICAgICAgICAgICBtc2dzdHIgPSBtc2dzdHIucmVwbGFjZShyZWdleHAsIGtleXdvcmRzW2tleXdvcmRdKTtcbiAgICAgICAgICB9XG4gICAgICAgIH1cbiAgICAgIH1cbiAgICAgIHJldHVybiBtc2dzdHI7XG4gICAgfTtcbiAgfTtcbn07XG5cbmV4cG9ydCBkZWZhdWx0IEkxOE47XG4iXSwibWFwcGluZ3MiOiJBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFFQTtBQUNBO0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0EiLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./components/i18n.js\n");

/***/ }),

/***/ "./components/sidebar.js":
/*!*******************************!*\
  !*** ./components/sidebar.js ***!
  \*******************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\nfunction _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError(\"Cannot call a class as a function\"); } }\n\nfunction _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if (\"value\" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }\n\nfunction _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }\n\n/* SENAITE Sidebar\n *\n * The sidebar shows when the mouse enters and hides when the mouse leaves the\n * HTML element.\n *\n * It keeps open when the toggle button was clicked.\n */\nvar Sidebar = /*#__PURE__*/function () {\n  function Sidebar(config) {\n    _classCallCheck(this, Sidebar);\n\n    this.config = Object.assign({\n      \"el\": \"sidebar\",\n      \"toggle_el\": \"sidebar-header\",\n      \"cookie_key\": \"sidebar-toggle\",\n      \"timeout\": 1000\n    }, config); // Timer ID\n\n    this.tid = null; // Bind \"this\" context when called\n\n    this.maximize = this.maximize.bind(this);\n    this.minimize = this.minimize.bind(this);\n    this.on_click = this.on_click.bind(this);\n    this.on_mouseenter = this.on_mouseenter.bind(this);\n    this.on_mouseleave = this.on_mouseleave.bind(this); // toggle button handler\n\n    this.toggle_el = document.getElementById(this.config.toggle_el);\n    this.toggle_el.addEventListener(\"click\", this.on_click); // sidebar view/hide handler\n\n    this.el = document.getElementById(this.config.el);\n    this.el.addEventListener(\"mouseenter\", this.on_mouseenter);\n    this.el.addEventListener(\"mouseleave\", this.on_mouseleave);\n\n    if (this.is_toggled()) {\n      this.el.classList.remove(\"minimized\");\n      this.el.classList.add(\"toggled\");\n    }\n\n    return this;\n  }\n\n  _createClass(Sidebar, [{\n    key: \"is_toggled\",\n    value: function is_toggled() {\n      return window.site.read_cookie(this.config.cookie_key) == \"true\";\n    }\n  }, {\n    key: \"toggle\",\n    value: function toggle() {\n      var _toggle = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : false;\n\n      window.site.set_cookie(this.config.cookie_key, _toggle);\n\n      if (_toggle) {\n        this.el.classList.add(\"toggled\");\n        this.maximize();\n      } else {\n        this.el.classList.remove(\"toggled\");\n        this.minimize();\n      }\n    }\n  }, {\n    key: \"minimize\",\n    value: function minimize() {\n      this.el.classList.add(\"minimized\");\n    }\n  }, {\n    key: \"maximize\",\n    value: function maximize() {\n      this.el.classList.remove(\"minimized\");\n    }\n  }, {\n    key: \"on_click\",\n    value: function on_click(event) {\n      // console.debug(\"Sidebar::on_click:event=\", event)\n      clearTimeout(this.tid);\n      this.toggle(!this.is_toggled());\n    }\n  }, {\n    key: \"on_mouseenter\",\n    value: function on_mouseenter(event) {\n      // console.debug(\"Sidebar::on_mouseenter:event=\", event)\n      clearTimeout(this.tid);\n      if (this.is_toggled()) return;\n      this.tid = setTimeout(this.maximize, this.config.timeout);\n    }\n  }, {\n    key: \"on_mouseleave\",\n    value: function on_mouseleave(event) {\n      // console.debug(\"Sidebar::on_mouseleave:event=\", event)\n      clearTimeout(this.tid);\n      if (this.is_toggled()) return;\n      this.minimize(); // console.debug(\"Clearing sidebar timeout\", this.tid);\n    }\n  }]);\n\n  return Sidebar;\n}();\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (Sidebar);//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9jb21wb25lbnRzL3NpZGViYXIuanMuanMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9jb21wb25lbnRzL3NpZGViYXIuanM/MjA4NyJdLCJzb3VyY2VzQ29udGVudCI6WyIvKiBTRU5BSVRFIFNpZGViYXJcbiAqXG4gKiBUaGUgc2lkZWJhciBzaG93cyB3aGVuIHRoZSBtb3VzZSBlbnRlcnMgYW5kIGhpZGVzIHdoZW4gdGhlIG1vdXNlIGxlYXZlcyB0aGVcbiAqIEhUTUwgZWxlbWVudC5cbiAqXG4gKiBJdCBrZWVwcyBvcGVuIHdoZW4gdGhlIHRvZ2dsZSBidXR0b24gd2FzIGNsaWNrZWQuXG4gKi9cblxuY2xhc3MgU2lkZWJhcntcblxuICBjb25zdHJ1Y3Rvcihjb25maWcpIHtcblxuICAgIHRoaXMuY29uZmlnID0gT2JqZWN0LmFzc2lnbih7XG4gICAgICBcImVsXCI6IFwic2lkZWJhclwiLFxuICAgICAgXCJ0b2dnbGVfZWxcIjogXCJzaWRlYmFyLWhlYWRlclwiLFxuICAgICAgXCJjb29raWVfa2V5XCI6IFwic2lkZWJhci10b2dnbGVcIixcbiAgICAgIFwidGltZW91dFwiOiAxMDAwLFxuICAgIH0sIGNvbmZpZyk7XG5cbiAgICAvLyBUaW1lciBJRFxuICAgIHRoaXMudGlkID0gbnVsbDtcblxuICAgIC8vIEJpbmQgXCJ0aGlzXCIgY29udGV4dCB3aGVuIGNhbGxlZFxuICAgIHRoaXMubWF4aW1pemUgPSB0aGlzLm1heGltaXplLmJpbmQodGhpcyk7XG4gICAgdGhpcy5taW5pbWl6ZSA9IHRoaXMubWluaW1pemUuYmluZCh0aGlzKTtcbiAgICB0aGlzLm9uX2NsaWNrID0gdGhpcy5vbl9jbGljay5iaW5kKHRoaXMpO1xuICAgIHRoaXMub25fbW91c2VlbnRlciA9IHRoaXMub25fbW91c2VlbnRlci5iaW5kKHRoaXMpXG4gICAgdGhpcy5vbl9tb3VzZWxlYXZlID0gdGhpcy5vbl9tb3VzZWxlYXZlLmJpbmQodGhpcyk7XG5cbiAgICAvLyB0b2dnbGUgYnV0dG9uIGhhbmRsZXJcbiAgICB0aGlzLnRvZ2dsZV9lbCA9IGRvY3VtZW50LmdldEVsZW1lbnRCeUlkKHRoaXMuY29uZmlnLnRvZ2dsZV9lbCk7XG4gICAgdGhpcy50b2dnbGVfZWwuYWRkRXZlbnRMaXN0ZW5lcihcImNsaWNrXCIsIHRoaXMub25fY2xpY2spO1xuXG4gICAgLy8gc2lkZWJhciB2aWV3L2hpZGUgaGFuZGxlclxuICAgIHRoaXMuZWwgPSBkb2N1bWVudC5nZXRFbGVtZW50QnlJZCh0aGlzLmNvbmZpZy5lbCk7XG4gICAgdGhpcy5lbC5hZGRFdmVudExpc3RlbmVyKFwibW91c2VlbnRlclwiLCB0aGlzLm9uX21vdXNlZW50ZXIpO1xuICAgIHRoaXMuZWwuYWRkRXZlbnRMaXN0ZW5lcihcIm1vdXNlbGVhdmVcIiwgdGhpcy5vbl9tb3VzZWxlYXZlKTtcblxuICAgIGlmICh0aGlzLmlzX3RvZ2dsZWQoKSkge1xuICAgICAgdGhpcy5lbC5jbGFzc0xpc3QucmVtb3ZlKFwibWluaW1pemVkXCIpO1xuICAgICAgdGhpcy5lbC5jbGFzc0xpc3QuYWRkKFwidG9nZ2xlZFwiKTtcbiAgICB9XG5cbiAgICByZXR1cm4gdGhpcztcbiAgfVxuXG4gIGlzX3RvZ2dsZWQoKSB7XG4gICAgcmV0dXJuIHdpbmRvdy5zaXRlLnJlYWRfY29va2llKHRoaXMuY29uZmlnLmNvb2tpZV9rZXkpID09IFwidHJ1ZVwiO1xuICB9XG5cbiAgdG9nZ2xlKHRvZ2dsZT1mYWxzZSkge1xuICAgIHdpbmRvdy5zaXRlLnNldF9jb29raWUodGhpcy5jb25maWcuY29va2llX2tleSwgdG9nZ2xlKVxuICAgIGlmICh0b2dnbGUpIHtcbiAgICAgIHRoaXMuZWwuY2xhc3NMaXN0LmFkZChcInRvZ2dsZWRcIilcbiAgICAgIHRoaXMubWF4aW1pemUoKTtcbiAgICB9IGVsc2Uge1xuICAgICAgdGhpcy5lbC5jbGFzc0xpc3QucmVtb3ZlKFwidG9nZ2xlZFwiKVxuICAgICAgdGhpcy5taW5pbWl6ZSgpO1xuICAgIH1cbiAgfVxuXG4gIG1pbmltaXplKCkge1xuICAgIHRoaXMuZWwuY2xhc3NMaXN0LmFkZChcIm1pbmltaXplZFwiKTtcbiAgfVxuXG4gIG1heGltaXplKCkge1xuICAgIHRoaXMuZWwuY2xhc3NMaXN0LnJlbW92ZShcIm1pbmltaXplZFwiKTtcbiAgfVxuXG4gIG9uX2NsaWNrKGV2ZW50KSB7XG4gICAgLy8gY29uc29sZS5kZWJ1ZyhcIlNpZGViYXI6Om9uX2NsaWNrOmV2ZW50PVwiLCBldmVudClcbiAgICBjbGVhclRpbWVvdXQodGhpcy50aWQpO1xuICAgIHRoaXMudG9nZ2xlKCF0aGlzLmlzX3RvZ2dsZWQoKSk7XG4gIH1cblxuICBvbl9tb3VzZWVudGVyKGV2ZW50KSB7XG4gICAgLy8gY29uc29sZS5kZWJ1ZyhcIlNpZGViYXI6Om9uX21vdXNlZW50ZXI6ZXZlbnQ9XCIsIGV2ZW50KVxuICAgIGNsZWFyVGltZW91dCh0aGlzLnRpZCk7XG4gICAgaWYgKHRoaXMuaXNfdG9nZ2xlZCgpKSByZXR1cm5cbiAgICB0aGlzLnRpZCA9IHNldFRpbWVvdXQodGhpcy5tYXhpbWl6ZSwgdGhpcy5jb25maWcudGltZW91dCk7XG4gIH1cblxuICBvbl9tb3VzZWxlYXZlKGV2ZW50KSB7XG4gICAgLy8gY29uc29sZS5kZWJ1ZyhcIlNpZGViYXI6Om9uX21vdXNlbGVhdmU6ZXZlbnQ9XCIsIGV2ZW50KVxuICAgIGNsZWFyVGltZW91dCh0aGlzLnRpZCk7XG4gICAgaWYgKHRoaXMuaXNfdG9nZ2xlZCgpKSByZXR1cm5cbiAgICB0aGlzLm1pbmltaXplKCk7XG4gICAgLy8gY29uc29sZS5kZWJ1ZyhcIkNsZWFyaW5nIHNpZGViYXIgdGltZW91dFwiLCB0aGlzLnRpZCk7XG4gIH1cbn1cblxuZXhwb3J0IGRlZmF1bHQgU2lkZWJhcjtcbiJdLCJtYXBwaW5ncyI6Ijs7Ozs7OztBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBRUE7QUFFQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBSkE7QUFDQTtBQU9BO0FBQ0E7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFFQTtBQUNBO0FBQ0E7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7OztBQUNBO0FBQ0E7QUFDQTs7O0FBRUE7QUFBQTtBQUNBO0FBQUE7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7OztBQUVBO0FBQ0E7QUFDQTs7O0FBRUE7QUFDQTtBQUNBOzs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBOzs7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7OztBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFFQTs7Ozs7O0FBR0EiLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./components/sidebar.js\n");

/***/ }),

/***/ "./components/site.js":
/*!****************************!*\
  !*** ./components/site.js ***!
  \****************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* WEBPACK VAR INJECTION */(function($) {/* Please use this command to compile this file into the parent `js` directory:\n    coffee --no-header -w -o ../ -c site.coffee\n */\nvar Site,\n    bind = function bind(fn, me) {\n  return function () {\n    return fn.apply(me, arguments);\n  };\n};\n\nSite = function () {\n  /**\n   * Creates a new instance of Site\n   */\n  function Site() {\n    this.set_cookie = bind(this.set_cookie, this);\n    this.read_cookie = bind(this.read_cookie, this);\n    this.authenticator = bind(this.authenticator, this);\n    console.debug(\"Site::init\");\n  }\n  /**\n   * Returns the authenticator value\n   */\n\n\n  Site.prototype.authenticator = function () {\n    var auth, url_params;\n    auth = $(\"input[name='_authenticator']\").val();\n\n    if (!auth) {\n      url_params = new URLSearchParams(window.location.search);\n      auth = url_params.get(\"_authenticator\");\n    }\n\n    return auth;\n  };\n  /**\n   * Reads a cookie value\n   * @param {name} the name of the cookie\n   */\n\n\n  Site.prototype.read_cookie = function (name) {\n    var c, ca, i;\n    console.debug(\"Site::read_cookie:\" + name);\n    name = name + '=';\n    ca = document.cookie.split(';');\n    i = 0;\n\n    while (i < ca.length) {\n      c = ca[i];\n\n      while (c.charAt(0) === ' ') {\n        c = c.substring(1);\n      }\n\n      if (c.indexOf(name) === 0) {\n        return c.substring(name.length, c.length);\n      }\n\n      i++;\n    }\n\n    return null;\n  };\n  /**\n   * Sets a cookie value\n   * @param {name} the name of the cookie\n   * @param {value} the value of the cookie\n   */\n\n\n  Site.prototype.set_cookie = function (name, value) {\n    var d, expires;\n    console.debug(\"Site::set_cookie:name=\" + name + \", value=\" + value);\n    d = new Date();\n    d.setTime(d.getTime() + 1 * 24 * 60 * 60 * 1000);\n    expires = 'expires=' + d.toUTCString();\n    document.cookie = name + '=' + value + ';' + expires + ';path=/';\n  };\n\n  return Site;\n}();\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (Site);\n/* WEBPACK VAR INJECTION */}.call(this, __webpack_require__(/*! jquery */ \"jquery\")))//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9jb21wb25lbnRzL3NpdGUuanMuanMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9jb21wb25lbnRzL3NpdGUuanM/NjE0NyJdLCJzb3VyY2VzQ29udGVudCI6WyJcbi8qIFBsZWFzZSB1c2UgdGhpcyBjb21tYW5kIHRvIGNvbXBpbGUgdGhpcyBmaWxlIGludG8gdGhlIHBhcmVudCBganNgIGRpcmVjdG9yeTpcbiAgICBjb2ZmZWUgLS1uby1oZWFkZXIgLXcgLW8gLi4vIC1jIHNpdGUuY29mZmVlXG4gKi9cbnZhciBTaXRlLFxuICBiaW5kID0gZnVuY3Rpb24oZm4sIG1lKXsgcmV0dXJuIGZ1bmN0aW9uKCl7IHJldHVybiBmbi5hcHBseShtZSwgYXJndW1lbnRzKTsgfTsgfTtcblxuU2l0ZSA9IChmdW5jdGlvbigpIHtcblxuICAvKipcbiAgICogQ3JlYXRlcyBhIG5ldyBpbnN0YW5jZSBvZiBTaXRlXG4gICAqL1xuICBmdW5jdGlvbiBTaXRlKCkge1xuICAgIHRoaXMuc2V0X2Nvb2tpZSA9IGJpbmQodGhpcy5zZXRfY29va2llLCB0aGlzKTtcbiAgICB0aGlzLnJlYWRfY29va2llID0gYmluZCh0aGlzLnJlYWRfY29va2llLCB0aGlzKTtcbiAgICB0aGlzLmF1dGhlbnRpY2F0b3IgPSBiaW5kKHRoaXMuYXV0aGVudGljYXRvciwgdGhpcyk7XG4gICAgY29uc29sZS5kZWJ1ZyhcIlNpdGU6OmluaXRcIik7XG4gIH1cblxuXG4gIC8qKlxuICAgKiBSZXR1cm5zIHRoZSBhdXRoZW50aWNhdG9yIHZhbHVlXG4gICAqL1xuXG4gIFNpdGUucHJvdG90eXBlLmF1dGhlbnRpY2F0b3IgPSBmdW5jdGlvbigpIHtcbiAgICB2YXIgYXV0aCwgdXJsX3BhcmFtcztcbiAgICBhdXRoID0gJChcImlucHV0W25hbWU9J19hdXRoZW50aWNhdG9yJ11cIikudmFsKCk7XG4gICAgaWYgKCFhdXRoKSB7XG4gICAgICB1cmxfcGFyYW1zID0gbmV3IFVSTFNlYXJjaFBhcmFtcyh3aW5kb3cubG9jYXRpb24uc2VhcmNoKTtcbiAgICAgIGF1dGggPSB1cmxfcGFyYW1zLmdldChcIl9hdXRoZW50aWNhdG9yXCIpO1xuICAgIH1cbiAgICByZXR1cm4gYXV0aDtcbiAgfTtcblxuXG4gIC8qKlxuICAgKiBSZWFkcyBhIGNvb2tpZSB2YWx1ZVxuICAgKiBAcGFyYW0ge25hbWV9IHRoZSBuYW1lIG9mIHRoZSBjb29raWVcbiAgICovXG5cbiAgU2l0ZS5wcm90b3R5cGUucmVhZF9jb29raWUgPSBmdW5jdGlvbihuYW1lKSB7XG4gICAgdmFyIGMsIGNhLCBpO1xuICAgIGNvbnNvbGUuZGVidWcoXCJTaXRlOjpyZWFkX2Nvb2tpZTpcIiArIG5hbWUpO1xuICAgIG5hbWUgPSBuYW1lICsgJz0nO1xuICAgIGNhID0gZG9jdW1lbnQuY29va2llLnNwbGl0KCc7Jyk7XG4gICAgaSA9IDA7XG4gICAgd2hpbGUgKGkgPCBjYS5sZW5ndGgpIHtcbiAgICAgIGMgPSBjYVtpXTtcbiAgICAgIHdoaWxlIChjLmNoYXJBdCgwKSA9PT0gJyAnKSB7XG4gICAgICAgIGMgPSBjLnN1YnN0cmluZygxKTtcbiAgICAgIH1cbiAgICAgIGlmIChjLmluZGV4T2YobmFtZSkgPT09IDApIHtcbiAgICAgICAgcmV0dXJuIGMuc3Vic3RyaW5nKG5hbWUubGVuZ3RoLCBjLmxlbmd0aCk7XG4gICAgICB9XG4gICAgICBpKys7XG4gICAgfVxuICAgIHJldHVybiBudWxsO1xuICB9O1xuXG5cbiAgLyoqXG4gICAqIFNldHMgYSBjb29raWUgdmFsdWVcbiAgICogQHBhcmFtIHtuYW1lfSB0aGUgbmFtZSBvZiB0aGUgY29va2llXG4gICAqIEBwYXJhbSB7dmFsdWV9IHRoZSB2YWx1ZSBvZiB0aGUgY29va2llXG4gICAqL1xuXG4gIFNpdGUucHJvdG90eXBlLnNldF9jb29raWUgPSBmdW5jdGlvbihuYW1lLCB2YWx1ZSkge1xuICAgIHZhciBkLCBleHBpcmVzO1xuICAgIGNvbnNvbGUuZGVidWcoXCJTaXRlOjpzZXRfY29va2llOm5hbWU9XCIgKyBuYW1lICsgXCIsIHZhbHVlPVwiICsgdmFsdWUpO1xuICAgIGQgPSBuZXcgRGF0ZTtcbiAgICBkLnNldFRpbWUoZC5nZXRUaW1lKCkgKyAxICogMjQgKiA2MCAqIDYwICogMTAwMCk7XG4gICAgZXhwaXJlcyA9ICdleHBpcmVzPScgKyBkLnRvVVRDU3RyaW5nKCk7XG4gICAgZG9jdW1lbnQuY29va2llID0gbmFtZSArICc9JyArIHZhbHVlICsgJzsnICsgZXhwaXJlcyArICc7cGF0aD0vJztcbiAgfTtcblxuICByZXR1cm4gU2l0ZTtcblxufSkoKTtcblxuZXhwb3J0IGRlZmF1bHQgU2l0ZTtcbiJdLCJtYXBwaW5ncyI6IkFBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFBQTtBQUFBO0FBQUE7QUFDQTtBQUNBO0FBRUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBR0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFHQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBR0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUVBO0FBQ0E7QUFDQTtBIiwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./components/site.js\n");

/***/ }),

/***/ "./i18n-wrapper.js":
/*!*************************!*\
  !*** ./i18n-wrapper.js ***!
  \*************************/
/*! exports provided: _t, _p */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"_t\", function() { return _t; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"_p\", function() { return _p; });\n/* harmony import */ var _components_i18n_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./components/i18n.js */ \"./components/i18n.js\");\n // SENAITE message factory\n\nvar t = null;\nvar _t = function _t(msgid, keywords) {\n  if (t === null) {\n    var i18n = new _components_i18n_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]();\n    console.debug(\"*** Loading `senaite.core` i18n MessageFactory ***\");\n    i18n.loadCatalog(\"senaite.core\");\n    t = i18n.MessageFactory(\"senaite.core\");\n  }\n\n  return t(msgid, keywords);\n}; // Plone message factory\n\nvar p = null;\nvar _p = function _p(msgid, keywords) {\n  if (p === null) {\n    var i18n = new _components_i18n_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]();\n    console.debug(\"*** Loading `plone` i18n MessageFactory ***\");\n    i18n.loadCatalog(\"plone\");\n    p = i18n.MessageFactory(\"plone\");\n  }\n\n  return p(msgid, keywords);\n};//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9pMThuLXdyYXBwZXIuanMuanMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9pMThuLXdyYXBwZXIuanM/NTdlOCJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgSTE4TiBmcm9tIFwiLi9jb21wb25lbnRzL2kxOG4uanNcIjtcblxuLy8gU0VOQUlURSBtZXNzYWdlIGZhY3RvcnlcbnZhciB0ID0gbnVsbDtcbmV4cG9ydCB2YXIgX3QgPSAobXNnaWQsIGtleXdvcmRzKSA9PiB7XG4gIGlmICh0ID09PSBudWxsKSB7XG4gICAgbGV0IGkxOG4gPSBuZXcgSTE4TigpO1xuICAgIGNvbnNvbGUuZGVidWcoXCIqKiogTG9hZGluZyBgc2VuYWl0ZS5jb3JlYCBpMThuIE1lc3NhZ2VGYWN0b3J5ICoqKlwiKTtcbiAgICBpMThuLmxvYWRDYXRhbG9nKFwic2VuYWl0ZS5jb3JlXCIpXG4gICAgdCA9IGkxOG4uTWVzc2FnZUZhY3RvcnkoXCJzZW5haXRlLmNvcmVcIilcbiAgfVxuICByZXR1cm4gdChtc2dpZCwga2V5d29yZHMpO1xufVxuXG4vLyBQbG9uZSBtZXNzYWdlIGZhY3RvcnlcbnZhciBwID0gbnVsbDtcbmV4cG9ydCB2YXIgX3AgPSAobXNnaWQsIGtleXdvcmRzKSA9PiB7XG4gIGlmIChwID09PSBudWxsKSB7XG4gICAgbGV0IGkxOG4gPSBuZXcgSTE4TigpO1xuICAgIGNvbnNvbGUuZGVidWcoXCIqKiogTG9hZGluZyBgcGxvbmVgIGkxOG4gTWVzc2FnZUZhY3RvcnkgKioqXCIpO1xuICAgIGkxOG4ubG9hZENhdGFsb2coXCJwbG9uZVwiKVxuICAgIHAgPSBpMThuLk1lc3NhZ2VGYWN0b3J5KFwicGxvbmVcIilcbiAgfVxuICByZXR1cm4gcChtc2dpZCwga2V5d29yZHMpO1xufVxuIl0sIm1hcHBpbmdzIjoiQUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQ0E7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFFQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBIiwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///./i18n-wrapper.js\n");

/***/ }),

/***/ "./scss/senaite.core.scss":
/*!********************************!*\
  !*** ./scss/senaite.core.scss ***!
  \********************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

eval("// extracted by mini-css-extract-plugin//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zY3NzL3NlbmFpdGUuY29yZS5zY3NzLmpzIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vLy4vc2Nzcy9zZW5haXRlLmNvcmUuc2Nzcz81Y2Y5Il0sInNvdXJjZXNDb250ZW50IjpbIi8vIGV4dHJhY3RlZCBieSBtaW5pLWNzcy1leHRyYWN0LXBsdWdpbiJdLCJtYXBwaW5ncyI6IkFBQUEiLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./scss/senaite.core.scss\n");

/***/ }),

/***/ "./senaite.core.js":
/*!*************************!*\
  !*** ./senaite.core.js ***!
  \*************************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! jquery */ \"jquery\");\n/* harmony import */ var jquery__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(jquery__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _components_i18n_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./components/i18n.js */ \"./components/i18n.js\");\n/* harmony import */ var _i18n_wrapper_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./i18n-wrapper.js */ \"./i18n-wrapper.js\");\n/* harmony import */ var _components_site_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./components/site.js */ \"./components/site.js\");\n/* harmony import */ var _components_sidebar_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./components/sidebar.js */ \"./components/sidebar.js\");\n\n\n\n\n\ndocument.addEventListener(\"DOMContentLoaded\", function () {\n  console.debug(\"*** SENAITE CORE JS LOADED ***\"); // Initialize i18n message factories\n\n  window.i18n = new _components_i18n_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]();\n  window._t = _i18n_wrapper_js__WEBPACK_IMPORTED_MODULE_2__[\"_t\"];\n  window._p = _i18n_wrapper_js__WEBPACK_IMPORTED_MODULE_2__[\"_p\"]; // BBB: set global `portal_url` variable\n\n  window.portal_url = document.body.dataset.portalUrl; // TinyMCE\n\n  tinymce.init({\n    height: 300,\n    selector: \"textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text'],textarea.richTextWidget\",\n    plugins: [\"paste\", \"link\", \"fullscreen\", \"table\", \"code\"],\n    content_css: \"/++plone++senaite.core.static/bundles/main.css\"\n  }); // /TinyMCE\n  // Initialize Site\n\n  window.site = new _components_site_js__WEBPACK_IMPORTED_MODULE_3__[\"default\"](); // Initialize Sidebar\n\n  window.sidebar = new _components_sidebar_js__WEBPACK_IMPORTED_MODULE_4__[\"default\"]({\n    \"el\": \"sidebar\"\n  }); // Tooltips\n\n  jquery__WEBPACK_IMPORTED_MODULE_0___default()(function () {\n    jquery__WEBPACK_IMPORTED_MODULE_0___default()(\"[data-toggle='tooltip']\").tooltip();\n  }); // /Tooltips\n  // Auto LogOff\n\n  var logoff = document.body.dataset.autoLogoff || 0;\n  var logged = document.body.classList.contains(\"userrole-authenticated\"); // Max value for setTimeout is a 32 bit integer\n\n  var max_timeout = Math.pow(2, 31) - 1;\n\n  if (logoff > 0 && logged) {\n    var logoff_ms = logoff * 60 * 1000;\n\n    if (logoff_ms > max_timeout) {\n      console.warn(\"Setting logoff_ms to max value \".concat(max_timeout, \"ms\"));\n      logoff_ms = max_timeout;\n    }\n\n    setTimeout(function () {\n      location.href = window.portal_url + \"/logout\";\n    }, logoff_ms);\n  } // /Auto LogOff\n\n});//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiLi9zZW5haXRlLmNvcmUuanMuanMiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly8vLi9zZW5haXRlLmNvcmUuanM/YTUyZCJdLCJzb3VyY2VzQ29udGVudCI6WyJpbXBvcnQgJCBmcm9tIFwianF1ZXJ5XCI7XG5pbXBvcnQgSTE4TiBmcm9tIFwiLi9jb21wb25lbnRzL2kxOG4uanNcIjtcbmltcG9ydCB7aTE4biwgX3QsIF9wfSBmcm9tIFwiLi9pMThuLXdyYXBwZXIuanNcIlxuaW1wb3J0IFNpdGUgZnJvbSBcIi4vY29tcG9uZW50cy9zaXRlLmpzXCJcbmltcG9ydCBTaWRlYmFyIGZyb20gXCIuL2NvbXBvbmVudHMvc2lkZWJhci5qc1wiXG5cblxuZG9jdW1lbnQuYWRkRXZlbnRMaXN0ZW5lcihcIkRPTUNvbnRlbnRMb2FkZWRcIiwgKCkgPT4ge1xuICBjb25zb2xlLmRlYnVnKFwiKioqIFNFTkFJVEUgQ09SRSBKUyBMT0FERUQgKioqXCIpO1xuXG4gIC8vIEluaXRpYWxpemUgaTE4biBtZXNzYWdlIGZhY3Rvcmllc1xuICB3aW5kb3cuaTE4biA9IG5ldyBJMThOKCk7XG4gIHdpbmRvdy5fdCA9IF90O1xuICB3aW5kb3cuX3AgPSBfcDtcblxuICAvLyBCQkI6IHNldCBnbG9iYWwgYHBvcnRhbF91cmxgIHZhcmlhYmxlXG4gIHdpbmRvdy5wb3J0YWxfdXJsID0gZG9jdW1lbnQuYm9keS5kYXRhc2V0LnBvcnRhbFVybFxuXG4gIC8vIFRpbnlNQ0VcbiAgdGlueW1jZS5pbml0KHtcbiAgICBoZWlnaHQ6IDMwMCxcbiAgICBzZWxlY3RvcjogXCJ0ZXh0YXJlYS5tY2VfZWRpdGFibGUsZGl2LkFyY2hldHlwZXNSaWNoV2lkZ2V0IHRleHRhcmVhLHRleHRhcmVhW25hbWU9J2Zvcm0ud2lkZ2V0cy5JUmljaFRleHRCZWhhdmlvci50ZXh0J10sdGV4dGFyZWEucmljaFRleHRXaWRnZXRcIixcbiAgICBwbHVnaW5zOiBbXCJwYXN0ZVwiLCBcImxpbmtcIiwgXCJmdWxsc2NyZWVuXCIsIFwidGFibGVcIiwgXCJjb2RlXCJdLFxuICAgIGNvbnRlbnRfY3NzIDogXCIvKytwbG9uZSsrc2VuYWl0ZS5jb3JlLnN0YXRpYy9idW5kbGVzL21haW4uY3NzXCIsXG4gIH0pXG4gIC8vIC9UaW55TUNFXG5cbiAgLy8gSW5pdGlhbGl6ZSBTaXRlXG4gIHdpbmRvdy5zaXRlID0gbmV3IFNpdGUoKTtcblxuICAvLyBJbml0aWFsaXplIFNpZGViYXJcbiAgd2luZG93LnNpZGViYXIgPSBuZXcgU2lkZWJhcih7XG4gICAgXCJlbFwiOiBcInNpZGViYXJcIixcbiAgfSk7XG5cblxuICAvLyBUb29sdGlwc1xuICAkKGZ1bmN0aW9uICgpIHtcbiAgICAkKFwiW2RhdGEtdG9nZ2xlPSd0b29sdGlwJ11cIikudG9vbHRpcCgpXG4gIH0pXG4gIC8vIC9Ub29sdGlwc1xuXG4gIC8vIEF1dG8gTG9nT2ZmXG4gIHZhciBsb2dvZmYgPSBkb2N1bWVudC5ib2R5LmRhdGFzZXQuYXV0b0xvZ29mZiB8fCAwO1xuICB2YXIgbG9nZ2VkID0gZG9jdW1lbnQuYm9keS5jbGFzc0xpc3QuY29udGFpbnMoXCJ1c2Vycm9sZS1hdXRoZW50aWNhdGVkXCIpO1xuICAvLyBNYXggdmFsdWUgZm9yIHNldFRpbWVvdXQgaXMgYSAzMiBiaXQgaW50ZWdlclxuICBjb25zdCBtYXhfdGltZW91dCA9IDIqKjMxIC0gMTtcbiAgaWYgKGxvZ29mZiA+IDAgJiYgbG9nZ2VkKSB7XG4gICAgdmFyIGxvZ29mZl9tcyA9IGxvZ29mZiAqIDYwICogMTAwMDtcbiAgICBpZiAobG9nb2ZmX21zID4gbWF4X3RpbWVvdXQpIHtcbiAgICAgIGNvbnNvbGUud2FybihgU2V0dGluZyBsb2dvZmZfbXMgdG8gbWF4IHZhbHVlICR7bWF4X3RpbWVvdXR9bXNgKTtcbiAgICAgIGxvZ29mZl9tcyA9IG1heF90aW1lb3V0O1xuICAgIH1cbiAgICBzZXRUaW1lb3V0KGZ1bmN0aW9uKCkge1xuICAgICAgbG9jYXRpb24uaHJlZiA9IHdpbmRvdy5wb3J0YWxfdXJsICsgXCIvbG9nb3V0XCI7XG4gICAgfSwgbG9nb2ZmX21zKTtcbiAgfVxuICAvLyAvQXV0byBMb2dPZmZcblxufSk7XG4iXSwibWFwcGluZ3MiOiJBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFBQTtBQUFBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUdBO0FBQ0E7QUFDQTtBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBRUE7QUFDQTtBQUVBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFKQTtBQVFBO0FBQ0E7QUFBQTtBQUNBO0FBRUE7QUFDQTtBQURBO0FBQ0E7QUFLQTtBQUNBO0FBQ0E7QUFHQTtBQUNBO0FBQUE7QUFDQTtBQUNBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUFBO0FBQ0E7QUFDQTtBQUNBO0FBQ0E7QUFBQTtBQUNBO0FBQ0E7QUFDQTtBQUNBO0FBRUEiLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///./senaite.core.js\n");

/***/ }),

/***/ 0:
/*!********************************************************!*\
  !*** multi ./senaite.core.js ./scss/senaite.core.scss ***!
  \********************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(/*! ./senaite.core.js */"./senaite.core.js");
module.exports = __webpack_require__(/*! ./scss/senaite.core.scss */"./scss/senaite.core.scss");


/***/ }),

/***/ "jquery":
/*!*************************!*\
  !*** external "jQuery" ***!
  \*************************/
/*! no static exports found */
/***/ (function(module, exports) {

eval("module.exports = jQuery;//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoianF1ZXJ5LmpzIiwic291cmNlcyI6WyJ3ZWJwYWNrOi8vL2V4dGVybmFsIFwialF1ZXJ5XCI/Y2QwYyJdLCJzb3VyY2VzQ29udGVudCI6WyJtb2R1bGUuZXhwb3J0cyA9IGpRdWVyeTsiXSwibWFwcGluZ3MiOiJBQUFBIiwic291cmNlUm9vdCI6IiJ9\n//# sourceURL=webpack-internal:///jquery\n");

/***/ })

/******/ });