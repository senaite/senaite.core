/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ 559:
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
var external_jQuery_ = __webpack_require__(559);
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
/* provided dependency */ var $ = __webpack_require__(559);
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
;// CONCATENATED MODULE: external "React"
const external_React_namespaceObject = React;
var external_React_default = /*#__PURE__*/__webpack_require__.n(external_React_namespaceObject);
;// CONCATENATED MODULE: external "ReactDOM"
const external_ReactDOM_namespaceObject = ReactDOM;
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/api.js
function api_slicedToArray(arr, i) { return api_arrayWithHoles(arr) || api_iterableToArrayLimit(arr, i) || api_unsupportedIterableToArray(arr, i) || api_nonIterableRest(); }

function api_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function api_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return api_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return api_arrayLikeToArray(o, minLen); }

function api_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function api_iterableToArrayLimit(arr, i) { var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"]; if (_i == null) return; var _arr = []; var _n = true; var _d = false; var _s, _e; try { for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function api_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function api_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function api_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function api_createClass(Constructor, protoProps, staticProps) { if (protoProps) api_defineProperties(Constructor.prototype, protoProps); if (staticProps) api_defineProperties(Constructor, staticProps); return Constructor; }

var ReferenceWidgetAPI = /*#__PURE__*/function () {
  function ReferenceWidgetAPI(props) {
    api_classCallCheck(this, ReferenceWidgetAPI);

    console.debug("ReferenceWidgetAPI::constructor");
    this.api_url = props.api_url;

    this.on_api_error = props.on_api_error || function (response) {};

    return this;
  }

  api_createClass(ReferenceWidgetAPI, [{
    key: "get_api_url",
    value: function get_api_url(endpoint) {
      return "".concat(this.api_url, "/").concat(endpoint, "#").concat(location.search);
    }
    /*
     * Fetch Ajax API resource from the server
     *
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
     */

  }, {
    key: "get_json",
    value: function get_json(endpoint, options) {
      var data, init, method, on_api_error, request, url;

      if (options == null) {
        options = {};
      }

      method = options.method || "POST";
      data = JSON.stringify(options.data) || "{}";
      on_api_error = this.on_api_error;
      url = this.get_api_url(endpoint);
      init = {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-TOKEN": this.get_csrf_token()
        },
        body: method === "POST" ? data : null,
        credentials: "include"
      };
      console.info("ReferenceWidgetAPI::fetch:endpoint=" + endpoint + " init=", init);
      request = new Request(url, init);
      return fetch(request).then(function (response) {
        if (!response.ok) {
          return Promise.reject(response);
        }

        return response;
      }).then(function (response) {
        return response.json();
      })["catch"](function (response) {
        on_api_error(response);
        return response;
      });
    }
  }, {
    key: "search",
    value: function search(catalog, query, params) {
      params = params || {};
      var url = "search?catalog=".concat(catalog);

      var _loop = function _loop() {
        var _Object$entries$_i = api_slicedToArray(_Object$entries[_i], 2),
            key = _Object$entries$_i[0],
            value = _Object$entries$_i[1];

        // handle arrays as repeating parameters
        if (Array.isArray(value)) {
          value.forEach(function (item) {
            url += "&".concat(key, "=").concat(item);
          });
          return "continue";
        } // workaround for path queries


        if (key == "path") {
          value = value.query || null;

          if (value.depth !== null) {
            url += "&depth=".concat(value.depth);
          }
        }

        if (value) {
          url += "&".concat(key, "=").concat(value);
        }
      };

      for (var _i = 0, _Object$entries = Object.entries(query); _i < _Object$entries.length; _i++) {
        var _ret = _loop();

        if (_ret === "continue") continue;
      }

      for (var _i2 = 0, _Object$entries2 = Object.entries(params); _i2 < _Object$entries2.length; _i2++) {
        var _Object$entries2$_i = api_slicedToArray(_Object$entries2[_i2], 2),
            key = _Object$entries2$_i[0],
            value = _Object$entries2$_i[1];

        url += "&".concat(key, "=").concat(value);
      }

      console.debug("ReferenceWidgetAPI::search:url=", url);
      return this.get_json(url, {
        method: "GET"
      });
    }
    /*
     * Get the plone.protect CSRF token
     * Note: The fields won't save w/o that token set
     */

  }, {
    key: "get_csrf_token",
    value: function get_csrf_token() {
      return document.querySelector("#protect-script").dataset.token;
    }
  }]);

  return ReferenceWidgetAPI;
}();

/* harmony default export */ const api = (ReferenceWidgetAPI);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/components/ReferenceField.js
function _typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { _typeof = function _typeof(obj) { return typeof obj; }; } else { _typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return _typeof(obj); }

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function ReferenceField_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ReferenceField_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function ReferenceField_createClass(Constructor, protoProps, staticProps) { if (protoProps) ReferenceField_defineProperties(Constructor.prototype, protoProps); if (staticProps) ReferenceField_defineProperties(Constructor, staticProps); return Constructor; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) _setPrototypeOf(subClass, superClass); }

function _setPrototypeOf(o, p) { _setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return _setPrototypeOf(o, p); }

function _createSuper(Derived) { var hasNativeReflectConstruct = _isNativeReflectConstruct(); return function _createSuperInternal() { var Super = _getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = _getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return _possibleConstructorReturn(this, result); }; }

function _possibleConstructorReturn(self, call) { if (call && (_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return _assertThisInitialized(self); }

function _assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function _isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function _getPrototypeOf(o) { _getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return _getPrototypeOf(o); }




var ReferenceField = /*#__PURE__*/function (_React$Component) {
  _inherits(ReferenceField, _React$Component);

  var _super = _createSuper(ReferenceField);

  function ReferenceField(props) {
    var _this;

    ReferenceField_classCallCheck(this, ReferenceField);

    _this = _super.call(this, props);
    _this.state = {}; // React reference to the input field
    // https://reactjs.org/docs/react-api.html#reactcreateref

    _this.input_field_ref = /*#__PURE__*/external_React_default().createRef(); // bind event handlers

    _this.on_focus = _this.on_focus.bind(_assertThisInitialized(_this));
    _this.on_blur = _this.on_blur.bind(_assertThisInitialized(_this));
    _this.on_change = _this.on_change.bind(_assertThisInitialized(_this));
    _this.on_keydown = _this.on_keydown.bind(_assertThisInitialized(_this));
    _this.on_keypress = _this.on_keypress.bind(_assertThisInitialized(_this));
    _this.on_clear_click = _this.on_clear_click.bind(_assertThisInitialized(_this));
    _this.on_search_click = _this.on_search_click.bind(_assertThisInitialized(_this));
    return _this;
  }
  /*
   * Returns the search value from the input field
   */


  ReferenceField_createClass(ReferenceField, [{
    key: "get_search_value",
    value: function get_search_value() {
      return this.input_field_ref.current.value;
    }
    /*
     * Handler when the search field get focused
     */

  }, {
    key: "on_focus",
    value: function on_focus(event) {
      console.debug("ReferenceField::on_focus");

      if (this.props.on_focus) {
        var value = this.get_search_value() || null;
        this.props.on_focus(value);
      }
    }
    /*
     * Handler when the search field lost focus
     */

  }, {
    key: "on_blur",
    value: function on_blur(event) {
      console.debug("ReferenceField::on_blur");

      if (this.props.on_blur) {
        var value = this.get_search_value();
        this.props.on_blur(value);
      }
    }
    /*
     * Handler when the search value changed
     */

  }, {
    key: "on_change",
    value: function on_change(event) {
      event.preventDefault();
      var value = this.get_search_value();
      console.debug("ReferenceField::on_change:value: ", value);

      if (this.props.on_search) {
        this.props.on_search(value);
      }
    }
    /*
     * Handler for keydown events in the search field
     *
     */

  }, {
    key: "on_keydown",
    value: function on_keydown(event) {
      // backspace
      if (event.which == 8) {
        if (this.get_search_value() == "") {
          this.props.on_clear();
        }
      } // down arrow


      if (event.which == 40) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("down");
        }
      } // up arrow


      if (event.which == 38) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("up");
        }
      } // left arrow


      if (event.which == 37) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("left");
        }
      } // right arrow


      if (event.which == 39) {
        if (this.props.on_arrow_key) {
          this.props.on_arrow_key("right");
        }
      }
    }
    /*
     * Handler for keypress events in the search field
     *
     */

  }, {
    key: "on_keypress",
    value: function on_keypress(event) {
      if (event.which == 13) {
        console.debug("ReferenceField::on_keypress:ENTER"); // prevent form submission when clicking ENTER

        event.preventDefault();

        if (this.props.on_enter) {
          this.props.on_enter();
        }
      }
    }
  }, {
    key: "on_clear_click",
    value: function on_clear_click(event) {
      event.preventDefault();

      if (this.props.on_clear) {
        var value = this.get_search_value();
        this.props.on_clear(value); // clear the input field

        this.input_field_ref.current.value = "";
      }
    }
  }, {
    key: "on_search_click",
    value: function on_search_click(event) {
      event.preventDefault();

      if (this.props.on_search) {
        var value = this.get_search_value();
        this.props.on_search(value);
      }
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "uidreferencewidget-search-field"
      }, /*#__PURE__*/external_React_default().createElement("div", {
        className: "input-group"
      }, /*#__PURE__*/external_React_default().createElement("input", _defineProperty({
        type: "text",
        name: this.props.name,
        className: this.props.className,
        ref: this.input_field_ref,
        disabled: this.props.disabled,
        onKeyDown: this.on_keydown,
        onKeyPress: this.on_keypress,
        onChange: this.on_change,
        onFocus: this.on_focus,
        onBlur: this.on_blur,
        placeholder: this.props.placeholder,
        style: {
          maxWidth: "160px"
        }
      }, "disabled", this.props.disabled)), /*#__PURE__*/external_React_default().createElement("div", {
        "class": "input-group-append"
      }, /*#__PURE__*/external_React_default().createElement("button", {
        className: "btn btn-sm btn-outline-secondary",
        disabled: this.props.disabled,
        onClick: this.on_clear_click
      }, /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-times"
      })), /*#__PURE__*/external_React_default().createElement("button", {
        className: "btn btn-sm btn-outline-primary",
        disabled: this.props.disabled,
        onClick: this.on_search_click
      }, /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-search"
      })))));
    }
  }]);

  return ReferenceField;
}((external_React_default()).Component);

