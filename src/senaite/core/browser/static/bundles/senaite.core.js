/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 311:
/***/ ((module) => {

module.exports = jQuery;

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other entry modules.
(() => {

// EXTERNAL MODULE: external "jQuery"
var external_jQuery_ = __webpack_require__(311);
var external_jQuery_default = /*#__PURE__*/__webpack_require__.n(external_jQuery_);
;// CONCATENATED MODULE: ./components/i18n.js
/* i18n integration. This is forked from jarn.jsi18n
 *
 * This is a singleton.
 * Configuration is done on the body tag data-i18ncatalogurl attribute
 *     <body data-i18ncatalogurl="/plonejsi18n">
 *
 *  Or, it'll default to "/plonejsi18n"
 */


var I18N = function I18N() {
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

    external_jQuery_default().getJSON(self.getUrl(domain, language), function (catalog) {
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

/* harmony default export */ const components_i18n = (I18N);
;// CONCATENATED MODULE: ./i18n-wrapper.js
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
var _p = function _p(msgid, keywords) {
  if (p === null) {
    var i18n = new components_i18n();
    console.debug("*** Loading `plone` i18n MessageFactory ***");
    i18n.loadCatalog("plone");
    p = i18n.MessageFactory("plone");
  }

  return p(msgid, keywords);
};
;// CONCATENATED MODULE: ./components/editform.js
var _excluded = ["name", "error"],
    _excluded2 = ["message", "level"],
    _excluded3 = ["title", "message"],
    _excluded4 = ["name"],
    _excluded5 = ["name"],
    _excluded6 = ["name", "message"],
    _excluded7 = ["name", "message"],
    _excluded8 = ["name", "value"],
    _excluded9 = ["selector", "html"],
    _excluded10 = ["selector", "name", "value"];

function _slicedToArray(arr, i) { return _arrayWithHoles(arr) || _iterableToArrayLimit(arr, i) || _unsupportedIterableToArray(arr, i) || _nonIterableRest(); }

function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _iterableToArrayLimit(arr, i) { var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"]; if (_i == null) return; var _arr = []; var _n = true; var _d = false; var _s, _e; try { for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function _arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function _toConsumableArray(arr) { return _arrayWithoutHoles(arr) || _iterableToArray(arr) || _unsupportedIterableToArray(arr) || _nonIterableSpread(); }

function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function _iterableToArray(iter) { if (typeof Symbol !== "undefined" && iter[Symbol.iterator] != null || iter["@@iterator"] != null) return Array.from(iter); }

function _arrayWithoutHoles(arr) { if (Array.isArray(arr)) return _arrayLikeToArray(arr); }

function _objectWithoutProperties(source, excluded) { if (source == null) return {}; var target = _objectWithoutPropertiesLoose(source, excluded); var key, i; if (Object.getOwnPropertySymbols) { var sourceSymbolKeys = Object.getOwnPropertySymbols(source); for (i = 0; i < sourceSymbolKeys.length; i++) { key = sourceSymbolKeys[i]; if (excluded.indexOf(key) >= 0) continue; if (!Object.prototype.propertyIsEnumerable.call(source, key)) continue; target[key] = source[key]; } } return target; }

function _objectWithoutPropertiesLoose(source, excluded) { if (source == null) return {}; var target = {}; var sourceKeys = Object.keys(source); var key, i; for (i = 0; i < sourceKeys.length; i++) { key = sourceKeys[i]; if (excluded.indexOf(key) >= 0) continue; target[key] = source[key]; } return target; }

function _createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = _unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e2) { throw _e2; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e3) { didErr = true; err = _e3; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function _unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return _arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return _arrayLikeToArray(o, minLen); }

function _arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); return Constructor; }

/* SENAITE Edit Form Handler
 *
 * This code handles field changes in edit forms and updates others according to
 * the changes with the help of adapters.
 *
 */
// needed for Bootstrap toasts


var EditForm = /*#__PURE__*/function () {
  function EditForm(config) {
    _classCallCheck(this, EditForm);

    this.config = Object.assign({
      "form_selectors": [],
      "field_selectors": []
    }, config);
    this.hooked_fields = []; // bind event handlers

    this.on_mutated = this.on_mutated.bind(this);
    this.on_modified = this.on_modified.bind(this);
    this.on_submit = this.on_submit.bind(this);
    this.on_blur = this.on_blur.bind(this);
    this.on_click = this.on_click.bind(this);
    this.on_change = this.on_change.bind(this);
    this.init_forms();
  }
  /**
   * Initialize all form elements given by the config
   */


  _createClass(EditForm, [{
    key: "init_forms",
    value: function init_forms() {
      var selectors = this.config.form_selectors;

      var _iterator = _createForOfIteratorHelper(selectors),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var selector = _step.value;
          var form = document.querySelector(selector);

          if (form && form.tagName === "FORM") {
            this.setup_form(form);
            this.watch_form(form);
          }
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }
    }
    /**
     * Trigger `initialized` event on the form element
     */

  }, {
    key: "setup_form",
    value: function setup_form(form) {
      console.debug("EditForm::setup_form(".concat(form, ")"));
      this.ajax_send(form, {}, "initialized");
    }
    /**
     * Bind event handlers on form fields to monitor changes
     */

  }, {
    key: "watch_form",
    value: function watch_form(form) {
      console.debug("EditForm::watch_form(".concat(form, ")"));
      var fields = this.get_form_fields(form);

      var _iterator2 = _createForOfIteratorHelper(fields),
          _step2;

      try {
        for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
          var field = _step2.value;
          this.hook_field(field);
        } // observe DOM mutations in form

      } catch (err) {
        _iterator2.e(err);
      } finally {
        _iterator2.f();
      }

      this.observe_mutations(form); // bind custom form event handlers

      form.addEventListener("modified", this.on_modified);
      form.addEventListener("mutated", this.on_mutated);

      if (form.hasAttribute("ajax-submit")) {
        form.addEventListener("submit", this.on_submit);
      }
    }
    /**
     * Bind event handlers to field
     */

  }, {
    key: "hook_field",
    value: function hook_field(field) {
      // return immediately if the fields is already hooked
      if (this.hooked_fields.indexOf(field) !== -1) {
        // console.debug(`Field '${field.name}' is already hooked`);
        return;
      }

      if (this.is_button(field) || this.is_input_button(field)) {
        // bind click event
        field.addEventListener("click", this.on_click);
      } else if (this.is_text(field) || this.is_textarea(field) || this.is_select(field)) {
        // bind change event
        field.addEventListener("change", this.on_change);
      } else if (this.is_radio(field) || this.is_checkbox(field)) {
        // bind click event
        field.addEventListener("click", this.on_click);
      } else {
        // bind blur event
        field.addEventListener("blur", this.on_blur);
      } // console.debug(`Hooked field '${field.name}'`);
      // remember hooked fields


      this.hooked_fields = this.hooked_fields.concat(field);
    }
    /**
     * Initialize a DOM mutation observer to rebind dynamic added fields,
     * e.g. for records field etc.
     */

  }, {
    key: "observe_mutations",
    value: function observe_mutations(form) {
      var observer = new MutationObserver(function (mutations) {
        var event = new CustomEvent("mutated", {
          detail: {
            form: form,
            mutations: mutations
          }
        });
        form.dispatchEvent(event);
      }); // observe the form with all contained elements

      observer.observe(form, {
        childList: true,
        subtree: true
      });
    }
    /**
     * Handle a single DOM mutation
     */

  }, {
    key: "handle_mutation",
    value: function handle_mutation(form, mutation) {
      var target = mutation.target;
      var parent = target.closest(".field");
      var added = mutation.addedNodes;
      var removed = mutation.removedNodes;
      var selectors = this.config.field_selectors; // handle picklist widget

      if (this.is_multiple_select(target)) {
        return this.notify(form, target, "modified");
      } // hook new fields, e.g. when the records field "More" button was clicked


      if (added && target.ELEMENT_NODE) {
        var _iterator3 = _createForOfIteratorHelper(target.querySelectorAll(selectors)),
            _step3;

        try {
          for (_iterator3.s(); !(_step3 = _iterator3.n()).done;) {
            var field = _step3.value;
            this.hook_field(field);
          }
        } catch (err) {
          _iterator3.e(err);
        } finally {
          _iterator3.f();
        }
      }
    }
    /**
     * toggles the submit button
     */

  }, {
    key: "toggle_submit",
    value: function toggle_submit(form, toggle) {
      var btn = form.querySelector("input[type='submit']");
      btn.disabled = !toggle;
    }
    /**
     * toggles the display of the field with the `d-none` class
     */

  }, {
    key: "toggle_field_visibility",
    value: function toggle_field_visibility(field) {
      var toggle = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : true;
      var parent = field.closest(".field");
      var css_class = "d-none";

      if (toggle === false) {
        parent.classList.add(css_class);
      } else {
        parent.classList.remove(css_class);
      }
    }
    /**
     * check if fields have errors
     */

  }, {
    key: "has_field_errors",
    value: function has_field_errors(form) {
      var fields_with_errors = form.querySelectorAll(".is-invalid");

      if (fields_with_errors.length > 0) {
        return true;
      }

      return false;
    }
    /**
     * set field readonly
     */

  }, {
    key: "set_field_readonly",
    value: function set_field_readonly(field) {
      var message = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      field.setAttribute("readonly", "");
      var existing_message = field.parentElement.querySelector("div.message");

      if (existing_message) {
        existing_message.innerHTML = _t(message);
      } else {
        var div = document.createElement("div");
        div.className = "message text-secondary small";
        div.innerHTML = _t(message);
        field.parentElement.appendChild(div);
      }
    }
    /**
     * set field editable
     */

  }, {
    key: "set_field_editable",
    value: function set_field_editable(field) {
      var message = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : null;
      field.removeAttribute("readonly");
      var existing_message = field.parentElement.querySelector("div.message");

      if (existing_message) {
        existing_message.innerHTML = _t(message);
      } else {
        var div = document.createElement("div");
        div.className = "message text-secondary small";
        div.innerHTML = _t(message);
        field.parentElement.appendChild(div);
      }
    }
    /**
     * set field error
     */

  }, {
    key: "set_field_error",
    value: function set_field_error(field, message) {
      field.classList.add("is-invalid");
      var existing_message = field.parentElement.querySelector("div.invalid-feedback");

      if (existing_message) {
        existing_message.innerHTML = _t(message);
      } else {
        var div = document.createElement("div");
        div.className = "invalid-feedback";
        div.innerHTML = _t(message);
        field.parentElement.appendChild(div);
      }
    }
    /**
     * remove field error
     */

  }, {
    key: "remove_field_error",
    value: function remove_field_error(field) {
      field.classList.remove("is-invalid");
      var msg = field.parentElement.querySelector(".invalid-feedback");

      if (msg) {
        msg.remove();
      }
    }
    /**
     * add a status message
     * @param {string} message the message to display in the alert
     * @param {string} level   one of "info", "success", "warning", "danger"
     * @param {object} options additional options to control the behavior
     *                 - option {string} title: alert title in bold
     *                 - option {string} flush: remove previous alerts
     */

  }, {
    key: "add_statusmessage",
    value: function add_statusmessage(message) {
      var level = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : "info";
      var options = arguments.length > 2 ? arguments[2] : undefined;
      options = options || {};
      var el = document.createElement("div");
      var title = options.title || "".concat(level.charAt(0).toUpperCase() + level.slice(1));
      el.innerHTML = "\n      <div class=\"alert alert-".concat(level, " alert-dismissible fade show\" role=\"alert\">\n        <strong>").concat(title, "</strong>\n        ").concat(_t(message), "\n        <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\">\n          <span aria-hidden=\"true\">&times;</span>\n        </button>\n      </div>\n    ");
      el = el.firstElementChild;
      var parent = document.getElementById("viewlet-above-content"); // clear put previous alerts

      if (options.flush) {
        var _iterator4 = _createForOfIteratorHelper(parent.querySelectorAll(".alert")),
            _step4;

        try {
          for (_iterator4.s(); !(_step4 = _iterator4.n()).done;) {
            var _el = _step4.value;

            _el.remove();
          }
        } catch (err) {
          _iterator4.e(err);
        } finally {
          _iterator4.f();
        }
      }

      parent.appendChild(el);
      return el;
    }
    /**
     * add a notification message
     */

  }, {
    key: "add_notification",
    value: function add_notification(title, message, options) {
      options = options || {};
      options = Object.assign({
        animation: true,
        autohide: true,
        delay: 5000
      }, options);
      var el = document.createElement("div");
      el.innerHTML = "\n      <div class=\"toast\" style=\"width:300px\" role=\"alert\"\n           data-animation=\"".concat(options.animation, "\"\n           data-autohide=\"").concat(options.autohide, "\"\n           data-delay=\"").concat(options.delay, "\">\n        <div class=\"toast-header\">\n          <strong class=\"mr-auto\">").concat(title.charAt(0).toUpperCase() + title.slice(1), "</strong>\n          <button type=\"button\" class=\"ml-2 mb-1 close\" data-dismiss=\"toast\" aria-label=\"Close\">\n            <span aria-hidden=\"true\">&times;</span>\n          </button>\n        </div>\n        <div class=\"toast-body\">\n          ").concat(_t(message), "\n        </div>\n      </div>\n    ");
      el = el.firstElementChild;
      var parent = document.querySelector(".toast-container");

      if (!parent) {
        parent = document.createElement("div");
        parent.innerHTML = "\n        <div style=\"position: fixed; top: 0px; right: 0px; width=100%;\">\n          <div class=\"toast-container\" style=\"position: absolute; top: 10px; right: 10px;\">\n          </div>\n        </div>\n      ";
        var wrapper = document.querySelector(".container-fluid");
        wrapper.appendChild(parent);
        parent = parent.querySelector(".toast-container");
      }

      parent.appendChild(el);
      return el;
    }
    /**
     * update the form with the response from the server
     */

  }, {
    key: "update_form",
    value: function update_form(form, data) {
      console.info("*** UPDATE FORM ***", data);
      var hide = data.hide || [];
      var show = data.show || [];
      var readonly = data.readonly || [];
      var editable = data.editable || [];
      var errors = data.errors || [];
      var messages = data.messages || [];
      var notifications = data.notifications || [];
      var updates = data.updates || [];
      var html = data.html || [];
      var attributes = data.attributes || []; // render field errors

      var _iterator5 = _createForOfIteratorHelper(errors),
          _step5;

      try {
        for (_iterator5.s(); !(_step5 = _iterator5.n()).done;) {
          var record = _step5.value;
          var name = void 0,
              error = void 0,
              rest = void 0;
          var _record = record;
          name = _record.name;
          error = _record.error;
          rest = _objectWithoutProperties(_record, _excluded);
          _record;
          var el = this.get_form_field_by_name(form, name);
          if (!el) continue;

          if (error) {
            this.set_field_error(el, error);
          } else {
            this.remove_field_error(el);
          }
        } // render status messages

      } catch (err) {
        _iterator5.e(err);
      } finally {
        _iterator5.f();
      }

      var _iterator6 = _createForOfIteratorHelper(messages),
          _step6;

      try {
        for (_iterator6.s(); !(_step6 = _iterator6.n()).done;) {
          var _record2 = _step6.value;

          var _name = void 0,
              _error = void 0,
              rest = void 0;

          var _record3 = _record2;
          message = _record3.message;
          level = _record3.level;
          rest = _objectWithoutProperties(_record3, _excluded2);
          _record3;
          var level = level || "info";
          var message = message || "";
          this.add_statusmessage(message, level, rest);
        } // render notification messages

      } catch (err) {
        _iterator6.e(err);
      } finally {
        _iterator6.f();
      }

      var _iterator7 = _createForOfIteratorHelper(notifications),
          _step7;

      try {
        for (_iterator7.s(); !(_step7 = _iterator7.n()).done;) {
          var _record4 = _step7.value;

          var title = void 0,
              _message = void 0,
              rest = void 0;

          var _record5 = _record4;
          title = _record5.title;
          _message = _record5.message;
          rest = _objectWithoutProperties(_record5, _excluded3);
          _record5;

          var _el2 = this.add_notification(title, _message, rest);

          external_jQuery_default()(_el2).toast("show");
        } // hide fields

      } catch (err) {
        _iterator7.e(err);
      } finally {
        _iterator7.f();
      }

      var _iterator8 = _createForOfIteratorHelper(hide),
          _step8;

      try {
        for (_iterator8.s(); !(_step8 = _iterator8.n()).done;) {
          var _record6 = _step8.value;

          var _name2 = void 0,
              rest = void 0;

          var _record7 = _record6;
          _name2 = _record7.name;
          rest = _objectWithoutProperties(_record7, _excluded4);
          _record7;

          var _el3 = this.get_form_field_by_name(form, _name2);

          if (!_el3) continue;
          this.toggle_field_visibility(_el3, false);
        } // show fields

      } catch (err) {
        _iterator8.e(err);
      } finally {
        _iterator8.f();
      }

      var _iterator9 = _createForOfIteratorHelper(show),
          _step9;

      try {
        for (_iterator9.s(); !(_step9 = _iterator9.n()).done;) {
          var _record8 = _step9.value;

          var _name3 = void 0,
              rest = void 0;

          var _record9 = _record8;
          _name3 = _record9.name;
          rest = _objectWithoutProperties(_record9, _excluded5);
          _record9;

          var _el4 = this.get_form_field_by_name(form, _name3);

          if (!_el4) continue;
          this.toggle_field_visibility(_el4, true);
        } // readonly fields

      } catch (err) {
        _iterator9.e(err);
      } finally {
        _iterator9.f();
      }

      var _iterator10 = _createForOfIteratorHelper(readonly),
          _step10;

      try {
        for (_iterator10.s(); !(_step10 = _iterator10.n()).done;) {
          var _record10 = _step10.value;

          var _name4 = void 0,
              _message2 = void 0,
              rest = void 0;

          var _record11 = _record10;
          _name4 = _record11.name;
          _message2 = _record11.message;
          rest = _objectWithoutProperties(_record11, _excluded6);
          _record11;

          var _el5 = this.get_form_field_by_name(form, _name4);

          if (!_el5) continue;
          this.set_field_readonly(_el5, _message2);
        } // editable fields

      } catch (err) {
        _iterator10.e(err);
      } finally {
        _iterator10.f();
      }

      var _iterator11 = _createForOfIteratorHelper(editable),
          _step11;

      try {
        for (_iterator11.s(); !(_step11 = _iterator11.n()).done;) {
          var _record12 = _step11.value;

          var _name5 = void 0,
              _message3 = void 0,
              rest = void 0;

          var _record13 = _record12;
          _name5 = _record13.name;
          _message3 = _record13.message;
          rest = _objectWithoutProperties(_record13, _excluded7);
          _record13;

          var _el6 = this.get_form_field_by_name(form, _name5);

          if (!_el6) continue;
          this.set_field_editable(_el6, _message3);
        } // updated fields

      } catch (err) {
        _iterator11.e(err);
      } finally {
        _iterator11.f();
      }

      var _iterator12 = _createForOfIteratorHelper(updates),
          _step12;

      try {
        for (_iterator12.s(); !(_step12 = _iterator12.n()).done;) {
          var _record14 = _step12.value;

          var _name6 = void 0,
              value = void 0,
              rest = void 0;

          var _record15 = _record14;
          _name6 = _record15.name;
          value = _record15.value;
          rest = _objectWithoutProperties(_record15, _excluded8);
          _record15;

          var _el7 = this.get_form_field_by_name(form, _name6);

          if (!_el7) continue;
          this.set_field_value(_el7, value);
        } // html

      } catch (err) {
        _iterator12.e(err);
      } finally {
        _iterator12.f();
      }

      var _iterator13 = _createForOfIteratorHelper(html),
          _step13;

      try {
        for (_iterator13.s(); !(_step13 = _iterator13.n()).done;) {
          var _record16 = _step13.value;

          var selector = void 0,
              _html = void 0,
              rest = void 0;

          var _record17 = _record16;
          selector = _record17.selector;
          _html = _record17.html;
          rest = _objectWithoutProperties(_record17, _excluded9);
          _record17;

          var _el8 = form.querySelector(selector);

          if (!_el8) continue;

          if (rest.append) {
            _el8.innerHTML = _el8.innerHTML + _html;
          } else {
            _el8.innerHTML = _html;
          }
        } // set attribute to an element

      } catch (err) {
        _iterator13.e(err);
      } finally {
        _iterator13.f();
      }

      var _iterator14 = _createForOfIteratorHelper(attributes),
          _step14;

      try {
        for (_iterator14.s(); !(_step14 = _iterator14.n()).done;) {
          var _record18 = _step14.value;

          var _selector = void 0,
              _name7 = void 0,
              _value = void 0,
              rest = void 0;

          var _record19 = _record18;
          _selector = _record19.selector;
          _name7 = _record19.name;
          _value = _record19.value;
          rest = _objectWithoutProperties(_record19, _excluded10);
          _record19;

          var _el9 = form.querySelector(_selector);

          if (!_el9) continue;

          if (_value === null) {
            _el9.removeAttribute(_name7);
          } else {
            _el9.addAttribute(_name7, _value);
          }
        } // disallow submit when field errors are present

      } catch (err) {
        _iterator14.e(err);
      } finally {
        _iterator14.f();
      }

      if (this.has_field_errors(form)) {
        this.toggle_submit(form, false);
      } else {
        this.toggle_submit(form, true);
      }
    }
    /**
     * return a form field by name
     */

  }, {
    key: "get_form_field_by_name",
    value: function get_form_field_by_name(form, name) {
      // get the first element that matches the name
      var exact = form.querySelector("[name='".concat(name, "']"));
      var fuzzy = form.querySelector("[name^='".concat(name, "']"));
      var field = exact || fuzzy || null;

      if (field === null) {
        return null;
      }

      return field;
    }
    /**
     * return a dictionary of all the form values
     */

  }, {
    key: "get_form_data",
    value: function get_form_data(form) {
      var data = {};
      var form_data = new FormData(form);
      form_data.forEach(function (value, key) {
        data[key] = value;
      });
      return data;
    }
    /**
     * Return form fields for the given selectors of the config
     */

  }, {
    key: "get_form_fields",
    value: function get_form_fields(form) {
      console.debug("EditForm::get_form_fields(".concat(form, ")"));
      var fields = [];
      var selectors = this.config.field_selectors;

      var _iterator15 = _createForOfIteratorHelper(selectors),
          _step15;

      try {
        for (_iterator15.s(); !(_step15 = _iterator15.n()).done;) {
          var _fields;

          var selector = _step15.value;
          var nodes = form.querySelectorAll(selector);
          fields = (_fields = fields).concat.apply(_fields, _toConsumableArray(nodes.values()));
        }
      } catch (err) {
        _iterator15.e(err);
      } finally {
        _iterator15.f();
      }

      return fields;
    }
    /**
     * returns the name of the field w/o ZPublisher converter
     */

  }, {
    key: "get_field_name",
    value: function get_field_name(field) {
      var name = field.name;
      return name.split(":")[0];
    }
    /**
     * return the value of the form field
     */

  }, {
    key: "get_field_value",
    value: function get_field_value(field) {
      if (this.is_checkbox(field)) {
        // returns true/false for checkboxes
        return field.checked;
      } else if (this.is_select(field)) {
        // returns a list of selected option
        var selected = field.selectedOptions;
        return Array.prototype.map.call(selected, function (option) {
          return option.value;
        });
      } else if (this.is_single_reference(field)) {
        // returns the value of the `uid` attribute
        return field.getAttribute("uid");
      } else if (this.is_multi_reference(field)) {
        // returns the value of the `uid` attribute and splits it on `,`
        var uids = field.getAttribute("uid");
        if (uids.length == 0) return [];
        return uids.split(",");
      } // return the plain field value


      return field.value;
    }
    /**
     * set the value of the form field
     */

  }, {
    key: "set_field_value",
    value: function set_field_value(field, value) {
      // for reference/select fields
      var selected = value.selected || [];
      var options = value.options || []; // set reference value

      if (this.is_single_reference(field)) {
        var _iterator16 = _createForOfIteratorHelper(selected),
            _step16;

        try {
          for (_iterator16.s(); !(_step16 = _iterator16.n()).done;) {
            var item = _step16.value;
            field.setAttribute("uid", item.value);
            field.value = item.title;
          }
        } catch (err) {
          _iterator16.e(err);
        } finally {
          _iterator16.f();
        }
      } // set select field
      else if (this.is_select(field)) {
        if (selected.length == 0) {
          var old_selected = field.options[field.selected];

          if (old_selected) {
            selected = [old_selected.value];
          }
        } // remove all options


        field.options.length = 0; // sort options

        options.sort(function (a, b) {
          var _a = a.title.toLowerCase();

          var _b = b.title.toLowerCase();

          if (a.value === null) _a = "";
          if (b.value === null) _b = "";
          if (_a < _b) return -1;
          if (_a > _b) return 1;
        }); // build new options

        var _iterator17 = _createForOfIteratorHelper(options),
            _step17;

        try {
          for (_iterator17.s(); !(_step17 = _iterator17.n()).done;) {
            var option = _step17.value;
            var el = document.createElement("option");
            el.value = option.value;
            el.innerHTML = option.title; // select item if the value is in the selected array

            if (selected.indexOf(option.value) !== -1) {
              el.selected = true;
            }

            field.appendChild(el);
          } // select first item

        } catch (err) {
          _iterator17.e(err);
        } finally {
          _iterator17.f();
        }

        if (selected.length == 0) {
          field.selectedIndex = 0;
        }
      } // set checkbox value
      else if (this.is_checkbox(field)) {
        field.checked = value;
      } // set other field values
      else {
        field.value = value;
      }
    }
    /**
     * trigger `modified` event on the form
     */

  }, {
    key: "modified",
    value: function modified(el) {
      var event = new CustomEvent("modified", {
        detail: {
          field: el,
          form: el.form
        }
      }); // dispatch the event on the element

      el.form.dispatchEvent(event);
    }
    /**
     * trigger ajax loading events
     */

  }, {
    key: "loading",
    value: function loading() {
      var toggle = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : true;
      var event_type = toggle ? "ajaxStart" : "ajaxStop";
      var event = new CustomEvent(event_type);
      document.dispatchEvent(event);
    }
    /**
     * notify a field change to the server ajax endpoint
     */

  }, {
    key: "notify",
    value: function notify(form, field, endpoint) {
      var data = {
        name: this.get_field_name(field),
        value: this.get_field_value(field)
      };
      this.ajax_send(form, data, endpoint);
    }
    /**
     * send application/json to the server
     */

  }, {
    key: "ajax_send",
    value: function ajax_send(form, data, endpoint) {
      var view_url = document.body.dataset.viewUrl;
      var ajax_url = "".concat(view_url, "/ajax_form/").concat(endpoint);
      var payload = Object.assign({
        "form": this.get_form_data(form)
      }, data);
      console.debug("EditForm::ajax_send --> ", payload);
      var init = {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(payload),
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-TOKEN": document.querySelector("#protect-script").dataset.token
        }
      };
      return this.ajax_request(form, ajax_url, init);
    }
    /**
     * send multipart/form-data to the server
     */

  }, {
    key: "ajax_submit",
    value: function ajax_submit(form, data, endpoint) {
      var view_url = document.body.dataset.viewUrl;
      var ajax_url = "".concat(view_url, "/ajax_form/").concat(endpoint);
      var payload = new FormData(form); // update form data

      for (var _i = 0, _Object$entries = Object.entries(data); _i < _Object$entries.length; _i++) {
        var _Object$entries$_i = _slicedToArray(_Object$entries[_i], 2),
            key = _Object$entries$_i[0],
            value = _Object$entries$_i[1];

        payload.set(key, value);
      }

      console.debug("EditForm::ajax_submit --> ", payload);
      var init = {
        method: "POST",
        body: payload
      };
      return this.ajax_request(form, ajax_url, init);
    }
    /**
     * execute ajax request
     */

  }, {
    key: "ajax_request",
    value: function ajax_request(form, url, init) {
      var _this = this;

      // send ajax request to server
      this.loading(true);
      var request = new Request(url, init);
      return fetch(request).then(function (response) {
        if (!response.ok) {
          return Promise.reject(response);
        }

        return response.json();
      }).then(function (data) {
        console.debug("EditForm::ajax_request --> ", data);

        _this.update_form(form, data);

        _this.loading(false);
      })["catch"](function (error) {
        console.error(error);

        _this.loading(false);
      });
    }
    /**
     * Toggle element disable
     */

  }, {
    key: "toggle_disable",
    value: function toggle_disable(el, toggle) {
      if (el) {
        el.disabled = toggle;
      }
    }
    /**
     * Checks if the element is a textarea field
     */

  }, {
    key: "is_textarea",
    value: function is_textarea(el) {
      return el.tagName == "TEXTAREA";
    }
    /**
     * Checks if the elment is a select field
     */

  }, {
    key: "is_select",
    value: function is_select(el) {
      return el.tagName == "SELECT";
    }
    /**
     * Checks if the element is a multiple select field
     */

  }, {
    key: "is_multiple_select",
    value: function is_multiple_select(el) {
      return this.is_select(el) && el.hasAttribute("multiple");
    }
    /**
     * Checks if the element is an input field
     */

  }, {
    key: "is_input",
    value: function is_input(el) {
      return el.tagName === "INPUT";
    }
    /**
     * Checks if the element is an input[type='text'] field
     */

  }, {
    key: "is_text",
    value: function is_text(el) {
      return this.is_input(el) && el.type === "text";
    }
    /**
     * Checks if the element is a button field
     */

  }, {
    key: "is_button",
    value: function is_button(el) {
      return el.tagName === "BUTTON";
    }
    /**
     * Checks if the element is an input[type='button'] field
     */

  }, {
    key: "is_input_button",
    value: function is_input_button(el) {
      return this.is_input(el) && el.type === "button";
    }
    /**
     * Checks if the element is an input[type='checkbox'] field
     */

  }, {
    key: "is_checkbox",
    value: function is_checkbox(el) {
      return this.is_input(el) && el.type === "checkbox";
    }
    /**
     * Checks if the element is an input[type='radio'] field
     */

  }, {
    key: "is_radio",
    value: function is_radio(el) {
      return this.is_input(el) && el.type === "radio";
    }
    /**
     * Checks if the element is a SENAITE reference field
     */

  }, {
    key: "is_reference",
    value: function is_reference(el) {
      return el.classList.contains("referencewidget");
    }
    /**
     * Checks if the element is a SENAITE single-reference field
     */

  }, {
    key: "is_single_reference",
    value: function is_single_reference(el) {
      return this.is_reference(el) && el.getAttribute("multivalued") == "0";
    }
    /**
     * Checks if the element is a SENAITE multi-reference field
     */

  }, {
    key: "is_multi_reference",
    value: function is_multi_reference(el) {
      return this.is_reference(el) && el.getAttribute("multivalued") == "1";
    }
    /**
     * event handler for `mutated` event
     */

  }, {
    key: "on_mutated",
    value: function on_mutated(event) {
      console.debug("EditForm::on_mutated");
      var form = event.detail.form;
      var mutations = event.detail.mutations; // reduce multiple mutations on the same node to one

      var seen = [];

      var _iterator18 = _createForOfIteratorHelper(mutations),
          _step18;

      try {
        for (_iterator18.s(); !(_step18 = _iterator18.n()).done;) {
          var mutation = _step18.value;

          if (seen.indexOf(mutation.target) > -1) {
            continue;
          }

          seen = seen.concat(mutation.target);
          this.handle_mutation(form, mutation);
        }
      } catch (err) {
        _iterator18.e(err);
      } finally {
        _iterator18.f();
      }
    }
    /**
     * event handler for `modified` event
     */

  }, {
    key: "on_modified",
    value: function on_modified(event) {
      console.debug("EditForm::on_modified");
      var form = event.detail.form;
      var field = event.detail.field;
      this.notify(form, field, "modified");
    }
    /**
     * event handler for `submit` event
     */

  }, {
    key: "on_submit",
    value: function on_submit(event) {
      var _this2 = this;

      console.debug("EditForm::on_submit");
      event.preventDefault();
      var data = {};
      var form = event.currentTarget.closest("form"); // NOTE: submit input field not included in request form data!

      var submitter = event.submitter;

      if (submitter) {
        data[submitter.name] = submitter.value; // disable submit button during ajax call

        this.toggle_disable(submitter, true);
      }

      this.ajax_submit(form, data, "submit").then(function (response) {
        return (// enable submit button after ajax call again
          _this2.toggle_disable(submitter, false)
        );
      });
    }
    /**
     * event handler for `blur` event
     */

  }, {
    key: "on_blur",
    value: function on_blur(event) {
      console.debug("EditForm::on_blur");
      var el = event.currentTarget;
      this.modified(el);
    }
    /**
     * event handler for `click` event
     */

  }, {
    key: "on_click",
    value: function on_click(event) {
      console.debug("EditForm::on_click");
      var el = event.currentTarget;
      this.modified(el);
    }
    /**
     * event handler for `change` event
     */

  }, {
    key: "on_change",
    value: function on_change(event) {
      console.debug("EditForm::on_change");
      var el = event.currentTarget;
      this.modified(el);
    }
  }]);

  return EditForm;
}();

/* harmony default export */ const editform = (EditForm);
;// CONCATENATED MODULE: ./components/site.js
/* provided dependency */ var $ = __webpack_require__(311);
/* Please use this command to compile this file into the parent `js` directory:
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

/* harmony default export */ const site = (Site);
;// CONCATENATED MODULE: ./components/sidebar.js
function sidebar_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function sidebar_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function sidebar_createClass(Constructor, protoProps, staticProps) { if (protoProps) sidebar_defineProperties(Constructor.prototype, protoProps); if (staticProps) sidebar_defineProperties(Constructor, staticProps); return Constructor; }

/* SENAITE Sidebar
 *
 * The sidebar shows when the mouse enters and hides when the mouse leaves the
 * HTML element.
 *
 * It keeps open when the toggle button was clicked.
 */
var Sidebar = /*#__PURE__*/function () {
  function Sidebar(config) {
    sidebar_classCallCheck(this, Sidebar);

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

    if (this.toggle_el) {
      this.toggle_el.addEventListener("click", this.on_click);
    } // sidebar view/hide handler


    this.el = document.getElementById(this.config.el);

    if (this.el) {
      this.el.addEventListener("mouseenter", this.on_mouseenter);
      this.el.addEventListener("mouseleave", this.on_mouseleave);

      if (this.is_toggled()) {
        this.el.classList.remove("minimized");
        this.el.classList.add("toggled");
      }
    }

    return this;
  }

  sidebar_createClass(Sidebar, [{
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

/* harmony default export */ const sidebar = (Sidebar);
;// CONCATENATED MODULE: ./senaite.core.js






document.addEventListener("DOMContentLoaded", function () {
  console.info("*** SENAITE CORE JS LOADED ***"); // Initialize i18n message factories

  window.i18n = new components_i18n();
  window._t = i18n_wrapper_t;
  window._p = _p; // BBB: set global `portal_url` variable

  window.portal_url = document.body.dataset.portalUrl; // Initialize Site

  window.site = new site(); // Initialize Sidebar

  window.sidebar = new sidebar({
    "el": "sidebar"
  }); // Ajax Edit Form Handler

  var form = new editform({
    form_selectors: ["form[name='edit_form']", "form.senaite-ajax-form"],
    field_selectors: ["input[type='text']", "input[type='number']", "input[type='checkbox']", "input[type='radio']", "input[type='file']", "select", "textarea"]
  }); // Init Tooltips

  external_jQuery_default()(function () {
    external_jQuery_default()("[data-toggle='tooltip']").tooltip();
    external_jQuery_default()("select.selectpicker").selectpicker();
  }); // Workflow Menu Update for Ajax Transitions
  // https://github.com/senaite/senaite.app.listing/pull/87

  document.body.addEventListener("listing:submit", function (event) {
    var menu = document.getElementById("plone-contentmenu-workflow"); // return immediately if no workflow menu is present

    if (menu === null) {
      return false;
    } // get the base url from the `data-base-url` attribute
    // -> see IBootstrapView


    var base_url = document.body.dataset.baseUrl;

    if (base_url === undefined) {
      // fallback to the current location URL
      base_url = location.href.split("#")[0].split("?")[0];
    }

    var request = new Request(base_url + "/menu/workflow_menu");
    fetch(request).then(function (response) {
      // we might get a 404 when the current page URL ends with a view, e.g.
      // `WS-ID/manage_results` or `CLIENT-ID/multi_results` etc.
      if (response.ok) {
        return response.text();
      }
    }).then(function (html) {
      if (!html) {
        return;
      }

      var parser = new DOMParser();
      var doc = parser.parseFromString(html, "text/html");
      var el = doc.body.firstChild;
      menu.replaceWith(el);
    });
  }); // Reload the whole view if the status of the view's context has changed
  // due to the transition submission of some items from the listing

  document.body.addEventListener("listing:submit", function (event) {
    // get the old workflow state of the view context
    var old_workflow_state = document.body.dataset.reviewState; // get the new workflow state of the view context
    // https://github.com/senaite/senaite.app.listing/pull/92

    var data = event.detail.data;
    var new_workflow_state = data.view_context_state; // reload the entire page if workflow state of the view context changed

    if (old_workflow_state != new_workflow_state) {
      location.reload();
    }
  });
});
})();

// This entry need to be wrapped in an IIFE because it need to be isolated against other entry modules.
(() => {
// extracted by mini-css-extract-plugin

})();

/******/ })()
;
//# sourceMappingURL=senaite.core.js.map