/* harmony default export */ const components_ReferenceField = (ReferenceField);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/components/ReferenceResults.js
function ReferenceResults_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { ReferenceResults_typeof = function _typeof(obj) { return typeof obj; }; } else { ReferenceResults_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return ReferenceResults_typeof(obj); }

function ReferenceResults_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = ReferenceResults_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function ReferenceResults_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return ReferenceResults_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return ReferenceResults_arrayLikeToArray(o, minLen); }

function ReferenceResults_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function ReferenceResults_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function ReferenceResults_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function ReferenceResults_createClass(Constructor, protoProps, staticProps) { if (protoProps) ReferenceResults_defineProperties(Constructor.prototype, protoProps); if (staticProps) ReferenceResults_defineProperties(Constructor, staticProps); return Constructor; }

function ReferenceResults_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) ReferenceResults_setPrototypeOf(subClass, superClass); }

function ReferenceResults_setPrototypeOf(o, p) { ReferenceResults_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return ReferenceResults_setPrototypeOf(o, p); }

function ReferenceResults_createSuper(Derived) { var hasNativeReflectConstruct = ReferenceResults_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = ReferenceResults_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = ReferenceResults_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return ReferenceResults_possibleConstructorReturn(this, result); }; }

function ReferenceResults_possibleConstructorReturn(self, call) { if (call && (ReferenceResults_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return ReferenceResults_assertThisInitialized(self); }

function ReferenceResults_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function ReferenceResults_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function ReferenceResults_getPrototypeOf(o) { ReferenceResults_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return ReferenceResults_getPrototypeOf(o); }




var ReferenceResults = /*#__PURE__*/function (_React$Component) {
  ReferenceResults_inherits(ReferenceResults, _React$Component);

  var _super = ReferenceResults_createSuper(ReferenceResults);

  function ReferenceResults(props) {
    var _this;

    ReferenceResults_classCallCheck(this, ReferenceResults);

    _this = _super.call(this, props); // bind event handlers

    _this.on_select = _this.on_select.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_page = _this.on_page.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_prev_page = _this.on_prev_page.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_next_page = _this.on_next_page.bind(ReferenceResults_assertThisInitialized(_this));
    _this.on_close = _this.on_close.bind(ReferenceResults_assertThisInitialized(_this));
    return _this;
  }
  /*
   * Return the header columns config
   *
   * @returns {Array} of column config objects
   */


  ReferenceResults_createClass(ReferenceResults, [{
    key: "get_columns",
    value: function get_columns() {
      return this.props.columns || [];
    }
    /*
     * Return only the (field-)names of the columns config
     *
     * @returns {Array} of column names
     */

  }, {
    key: "get_column_names",
    value: function get_column_names() {
      var columns = this.get_columns();
      return columns.map(function (column) {
        return column.name;
      });
    }
    /*
     * Return only the labels of the columns config
     *
     * @returns {Array} of column labels
     */

  }, {
    key: "get_column_labels",
    value: function get_column_labels() {
      var columns = this.get_columns();
      return columns.map(function (column) {
        return column.label;
      });
    }
    /*
     * Return the search results
     *
     * @returns {Array} of result objects (items of `senaite.jsonapi` response)
     */

  }, {
    key: "get_results",
    value: function get_results() {
      return this.props.results || [];
    }
    /*
     * Checks if results are available
     *
     * @returns {Boolean} true if there are results, false otherwise
     */

  }, {
    key: "has_results",
    value: function has_results() {
      return this.get_results().length > 0;
    }
    /*
     * Returns the style object for the dropdown table
     *
     * @returns {Object} of ReactJS CSS styles
     */

  }, {
    key: "get_style",
    value: function get_style() {
      return {
        minWidth: this.props.width || "400px",
        backgroundColor: "white",
        zIndex: 999999
      };
    }
    /*
     * Returns the UID of a result object
     *
     * @returns {String} UID of the result
     */

  }, {
    key: "get_result_uid",
    value: function get_result_uid(result) {
      return result.uid || "NO UID FOUND!";
    }
    /*
     * Checks wehter the UID is already in the list of selected UIDs
     *
     * @returns {Boolean} true if the UID is already selected, false otherwise
     */

  }, {
    key: "is_uid_selected",
    value: function is_uid_selected(uid) {
      return this.props.uids.indexOf(uid) > -1;
    }
    /*
     * Build Header <th></th> columns
     *
     * @returns {Array} of <th>...</th> columns
     */

  }, {
    key: "build_header_columns",
    value: function build_header_columns() {
      var columns = [];

      var _iterator = ReferenceResults_createForOfIteratorHelper(this.get_columns()),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var column = _step.value;
          var label = column.label || column.title;
          var width = column.width || "auto";
          var align = column.align || "left";
          columns.push( /*#__PURE__*/external_React_default().createElement("th", {
            className: "border-top-0",
            width: width,
            align: align
          }, _t(label)));
        } // Append additional column for usage state

      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      columns.push( /*#__PURE__*/external_React_default().createElement("th", {
        className: "border-top-0",
        width: "1"
      }));
      return columns;
    }
    /*
     * Build table <tr></tr> rows
     *
     * @returns {Array} of <tr>...</tr> rows
     */

  }, {
    key: "build_rows",
    value: function build_rows() {
      var _this2 = this;

      var rows = [];
      var results = this.get_results();
      results.forEach(function (result, index) {
        var uid = _this2.get_result_uid(result);

        rows.push( /*#__PURE__*/external_React_default().createElement("tr", {
          uid: uid,
          className: _this2.props.focused == index ? "table-active" : "",
          onClick: _this2.on_select
        }, _this2.build_columns(result)));
      });
      return rows;
    }
    /*
     * Build Header <td></td> columns
     *
     * @returns {Array} of <td>...</td> columns
     */

  }, {
    key: "build_columns",
    value: function build_columns(result) {
      var columns = [];
      var searchterm = this.props.searchterm || "";

      var _iterator2 = ReferenceResults_createForOfIteratorHelper(this.get_column_names()),
          _step2;

      try {
        for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
          var name = _step2.value;
          var value = result[name];
          var highlighted = this.highlight(value, searchterm);
          columns.push( /*#__PURE__*/external_React_default().createElement("td", {
            dangerouslySetInnerHTML: {
              __html: highlighted
            }
          }));
        }
      } catch (err) {
        _iterator2.e(err);
      } finally {
        _iterator2.f();
      }

      var uid = result.uid;
      var used = this.props.uids.indexOf(uid) > -1;
      columns.push( /*#__PURE__*/external_React_default().createElement("td", null, used && /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-link text-success"
      })));
      return columns;
    }
    /*
     * Highlight any found match of the searchterm in the text
     *
     * @returns {String} highlighted text
     */

  }, {
    key: "highlight",
    value: function highlight(text, searchterm) {
      if (searchterm.length == 0) return text;

      try {
        var rx = new RegExp(searchterm, "gi");
        text = text.replaceAll(rx, function (m) {
          return "<span class='font-weight-bold text-info'>" + m + "</span>";
        });
      } catch (error) {// pass
      }

      return text;
    }
    /*
     * Build pagination <li>...</li> items
     *
     * @returns {Array} Pagination JSX
     */

  }, {
    key: "build_pages",
    value: function build_pages() {
      var pages = [];

      for (var page = 1; page <= this.props.pages; page++) {
        var cls = ["page-item"];
        if (this.props.page == page) cls.push("active");
        pages.push( /*#__PURE__*/external_React_default().createElement("li", {
          className: cls.join(" ")
        }, /*#__PURE__*/external_React_default().createElement("button", {
          className: "page-link",
          page: page,
          onClick: this.on_page
        }, page)));
      }

      return pages;
    }
    /*
     * Build pagination next button
     *
     * @returns {Array} Next button JSX
     */

  }, {
    key: "build_next_button",
    value: function build_next_button() {
      var cls = ["page-item"];
      if (!this.props.next_url) cls.push("disabled");
      return /*#__PURE__*/external_React_default().createElement("li", {
        className: cls.join(" ")
      }, /*#__PURE__*/external_React_default().createElement("button", {
        className: "page-link",
        onClick: this.on_next_page
      }, "Next"));
    }
    /*
     * Build pagination previous button
     *
     * @returns {Array} Previous button JSX
     */

  }, {
    key: "build_prev_button",
    value: function build_prev_button() {
      var cls = ["page-item"];
      if (!this.props.prev_url) cls.push("disabled");
      return /*#__PURE__*/external_React_default().createElement("li", {
        className: cls.join(" ")
      }, /*#__PURE__*/external_React_default().createElement("button", {
        className: "page-link",
        onClick: this.on_prev_page
      }, "Previous"));
    }
    /*
     * Build results dropdown close button
     *
     * @returns {Array} Close button JSX
     */

  }, {
    key: "build_close_button",
    value: function build_close_button() {
      return /*#__PURE__*/external_React_default().createElement("button", {
        className: "btn btn-sm btn-link",
        onClick: this.on_close
      }, /*#__PURE__*/external_React_default().createElement("i", {
        "class": "fas fa-window-close"
      }));
    }
    /*
     * Event handler when a result was selected
     */

  }, {
    key: "on_select",
    value: function on_select(event) {
      event.preventDefault();
      var target = event.currentTarget;
      var uid = target.getAttribute("uid");
      console.debug("ReferenceResults::on_select:event=", event);

      if (this.props.on_select) {
        this.props.on_select(uid);
      }
    }
    /*
     * Event handler when a page was clicked
     */

  }, {
    key: "on_page",
    value: function on_page(event) {
      event.preventDefault();
      var target = event.currentTarget;
      var page = target.getAttribute("page");
      console.debug("ReferenceResults::on_page:event=", event);

      if (page == this.props.page) {
        return;
      }

      if (this.props.on_page) {
        this.props.on_page(page);
      }
    }
    /*
     * Event handler when the pagination previous button was clicked
     */

  }, {
    key: "on_prev_page",
    value: function on_prev_page(event) {
      event.preventDefault();
      console.debug("ReferenceResults::on_prev_page:event=", event);
      var page = this.props.page;

      if (page < 2) {
        console.warn("No previous pages available!");
        return;
      }

      if (this.props.on_page) {
        this.props.on_page(page - 1);
      }
    }
    /*
     * Event handler when the pagination next button was clicked
     */

  }, {
    key: "on_next_page",
    value: function on_next_page(event) {
      event.preventDefault();
      console.debug("ReferenceResults::on_next_page:event=", event);
      var page = this.props.page;

      if (page + 1 > this.props.pages) {
        console.warn("No next pages available!");
        return;
      }

      if (this.props.on_page) {
        this.props.on_page(page + 1);
      }
    }
    /*
     * Event handler when the dropdown close button was clicked
     */

  }, {
    key: "on_close",
    value: function on_close(event) {
      event.preventDefault();
      console.debug("ReferenceResults::on_close:event=", event);

      if (this.props.on_clear) {
        this.props.on_clear();
      }
    }
    /*
     * Render the reference results selection
     */

  }, {
    key: "render",
    value: function render() {
      if (!this.has_results()) {
        return null;
      }

      return /*#__PURE__*/external_React_default().createElement("div", {
        className: this.props.className,
        style: this.get_style()
      }, /*#__PURE__*/external_React_default().createElement("div", {
        style: {
          position: "absolute",
          top: 0,
          right: 0
        }
      }, this.build_close_button()), /*#__PURE__*/external_React_default().createElement("table", {
        className: "table table-sm table-hover small"
      }, /*#__PURE__*/external_React_default().createElement("thead", null, /*#__PURE__*/external_React_default().createElement("tr", null, this.build_header_columns())), /*#__PURE__*/external_React_default().createElement("tbody", null, this.build_rows())), this.props.pages > 1 && /*#__PURE__*/external_React_default().createElement("nav", null, /*#__PURE__*/external_React_default().createElement("ul", {
        className: "pagination pagination-sm justify-content-center"
      }, this.build_prev_button(), this.build_pages(), this.build_next_button())));
    }
  }]);

  return ReferenceResults;
}((external_React_default()).Component);

/* harmony default export */ const components_ReferenceResults = (ReferenceResults);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/components/References.js
function References_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { References_typeof = function _typeof(obj) { return typeof obj; }; } else { References_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return References_typeof(obj); }

function References_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = References_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e2) { throw _e2; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e3) { didErr = true; err = _e3; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function References_slicedToArray(arr, i) { return References_arrayWithHoles(arr) || References_iterableToArrayLimit(arr, i) || References_unsupportedIterableToArray(arr, i) || References_nonIterableRest(); }

function References_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function References_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return References_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return References_arrayLikeToArray(o, minLen); }

function References_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function References_iterableToArrayLimit(arr, i) { var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"]; if (_i == null) return; var _arr = []; var _n = true; var _d = false; var _s, _e; try { for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function References_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function References_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function References_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function References_createClass(Constructor, protoProps, staticProps) { if (protoProps) References_defineProperties(Constructor.prototype, protoProps); if (staticProps) References_defineProperties(Constructor, staticProps); return Constructor; }

function References_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) References_setPrototypeOf(subClass, superClass); }

function References_setPrototypeOf(o, p) { References_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return References_setPrototypeOf(o, p); }

function References_createSuper(Derived) { var hasNativeReflectConstruct = References_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = References_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = References_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return References_possibleConstructorReturn(this, result); }; }

function References_possibleConstructorReturn(self, call) { if (call && (References_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return References_assertThisInitialized(self); }

function References_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function References_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function References_getPrototypeOf(o) { References_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return References_getPrototypeOf(o); }




var References = /*#__PURE__*/function (_React$Component) {
  References_inherits(References, _React$Component);

  var _super = References_createSuper(References);

  function References(props) {
    var _this;

    References_classCallCheck(this, References);

    _this = _super.call(this, props);
    _this.on_deselect = _this.on_deselect.bind(References_assertThisInitialized(_this));
    return _this;
  }

  References_createClass(References, [{
    key: "get_selected_uids",
    value: function get_selected_uids() {
      return this.props.uids || [];
    }
    /*
     * Simple template interpolation that replaces ${...} placeholders
     * with any found value from the context object.
     *
     * https://stackoverflow.com/questions/29182244/convert-a-string-to-a-template-string
     */

  }, {
    key: "interpolate",
    value: function interpolate(template, context) {
      for (var _i = 0, _Object$entries = Object.entries(context); _i < _Object$entries.length; _i++) {
        var _Object$entries$_i = References_slicedToArray(_Object$entries[_i], 2),
            key = _Object$entries$_i[0],
            value = _Object$entries$_i[1];

        template = template.replace(new RegExp('\\$\\{' + key + '\\}', 'g'), value);
      }

      return template;
    }
  }, {
    key: "render_display_template",
    value: function render_display_template(uid) {
      var template = this.props.display_template;
      var context = this.props.records[uid];
      if (!context) return uid;
      return this.interpolate(template, context);
    }
  }, {
    key: "build_selected_items",
    value: function build_selected_items() {
      var items = [];
      var selected_uids = this.get_selected_uids();

      var _iterator = References_createForOfIteratorHelper(selected_uids),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var uid = _step.value;
          items.push( /*#__PURE__*/external_React_default().createElement("li", {
            uid: uid
          }, /*#__PURE__*/external_React_default().createElement("div", {
            className: "p-1 mb-1 mr-1 bg-light border rounded d-inline-block"
          }, /*#__PURE__*/external_React_default().createElement("span", {
            dangerouslySetInnerHTML: {
              __html: this.render_display_template(uid)
            }
          }), /*#__PURE__*/external_React_default().createElement("button", {
            uid: uid,
            className: "btn btn-sm btn-link-danger",
            onClick: this.on_deselect
          }, /*#__PURE__*/external_React_default().createElement("i", {
            className: "fas fa-times-circle"
          })))));
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      return items;
    }
  }, {
    key: "on_deselect",
    value: function on_deselect(event) {
      event.preventDefault();
      var target = event.currentTarget;
      var uid = target.getAttribute("uid");
      console.debug("References::on_deselect: Remove UID", uid);

      if (this.props.on_deselect) {
        this.props.on_deselect(uid);
      }
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "uidreferencewidget-references"
      }, /*#__PURE__*/external_React_default().createElement("ul", {
        className: "list-unstyled list-group list-group-horizontal"
      }, this.build_selected_items()), /*#__PURE__*/external_React_default().createElement("textarea", {
        className: "d-none",
        name: this.props.name,
        value: this.props.uids.join("\n")
      }));
    }
  }]);

  return References;
}((external_React_default()).Component);

/* harmony default export */ const components_References = (References);
;// CONCATENATED MODULE: ./widgets/uidreferencewidget/widget.js
function widget_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { widget_typeof = function _typeof(obj) { return typeof obj; }; } else { widget_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return widget_typeof(obj); }

function widget_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = widget_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function widget_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return widget_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return widget_arrayLikeToArray(o, minLen); }

function widget_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function widget_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function widget_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function widget_createClass(Constructor, protoProps, staticProps) { if (protoProps) widget_defineProperties(Constructor.prototype, protoProps); if (staticProps) widget_defineProperties(Constructor, staticProps); return Constructor; }

function widget_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) widget_setPrototypeOf(subClass, superClass); }

function widget_setPrototypeOf(o, p) { widget_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return widget_setPrototypeOf(o, p); }

function widget_createSuper(Derived) { var hasNativeReflectConstruct = widget_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = widget_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = widget_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return widget_possibleConstructorReturn(this, result); }; }

function widget_possibleConstructorReturn(self, call) { if (call && (widget_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return widget_assertThisInitialized(self); }

function widget_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function widget_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function widget_getPrototypeOf(o) { widget_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return widget_getPrototypeOf(o); }








var UIDReferenceWidgetController = /*#__PURE__*/function (_React$Component) {
  widget_inherits(UIDReferenceWidgetController, _React$Component);

  var _super = widget_createSuper(UIDReferenceWidgetController);

  function UIDReferenceWidgetController(props) {
    var _this;

    widget_classCallCheck(this, UIDReferenceWidgetController);

    _this = _super.call(this, props); // Internal state

    _this.state = {
      results: [],
      // `items` list of search results coming from `senaite.jsonapi`
      searchterm: "",
      // the search term that was entered by the user
      loading: false,
      // loading flag when searching for results
      count: 0,
      // count of results (coming from `senaite.jsonapi`)
      page: 1,
      // current page (coming from `senaite.jsonapi`)
      pages: 1,
      // number of pages (coming from `senaite.jsonapi`)
      next_url: null,
      // next page API URL (coming from `senaite.jsonapi`)
      prev_url: null,
      // previous page API URL (coming from `senaite.jsonapi`)
      b_start: 1,
      // batch start for pagination (see `senaite.jsonapi.batch`)
      focused: 0 // current result that has the focus

    }; // Root input HTML element

    var el = props.root_el; // Data keys located at the root element
    // -> initial values are set from the widget class

    var data_keys = ["id", "name", "uids", "api_url", "records", "catalog", "query", "columns", "display_template", "limit", "multi_valued", "disabled", "readonly"]; // Query data keys and set state with parsed JSON value

    for (var _i = 0, _data_keys = data_keys; _i < _data_keys.length; _i++) {
      var key = _data_keys[_i];
      var value = el.dataset[key];
      _this.state[key] = _this.parse_json(value);
    } // Initialize communication API with the API URL


    _this.api = new api({
      api_url: _this.state.api_url
    }); // Bind callbacks to current context

    _this.search = _this.search.bind(widget_assertThisInitialized(_this));
    _this.goto_page = _this.goto_page.bind(widget_assertThisInitialized(_this));
    _this.clear_results = _this.clear_results.bind(widget_assertThisInitialized(_this));
    _this.select = _this.select.bind(widget_assertThisInitialized(_this));
    _this.select_focused = _this.select_focused.bind(widget_assertThisInitialized(_this));
    _this.deselect = _this.deselect.bind(widget_assertThisInitialized(_this));
    _this.navigate_results = _this.navigate_results.bind(widget_assertThisInitialized(_this));
    _this.on_keydown = _this.on_keydown.bind(widget_assertThisInitialized(_this));
    _this.on_click = _this.on_click.bind(widget_assertThisInitialized(_this)); // dev only

    window.widget = widget_assertThisInitialized(_this);
    return widget_possibleConstructorReturn(_this, widget_assertThisInitialized(_this));
  }

  widget_createClass(UIDReferenceWidgetController, [{
    key: "componentDidMount",
    value: function componentDidMount() {
      // Bind event listeners of the document
      document.addEventListener("keydown", this.on_keydown, false);
      document.addEventListener("click", this.on_click, false);
    }
  }, {
    key: "componentWillUnmount",
    value: function componentWillUnmount() {
      // Remove event listeners of the document
      document.removeEventListener("keydown", this.on_keydown, false);
      document.removeEventListener("click", this.on_click, false);
    }
    /*
     * JSON parse the given value
     *
     * @param {String} value: The JSON value to parse
     */

  }, {
    key: "parse_json",
    value: function parse_json(value) {
      try {
        return JSON.parse(value);
      } catch (error) {
        console.error("Could not parse \"".concat(value, "\" to JSON"));
      }
    }
  }, {
    key: "is_disabled",
    value: function is_disabled() {
      if (this.state.disabled) {
        return true;
      }

      if (this.state.readonly) {
        return true;
      }

      if (!this.state.multi_valued && this.state.uids.length > 0) {
        return true;
      }

      return false;
    }
    /*
     * Create a query object for the API
     *
     * This method prepares a query from the current state variables,
     * which can be used to call the `api.search` method.
     *
     * @param {Object} options: Additional options to add to the query
     * @returns {Object} The query object
     */

  }, {
    key: "make_query",
    value: function make_query(options) {
      options = options || {};
      return Object.assign({
        q: this.state.searchterm,
        limit: this.state.limit,
        complete: 1
      }, options, this.state.query);
    }
    /*
     * Execute a search query and set the results to the state
     *
     * @param {Object} url_params: Additional search params for the API search URL
     * @returns {Promise}
     */

  }, {
    key: "fetch_results",
    value: function fetch_results(url_params) {
      url_params = url_params || {}; // prepare the server request

      var self = this;
      var query = this.make_query();
      this.toggle_loading(true);
      var promise = this.api.search(this.state.catalog, query, url_params);
      promise.then(function (data) {
        console.debug("ReferenceWidgetController::fetch_results:GOT DATA: ", data);
        self.set_results_data(data);
        self.toggle_loading(false);
      });
      return promise;
    }
    /*
     * Execute a search for the given searchterm
     *
     * @param {String} searchterm: The value entered into the search field
     * @returns {Promise}
     */

  }, {
    key: "search",
    value: function search(searchterm) {
      if (!searchterm && this.state.results.length > 0) {
        this.state.searchterm = "";
        return;
      }

      console.debug("ReferenceWidgetController::search:searchterm:", searchterm); // set the searchterm directly to avoid re-rendering

      this.state.searchterm = searchterm || "";
      return this.fetch_results();
    }
    /*
     * Fetch results of a page
     *
     * @param {Integer} page: The page to fetch
     * @returns {Promise}
     */

  }, {
    key: "goto_page",
    value: function goto_page(page) {
      page = parseInt(page);
      var limit = parseInt(this.state.limit); // calculate the beginning of the page
      // Note: this is the count of previous items that are excluded

      var b_start = page * limit - limit;
      return this.fetch_results({
        b_start: b_start
      });
    }
    /*
     * Add the UID of a search result to the state
     *
     * @param {String} uid: The selected UID
     * @returns {Array} uids: current selected UIDs
     */

  }, {
    key: "select",
    value: function select(uid) {
      console.debug("ReferenceWidgetController::select:uid:", uid); // create a copy of the selected UIDs

      var uids = [].concat(this.state.uids); // Add the new UID if it is not selected yet

      if (uids.indexOf(uid) == -1) {
        uids.push(uid);
      }

      this.setState({
        uids: uids
      });

      if (uids.length > 0 && !this.state.multi_valued) {
        this.clear_results();
      }

      return uids;
    }
    /*
     * Add/remove the focused result
     *
     */

  }, {
    key: "select_focused",
    value: function select_focused() {
      console.debug("ReferenceWidgetController::select_focused");
      var focused = this.state.focused;
      var result = this.state.results.at(focused);

      if (result) {
        var uid = result.uid;

        if (this.state.uids.indexOf(uid) == -1) {
          this.select(uid);
        } else {
          this.deselect(uid);
        }
      }
    }
    /*
     * Remove the UID of a reference from the state
     *
     * @param {String} uid: The selected UID
     * @returns {Array} uids: current selected UIDs
     */

  }, {
    key: "deselect",
    value: function deselect(uid) {
      console.debug("ReferenceWidgetController::deselect:uid:", uid);
      var uids = [].concat(this.state.uids);
      var pos = uids.indexOf(uid);

      if (pos > -1) {
        uids.splice(pos, 1);
      }

      this.setState({
        uids: uids
      });
      return uids;
    }
    /*
     * Navigate the results either up or down
     *
     * @param {String} direction: either up or down
     */

  }, {
    key: "navigate_results",
    value: function navigate_results(direction) {
      var page = this.state.page;
      var pages = this.state.pages;
      var results = this.state.results;
      var focused = this.state.focused;
      var searchterm = this.state.searchterm;
      console.debug("ReferenceWidgetController::navigate_results:focused:", focused);

      if (direction == "up") {
        if (focused > 0) {
          this.setState({
            focused: focused - 1
          });
        } else {
          this.setState({
            focused: 0
          });

          if (page > 1) {
            this.goto_page(page - 1);
          }
        }
      } else if (direction == "down") {
        if (this.state.results.length == 0) {
          this.search(searchterm);
        }

        if (focused < results.length - 1) {
          this.setState({
            focused: focused + 1
          });
        } else {
          this.setState({
            focused: 0
          });

          if (page < pages) {
            this.goto_page(page + 1);
          }
        }
      } else if (direction == "left") {
        this.setState({
          focused: 0
        });

        if (page > 0) {
          this.goto_page(page - 1);
        }
      } else if (direction == "right") {
        this.setState({
          focused: 0
        });

        if (page < pages) {
          this.goto_page(page + 1);
        }
      }
    }
    /*
     * Toggle loading state
     *
     * @param {Boolean} toggle: The loading state to set
     * @returns {Boolean} toggle: The current loading state
     */

  }, {
    key: "toggle_loading",
    value: function toggle_loading(toggle) {
      if (toggle == null) {
        toggle = false;
      }

      this.setState({
        loading: toggle
      });
      return toggle;
    }
    /*
     * Set results data coming from `senaite.jsonapi`
     *
     * @param {Object} data: JSON search result object returned from `senaite.jsonapi`
     */

  }, {
    key: "set_results_data",
    value: function set_results_data(data) {
      data = data || {};
      var items = data.items || [];
      var records = Object.assign(this.state.records, {}); // update state records

      var _iterator = widget_createForOfIteratorHelper(items),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var item = _step.value;
          var uid = item.uid;
          records[uid] = item;
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      this.setState({
        records: records,
        results: items,
        count: data.count || 0,
        page: data.page || 1,
        pages: data.pages || 1,
        next_url: data.next || null,
        prev_url: data.previous || null
      });
    }
    /*
     * Clear results from the state
     */

  }, {
    key: "clear_results",
    value: function clear_results() {
      this.setState({
        results: [],
        count: 0,
        page: 1,
        pages: 1,
        next_url: null,
        prev_url: null
      });
    }
    /*
     * ReactJS event handler for keydown event
     */

  }, {
    key: "on_keydown",
    value: function on_keydown(event) {
      // clear results when ESC key is pressed
      if (event.keyCode === 27) {
        this.clear_results();
      }
    }
    /*
     * ReactJS event handler for click events
     */

  }, {
    key: "on_click",
    value: function on_click(event) {
      // clear results when clicked outside of the widget
      var widget = this.props.root_el;
      var target = event.target;

      if (!widget.contains(target)) {
        this.clear_results();
      }
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "uidreferencewidget"
      }, /*#__PURE__*/external_React_default().createElement(components_References, {
        uids: this.state.uids,
        records: this.state.records,
        display_template: this.state.display_template,
        name: this.state.name,
        on_deselect: this.deselect
      }), /*#__PURE__*/external_React_default().createElement(components_ReferenceField, {
        className: "form-control",
        name: "uidreference-search",
        disabled: this.is_disabled(),
        on_search: this.search,
        on_clear: this.clear_results,
        on_focus: this.search,
        on_arrow_key: this.navigate_results,
        on_enter: this.select_focused
      }), /*#__PURE__*/external_React_default().createElement(components_ReferenceResults, {
        className: "position-absolute shadow border rounded bg-white mt-1 p-1",
        columns: this.state.columns,
        uids: this.state.uids,
        searchterm: this.state.searchterm,
        results: this.state.results,
        focused: this.state.focused,
        count: this.state.count,
        page: this.state.page,
        pages: this.state.pages,
        next_url: this.state.next_url,
        prev_url: this.state.prev_url,
        on_select: this.select,
        on_page: this.goto_page,
        on_clear: this.clear_results
      }));
    }
  }]);

  return UIDReferenceWidgetController;
}((external_React_default()).Component);

/* harmony default export */ const uidreferencewidget_widget = (UIDReferenceWidgetController);
;// CONCATENATED MODULE: ./widgets/addresswidget/api.js
function addresswidget_api_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function addresswidget_api_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function addresswidget_api_createClass(Constructor, protoProps, staticProps) { if (protoProps) addresswidget_api_defineProperties(Constructor.prototype, protoProps); if (staticProps) addresswidget_api_defineProperties(Constructor, staticProps); return Constructor; }

var AddressWidgetAPI = /*#__PURE__*/function () {
  function AddressWidgetAPI(props) {
    addresswidget_api_classCallCheck(this, AddressWidgetAPI);

    console.debug("AddressWidgetAPI::constructor");
    this.portal_url = props.portal_url;

    this.on_api_error = props.on_api_error || function (response) {};

    return this;
  }

  addresswidget_api_createClass(AddressWidgetAPI, [{
    key: "get_url",
    value: function get_url(endpoint) {
      return "".concat(this.portal_url, "/").concat(endpoint);
    }
    /*
     * Fetch JSON resource from the server
     *
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
     */

  }, {
    key: "get_json",
    value: function get_json(endpoint, options) {
      var data, init, method, on_api_error, request, url;

      if (options == null) {
        options = {};
      }

      method = options.method || "POST";
      data = JSON.stringify(options.data) || "{}";
      on_api_error = this.on_api_error;
      url = this.get_url(endpoint);
      init = {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "X-CSRF-TOKEN": this.get_csrf_token()
        },
        body: method === "POST" ? data : null,
        credentials: "include"
      };
      console.info("AddressWidgetAPI::fetch:endpoint=" + endpoint + " init=", init);
      request = new Request(url, init);
      return fetch(request).then(function (response) {
        if (!response.ok) {
          return Promise.reject(response);
        }

        return response;
      }).then(function (response) {
        return response.json();
      })["catch"](function (response) {
        on_api_error(response);
        return response;
      });
    }
  }, {
    key: "fetch_subdivisions",
    value: function fetch_subdivisions(parent) {
      var url = "geo_subdivisions";
      console.debug("AddressWidgetAPI::fetch_subdivisions:url=", url);
      var options = {
        method: "POST",
        data: {
          "parent": parent
        }
      };
      return this.get_json(url, options);
    }
    /*
     * Get the plone.protect CSRF token
     */

  }, {
    key: "get_csrf_token",
    value: function get_csrf_token() {
      return document.querySelector("#protect-script").dataset.token;
    }
  }]);

  return AddressWidgetAPI;
}();

/* harmony default export */ const addresswidget_api = (AddressWidgetAPI);
;// CONCATENATED MODULE: ./widgets/addresswidget/components/LocationSelector.js
function LocationSelector_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { LocationSelector_typeof = function _typeof(obj) { return typeof obj; }; } else { LocationSelector_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return LocationSelector_typeof(obj); }

function LocationSelector_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = LocationSelector_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function LocationSelector_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return LocationSelector_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return LocationSelector_arrayLikeToArray(o, minLen); }

function LocationSelector_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function LocationSelector_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function LocationSelector_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function LocationSelector_createClass(Constructor, protoProps, staticProps) { if (protoProps) LocationSelector_defineProperties(Constructor.prototype, protoProps); if (staticProps) LocationSelector_defineProperties(Constructor, staticProps); return Constructor; }

function LocationSelector_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) LocationSelector_setPrototypeOf(subClass, superClass); }

function LocationSelector_setPrototypeOf(o, p) { LocationSelector_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return LocationSelector_setPrototypeOf(o, p); }

function LocationSelector_createSuper(Derived) { var hasNativeReflectConstruct = LocationSelector_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = LocationSelector_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = LocationSelector_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return LocationSelector_possibleConstructorReturn(this, result); }; }

function LocationSelector_possibleConstructorReturn(self, call) { if (call && (LocationSelector_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return LocationSelector_assertThisInitialized(self); }

function LocationSelector_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function LocationSelector_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function LocationSelector_getPrototypeOf(o) { LocationSelector_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return LocationSelector_getPrototypeOf(o); }




var LocationSelector = /*#__PURE__*/function (_React$Component) {
  LocationSelector_inherits(LocationSelector, _React$Component);

  var _super = LocationSelector_createSuper(LocationSelector);

  function LocationSelector(props) {
    LocationSelector_classCallCheck(this, LocationSelector);

    return _super.call(this, props);
  }

  LocationSelector_createClass(LocationSelector, [{
    key: "render_options",
    value: function render_options() {
      var options = [];
      var locations = this.props.locations;
      options.push( /*#__PURE__*/external_React_default().createElement("option", {
        value: ""
      }));

      if (Array.isArray(locations)) {
        var _iterator = LocationSelector_createForOfIteratorHelper(locations),
            _step;

        try {
          for (_iterator.s(); !(_step = _iterator.n()).done;) {
            var location = _step.value;
            options.push( /*#__PURE__*/external_React_default().createElement("option", {
              value: location
            }, location));
          }
        } catch (err) {
          _iterator.e(err);
        } finally {
          _iterator.f();
        }
      }

      return options;
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("select", {
        id: this.props.id,
        name: this.props.name,
        value: this.props.value,
        onChange: this.props.onChange
      }, this.render_options());
    }
  }]);

  return LocationSelector;
}((external_React_default()).Component);

/* harmony default export */ const components_LocationSelector = (LocationSelector);
;// CONCATENATED MODULE: ./widgets/addresswidget/components/AddressField.js
function AddressField_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { AddressField_typeof = function _typeof(obj) { return typeof obj; }; } else { AddressField_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return AddressField_typeof(obj); }

function AddressField_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function AddressField_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function AddressField_createClass(Constructor, protoProps, staticProps) { if (protoProps) AddressField_defineProperties(Constructor.prototype, protoProps); if (staticProps) AddressField_defineProperties(Constructor, staticProps); return Constructor; }

function AddressField_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) AddressField_setPrototypeOf(subClass, superClass); }

function AddressField_setPrototypeOf(o, p) { AddressField_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return AddressField_setPrototypeOf(o, p); }

function AddressField_createSuper(Derived) { var hasNativeReflectConstruct = AddressField_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = AddressField_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = AddressField_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return AddressField_possibleConstructorReturn(this, result); }; }

function AddressField_possibleConstructorReturn(self, call) { if (call && (AddressField_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return AddressField_assertThisInitialized(self); }

function AddressField_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function AddressField_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function AddressField_getPrototypeOf(o) { AddressField_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return AddressField_getPrototypeOf(o); }





var AddressField = /*#__PURE__*/function (_React$Component) {
  AddressField_inherits(AddressField, _React$Component);

  var _super = AddressField_createSuper(AddressField);

  function AddressField(props) {
    AddressField_classCallCheck(this, AddressField);

    return _super.call(this, props);
  }

  AddressField_createClass(AddressField, [{
    key: "is_location_selector",
    value: function is_location_selector() {
      return Array.isArray(this.props.locations);
    }
  }, {
    key: "is_visible",
    value: function is_visible() {
      var visible = true;

      if (this.is_location_selector()) {
        visible = this.props.locations.length > 0;
      }

      return visible;
    }
  }, {
    key: "render_element",
    value: function render_element() {
      if (this.is_location_selector()) {
        return /*#__PURE__*/external_React_default().createElement(components_LocationSelector, {
          id: this.props.id,
          name: this.props.name,
          value: this.props.value,
          locations: this.props.locations,
          onChange: this.props.onChange
        });
      } else {
        return /*#__PURE__*/external_React_default().createElement("input", {
          type: "text",
          id: this.props.id,
          name: this.props.name,
          value: this.props.value,
          onChange: this.props.onChange
        });
      }
    }
  }, {
    key: "render",
    value: function render() {
      if (!this.is_visible()) {
        return /*#__PURE__*/external_React_default().createElement("input", {
          type: "hidden",
          id: this.props.id,
          name: this.props.name,
          value: this.props.value
        });
      }

      return /*#__PURE__*/external_React_default().createElement("div", {
        "class": "form-group form-row mb-2"
      }, /*#__PURE__*/external_React_default().createElement("div", {
        "class": "col input-group input-group-sm"
      }, /*#__PURE__*/external_React_default().createElement("div", {
        "class": "input-group-prepend"
      }, /*#__PURE__*/external_React_default().createElement("label", {
        "class": "input-group-text",
        "for": this.props.id
      }, this.props.label)), this.render_element()));
    }
  }]);

  return AddressField;
}((external_React_default()).Component);

/* harmony default export */ const components_AddressField = (AddressField);
;// CONCATENATED MODULE: ./widgets/addresswidget/components/Address.js
function Address_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { Address_typeof = function _typeof(obj) { return typeof obj; }; } else { Address_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return Address_typeof(obj); }

function Address_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function Address_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function Address_createClass(Constructor, protoProps, staticProps) { if (protoProps) Address_defineProperties(Constructor.prototype, protoProps); if (staticProps) Address_defineProperties(Constructor, staticProps); return Constructor; }

function Address_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) Address_setPrototypeOf(subClass, superClass); }

function Address_setPrototypeOf(o, p) { Address_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return Address_setPrototypeOf(o, p); }

function Address_createSuper(Derived) { var hasNativeReflectConstruct = Address_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = Address_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = Address_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return Address_possibleConstructorReturn(this, result); }; }

function Address_possibleConstructorReturn(self, call) { if (call && (Address_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return Address_assertThisInitialized(self); }

function Address_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function Address_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function Address_getPrototypeOf(o) { Address_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return Address_getPrototypeOf(o); }





var Address = /*#__PURE__*/function (_React$Component) {
  Address_inherits(Address, _React$Component);

  var _super = Address_createSuper(Address);

  function Address(props) {
    var _this;

    Address_classCallCheck(this, Address);

    _this = _super.call(this, props);
    _this.state = {
      country: props.country,
      subdivision1: props.subdivision1,
      subdivision2: props.subdivision2,
      city: props.city,
      zip: props.zip,
      address: props.address,
      address_type: props.address_type
    }; // Event handlers

    _this.on_country_change = _this.on_country_change.bind(Address_assertThisInitialized(_this));
    _this.on_subdivision1_change = _this.on_subdivision1_change.bind(Address_assertThisInitialized(_this));
    _this.on_subdivision2_change = _this.on_subdivision2_change.bind(Address_assertThisInitialized(_this));
    _this.on_city_change = _this.on_city_change.bind(Address_assertThisInitialized(_this));
    _this.on_zip_change = _this.on_zip_change.bind(Address_assertThisInitialized(_this));
    _this.on_address_change = _this.on_address_change.bind(Address_assertThisInitialized(_this));
    return _this;
  }

  Address_createClass(Address, [{
    key: "force_array",
    value: function force_array(value) {
      if (!Array.isArray(value)) {
        value = [];
      }

      return value;
    }
    /**
     * Returns the list of first-level subdivisions of the current country,
     * sorted alphabetically
     */

  }, {
    key: "get_subdivisions1",
    value: function get_subdivisions1() {
      var country = this.state.country;
      return this.force_array(this.props.subdivisions1[country]);
    }
    /**
     * Returns the list of subdivisions of the current first-level subdivision,
     * sorted sorted alphabetically
     */

  }, {
    key: "get_subdivisions2",
    value: function get_subdivisions2() {
      var subdivision1 = this.state.subdivision1;
      return this.force_array(this.props.subdivisions2[subdivision1]);
    }
  }, {
    key: "get_label",
    value: function get_label(key) {
      var country = this.state.country;
      var label = this.props.labels[country];

      if (label != null && label.constructor == Object && key in label) {
        label = label[key];
      } else {
        label = this.props.labels[key];
      }

      return label;
    }
    /** Event triggered when the value for Country selector changes. Updates the
     * selector of subdivisions (e.g. states) with the list of top-level
     * subdivisions for the selected country
     */

  }, {
    key: "on_country_change",
    value: function on_country_change(event) {
      var value = event.currentTarget.value;
      console.debug("Address::on_country_change: ".concat(value));

      if (this.props.on_country_change) {
        this.props.on_country_change(value);
      }

      this.setState({
        country: value,
        subdivision1: "",
        subdivision2: ""
      });
    }
    /** Event triggered when the value for the Country first-level subdivision
     * (e.g. state) selector changes. Updates the selector of subdivisions (e.g.
     * districts) for the selected subdivision and country
     */

  }, {
    key: "on_subdivision1_change",
    value: function on_subdivision1_change(event) {
      var value = event.currentTarget.value;
      console.debug("Address::on_subdivision1_change: ".concat(value));

      if (this.props.on_subdivision1_change) {
        var country = this.state.country;
        this.props.on_subdivision1_change(country, value);
      }

      this.setState({
        subdivision1: value,
        subdivision2: ""
      });
    }
    /** Event triggered when the value for the second-level subdivision (e.g.
     * district) selector changes
     */

  }, {
    key: "on_subdivision2_change",
    value: function on_subdivision2_change(event) {
      var value = event.currentTarget.value;
      console.debug("Address::on_subdivision2_change: ".concat(value));

      if (this.props.on_subdivision2_change) {
        this.props.on_subdivision2_change(value);
      }

      this.setState({
        subdivision2: value
      });
    }
    /** Event triggered when the value for the address field changes
     */

  }, {
    key: "on_address_change",
    value: function on_address_change(event) {
      var value = event.currentTarget.value;
      this.setState({
        address: value
      });
    }
    /** Event triggered when the value for the zip field changes
     */

  }, {
    key: "on_zip_change",
    value: function on_zip_change(event) {
      var value = event.currentTarget.value;
      this.setState({
        zip: value
      });
    }
    /** Event triggered when the value for the city field changes
     */

  }, {
    key: "on_city_change",
    value: function on_city_change(event) {
      var value = event.currentTarget.value;
      this.setState({
        city: value
      });
    }
  }, {
    key: "get_input_id",
    value: function get_input_id(subfield) {
      var id = this.props.id;
      var index = this.props.index;
      return "".concat(id, "-").concat(index, "-").concat(subfield);
    }
  }, {
    key: "get_input_name",
    value: function get_input_name(subfield) {
      var name = this.props.name;
      var index = this.props.index;
      return "".concat(name, ".").concat(index, ".").concat(subfield);
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", null, /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("country"),
        name: this.get_input_name("country"),
        label: this.props.labels.country,
        value: this.state.country,
        locations: this.props.countries,
        onChange: this.on_country_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("subdivision1"),
        name: this.get_input_name("subdivision1"),
        label: this.get_label("subdivision1"),
        value: this.state.subdivision1,
        locations: this.get_subdivisions1(),
        onChange: this.on_subdivision1_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("subdivision2"),
        name: this.get_input_name("subdivision2"),
        label: this.get_label("subdivision2"),
        value: this.state.subdivision2,
        locations: this.get_subdivisions2(),
        onChange: this.on_subdivision2_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("city"),
        name: this.get_input_name("city"),
        label: this.props.labels.city,
        value: this.state.city,
        onChange: this.on_city_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("zip"),
        name: this.get_input_name("zip"),
        label: this.props.labels.zip,
        value: this.state.zip,
        onChange: this.on_zip_change
      }), /*#__PURE__*/external_React_default().createElement(components_AddressField, {
        id: this.get_input_id("address"),
        name: this.get_input_name("address"),
        label: this.props.labels.address,
        value: this.state.address,
        onChange: this.on_address_change
      }), /*#__PURE__*/external_React_default().createElement("input", {
        type: "hidden",
        id: this.get_input_id("type"),
        name: this.get_input_name("type"),
        value: this.state.address_type
      }));
    }
  }]);

  return Address;
}((external_React_default()).Component);

/* harmony default export */ const components_Address = (Address);
;// CONCATENATED MODULE: ./widgets/addresswidget/widget.js
function addresswidget_widget_typeof(obj) { "@babel/helpers - typeof"; if (typeof Symbol === "function" && typeof Symbol.iterator === "symbol") { addresswidget_widget_typeof = function _typeof(obj) { return typeof obj; }; } else { addresswidget_widget_typeof = function _typeof(obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; }; } return addresswidget_widget_typeof(obj); }

function widget_slicedToArray(arr, i) { return widget_arrayWithHoles(arr) || widget_iterableToArrayLimit(arr, i) || addresswidget_widget_unsupportedIterableToArray(arr, i) || widget_nonIterableRest(); }

function widget_nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }

function widget_iterableToArrayLimit(arr, i) { var _i = arr == null ? null : typeof Symbol !== "undefined" && arr[Symbol.iterator] || arr["@@iterator"]; if (_i == null) return; var _arr = []; var _n = true; var _d = false; var _s, _e; try { for (_i = _i.call(arr); !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"] != null) _i["return"](); } finally { if (_d) throw _e; } } return _arr; }

function widget_arrayWithHoles(arr) { if (Array.isArray(arr)) return arr; }

function addresswidget_widget_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = addresswidget_widget_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e2) { throw _e2; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e3) { didErr = true; err = _e3; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function addresswidget_widget_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return addresswidget_widget_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return addresswidget_widget_arrayLikeToArray(o, minLen); }

function addresswidget_widget_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }

function ownKeys(object, enumerableOnly) { var keys = Object.keys(object); if (Object.getOwnPropertySymbols) { var symbols = Object.getOwnPropertySymbols(object); if (enumerableOnly) { symbols = symbols.filter(function (sym) { return Object.getOwnPropertyDescriptor(object, sym).enumerable; }); } keys.push.apply(keys, symbols); } return keys; }

function _objectSpread(target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i] != null ? arguments[i] : {}; if (i % 2) { ownKeys(Object(source), true).forEach(function (key) { widget_defineProperty(target, key, source[key]); }); } else if (Object.getOwnPropertyDescriptors) { Object.defineProperties(target, Object.getOwnPropertyDescriptors(source)); } else { ownKeys(Object(source)).forEach(function (key) { Object.defineProperty(target, key, Object.getOwnPropertyDescriptor(source, key)); }); } } return target; }

function widget_defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function addresswidget_widget_classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function addresswidget_widget_defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } }

function addresswidget_widget_createClass(Constructor, protoProps, staticProps) { if (protoProps) addresswidget_widget_defineProperties(Constructor.prototype, protoProps); if (staticProps) addresswidget_widget_defineProperties(Constructor, staticProps); return Constructor; }

function addresswidget_widget_inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function"); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, writable: true, configurable: true } }); if (superClass) addresswidget_widget_setPrototypeOf(subClass, superClass); }

function addresswidget_widget_setPrototypeOf(o, p) { addresswidget_widget_setPrototypeOf = Object.setPrototypeOf || function _setPrototypeOf(o, p) { o.__proto__ = p; return o; }; return addresswidget_widget_setPrototypeOf(o, p); }

function addresswidget_widget_createSuper(Derived) { var hasNativeReflectConstruct = addresswidget_widget_isNativeReflectConstruct(); return function _createSuperInternal() { var Super = addresswidget_widget_getPrototypeOf(Derived), result; if (hasNativeReflectConstruct) { var NewTarget = addresswidget_widget_getPrototypeOf(this).constructor; result = Reflect.construct(Super, arguments, NewTarget); } else { result = Super.apply(this, arguments); } return addresswidget_widget_possibleConstructorReturn(this, result); }; }

function addresswidget_widget_possibleConstructorReturn(self, call) { if (call && (addresswidget_widget_typeof(call) === "object" || typeof call === "function")) { return call; } else if (call !== void 0) { throw new TypeError("Derived constructors may only return object or undefined"); } return addresswidget_widget_assertThisInitialized(self); }

function addresswidget_widget_assertThisInitialized(self) { if (self === void 0) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return self; }

function addresswidget_widget_isNativeReflectConstruct() { if (typeof Reflect === "undefined" || !Reflect.construct) return false; if (Reflect.construct.sham) return false; if (typeof Proxy === "function") return true; try { Boolean.prototype.valueOf.call(Reflect.construct(Boolean, [], function () {})); return true; } catch (e) { return false; } }

function addresswidget_widget_getPrototypeOf(o) { addresswidget_widget_getPrototypeOf = Object.setPrototypeOf ? Object.getPrototypeOf : function _getPrototypeOf(o) { return o.__proto__ || Object.getPrototypeOf(o); }; return addresswidget_widget_getPrototypeOf(o); }






var AddressWidgetController = /*#__PURE__*/function (_React$Component) {
  addresswidget_widget_inherits(AddressWidgetController, _React$Component);

  var _super = addresswidget_widget_createSuper(AddressWidgetController);

  function AddressWidgetController(props) {
    var _this;

    addresswidget_widget_classCallCheck(this, AddressWidgetController);

    _this = _super.call(this, props); // Root input HTML element

    var el = props.root_el;
    _this.state = {}; // Data keys located at the root element
    // -> initial values are set from the widget class

    var data_keys = ["id", "name", "items", "portal_url", "labels", "countries", "subdivisions1", "subdivisions2"]; // Query data keys and set state with parsed JSON value

    for (var _i = 0, _data_keys = data_keys; _i < _data_keys.length; _i++) {
      var key = _data_keys[_i];
      var value = el.dataset[key];
      _this.state[key] = _this.parse_json(value);
    } // Initialize communication API with the API URL


    _this.api = new addresswidget_api({
      portal_url: _this.state.portal_url
    }); // Bind callbacks to current context

    _this.on_country_change = _this.on_country_change.bind(addresswidget_widget_assertThisInitialized(_this));
    _this.on_subdivision1_change = _this.on_subdivision1_change.bind(addresswidget_widget_assertThisInitialized(_this));
    return addresswidget_widget_possibleConstructorReturn(_this, addresswidget_widget_assertThisInitialized(_this));
  }

  addresswidget_widget_createClass(AddressWidgetController, [{
    key: "parse_json",
    value: function parse_json(value) {
      try {
        return JSON.parse(value);
      } catch (error) {
        console.error("Could not parse \"".concat(value, "\" to JSON"));
      }
    }
    /**
     * Event triggered when the user selects a country. Function fetches and
     * updates the geo mapping with the first level subdivisions for the selected
     * country if are not up-to-date yet. It also updates the label for the first
     * level subdivision in accordance.
     */

  }, {
    key: "on_country_change",
    value: function on_country_change(country) {
      console.debug("widget::on_country_change: ".concat(country));
      var self = this;
      var promise = this.api.fetch_subdivisions(country);
      promise.then(function (data) {
        // Update the label with the type of 1st-level subdivisions
        var labels = _objectSpread({}, self.state.labels);

        if (data.length > 0) {
          labels[country]["subdivision1"] = data[0].type;
        } // Create a copy instead of modifying the existing dict from state var


        var subdivisions = _objectSpread({}, self.state.subdivisions1); // Only interested in names, sorted alphabetically


        subdivisions[country] = data.map(function (x) {
          return x.name;
        }).sort(); // Update current state with the changes

        self.setState({
          subdivisions1: subdivisions,
          labels: labels
        });
      });
      return promise;
    }
    /**
     * Event triggered when the user selects a first-level subdivision of a
     * country. Function fetches and updates the geo mapping with the second level
     * subdivisions for the selected subdivision if are not up-to-date. It also
     * updates the label for the second level subdivision in accordance.
     */

  }, {
    key: "on_subdivision1_change",
    value: function on_subdivision1_change(country, subdivision) {
      console.debug("widget::on_subdivision1_change: ".concat(country, ", ").concat(subdivision));
      var self = this;
      var promise = this.api.fetch_subdivisions(subdivision);
      promise.then(function (data) {
        // Update the label with the type of 1st-level subdivisions
        var labels = _objectSpread({}, self.state.labels);

        if (data.length > 0) {
          labels[country]["subdivision2"] = data[0].type;
        } // Create a copy instead of modifying the existing dict from state var


        var subdivisions = _objectSpread({}, self.state.subdivisions2); // Only interested in names, sorted alphabetically


        subdivisions[subdivision] = data.map(function (x) {
          return x.name;
        }).sort(); // Update current state with the changes

        self.setState({
          subdivisions2: subdivisions,
          labels: labels
        });
      });
      return promise;
    }
  }, {
    key: "render_items",
    value: function render_items() {
      var html_items = [];
      var items = this.state.items;

      var _iterator = addresswidget_widget_createForOfIteratorHelper(items.entries()),
          _step;

      try {
        for (_iterator.s(); !(_step = _iterator.n()).done;) {
          var _step$value = widget_slicedToArray(_step.value, 2),
              index = _step$value[0],
              item = _step$value[1];

          var section_title = "";

          if (items.length > 1) {
            // Only render the title if more than one address
            section_title = /*#__PURE__*/external_React_default().createElement("strong", null, this.state.labels[item.type]);
          }

          html_items.push( /*#__PURE__*/external_React_default().createElement("div", {
            "class": "mb-2 pt-2"
          }, section_title, /*#__PURE__*/external_React_default().createElement(components_Address, {
            id: this.state.id,
            name: this.state.name,
            index: index,
            address_type: item.type,
            country: item.country,
            subdivision1: item.subdivision1,
            subdivision2: item.subdivision2,
            city: item.city,
            zip: item.zip,
            address: item.address,
            labels: this.state.labels,
            countries: this.state.countries,
            subdivisions1: this.state.subdivisions1,
            subdivisions2: this.state.subdivisions2,
            on_country_change: this.on_country_change,
            on_subdivision1_change: this.on_subdivision1_change
          })));
        }
      } catch (err) {
        _iterator.e(err);
      } finally {
        _iterator.f();
      }

      return html_items;
    }
  }, {
    key: "render",
    value: function render() {
      return /*#__PURE__*/external_React_default().createElement("div", {
        className: "addresswidget"
      }, this.render_items());
    }
  }]);

  return AddressWidgetController;
}((external_React_default()).Component);

/* harmony default export */ const addresswidget_widget = (AddressWidgetController);
;// CONCATENATED MODULE: ./senaite.core.js
function senaite_core_createForOfIteratorHelper(o, allowArrayLike) { var it = typeof Symbol !== "undefined" && o[Symbol.iterator] || o["@@iterator"]; if (!it) { if (Array.isArray(o) || (it = senaite_core_unsupportedIterableToArray(o)) || allowArrayLike && o && typeof o.length === "number") { if (it) o = it; var i = 0; var F = function F() {}; return { s: F, n: function n() { if (i >= o.length) return { done: true }; return { done: false, value: o[i++] }; }, e: function e(_e) { throw _e; }, f: F }; } throw new TypeError("Invalid attempt to iterate non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); } var normalCompletion = true, didErr = false, err; return { s: function s() { it = it.call(o); }, n: function n() { var step = it.next(); normalCompletion = step.done; return step; }, e: function e(_e2) { didErr = true; err = _e2; }, f: function f() { try { if (!normalCompletion && it["return"] != null) it["return"](); } finally { if (didErr) throw err; } } }; }

function senaite_core_unsupportedIterableToArray(o, minLen) { if (!o) return; if (typeof o === "string") return senaite_core_arrayLikeToArray(o, minLen); var n = Object.prototype.toString.call(o).slice(8, -1); if (n === "Object" && o.constructor) n = o.constructor.name; if (n === "Map" || n === "Set") return Array.from(o); if (n === "Arguments" || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(n)) return senaite_core_arrayLikeToArray(o, minLen); }

function senaite_core_arrayLikeToArray(arr, len) { if (len == null || len > arr.length) len = arr.length; for (var i = 0, arr2 = new Array(len); i < len; i++) { arr2[i] = arr[i]; } return arr2; }









document.addEventListener("DOMContentLoaded", function () {
  console.debug("*** SENAITE CORE JS LOADED ***"); // Initialize i18n message factories

  window.i18n = new components_i18n();
  window._t = i18n_wrapper_t;
  window._p = _p; // BBB: set global `portal_url` variable

  window.portal_url = document.body.dataset.portalUrl; // TinyMCE

  tinymce.init({
    height: 300,
    paste_data_images: true,
    selector: "textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text'],textarea.richTextWidget",
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    content_css: "/++plone++senaite.core.static/bundles/main.css"
  }); // /TinyMCE
  // Initialize Site

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
  }); // Widgets

  window.widgets = {}; // Referencewidgets

  var ref_widgets = document.getElementsByClassName("senaite-uidreference-widget-input");

  var _iterator = senaite_core_createForOfIteratorHelper(ref_widgets),
      _step;

  try {
    for (_iterator.s(); !(_step = _iterator.n()).done;) {
      var widget = _step.value;
      var id = widget.dataset.id;
      var controller = ReactDOM.render( /*#__PURE__*/React.createElement(uidreferencewidget_widget, {
        root_el: widget
      }), widget);
      window.widgets[id] = controller;
    } // AddressWidget

  } catch (err) {
    _iterator.e(err);
  } finally {
    _iterator.f();
  }

  var address_widgets = document.getElementsByClassName("senaite-address-widget-input");

  var _iterator2 = senaite_core_createForOfIteratorHelper(address_widgets),
      _step2;

  try {
    for (_iterator2.s(); !(_step2 = _iterator2.n()).done;) {
      var _widget = _step2.value;
      var _id = _widget.dataset.id;

      var _controller = ReactDOM.render( /*#__PURE__*/React.createElement(addresswidget_widget, {
        root_el: _widget
      }), _widget);

      window.widgets[_id] = _controller;
    }
  } catch (err) {
    _iterator2.e(err);
  } finally {
    _iterator2.f();
  }
});
})();

// This entry need to be wrapped in an IIFE because it need to be isolated against other entry modules.
(() => {
// extracted by mini-css-extract-plugin

})();

/******/ })()
;
//# sourceMappingURL=main.js.map