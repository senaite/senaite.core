
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
    indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.AnalysisServiceEditView = (function() {
    function AnalysisServiceEditView() {
      this.on_partition_required_volume_change = bind(this.on_partition_required_volume_change, this);
      this.on_partition_container_change = bind(this.on_partition_container_change, this);
      this.on_partition_separate_container_change = bind(this.on_partition_separate_container_change, this);
      this.on_partition_sampletype_change = bind(this.on_partition_sampletype_change, this);
      this.on_default_container_change = bind(this.on_default_container_change, this);
      this.on_default_preservation_change = bind(this.on_default_preservation_change, this);
      this.on_separate_container_change = bind(this.on_separate_container_change, this);
      this.on_calculation_change = bind(this.on_calculation_change, this);
      this.on_use_default_calculation_change = bind(this.on_use_default_calculation_change, this);
      this.on_default_method_change = bind(this.on_default_method_change, this);
      this.on_default_instrument_change = bind(this.on_default_instrument_change, this);
      this.on_instruments_change = bind(this.on_instruments_change, this);
      this.on_instrument_assignment_allowed_change = bind(this.on_instrument_assignment_allowed_change, this);
      this.on_methods_change = bind(this.on_methods_change, this);
      this.on_manual_entry_of_results_change = bind(this.on_manual_entry_of_results_change, this);
      this.toggle_checkbox = bind(this.toggle_checkbox, this);
      this.select_options = bind(this.select_options, this);
      this.parse_select_option = bind(this.parse_select_option, this);
      this.parse_select_options = bind(this.parse_select_options, this);
      this.add_select_option = bind(this.add_select_option, this);
      this.is_uid = bind(this.is_uid, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.get_url = bind(this.get_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.load_object_by_uid = bind(this.load_object_by_uid, this);
      this.load_manual_interims = bind(this.load_manual_interims, this);
      this.load_calculation = bind(this.load_calculation, this);
      this.load_method_calculation = bind(this.load_method_calculation, this);
      this.load_instrument_methods = bind(this.load_instrument_methods, this);
      this.load_available_instruments = bind(this.load_available_instruments, this);
      this.show_alert = bind(this.show_alert, this);
      this.set_instrument_methods = bind(this.set_instrument_methods, this);
      this.set_method_calculation = bind(this.set_method_calculation, this);
      this.flush_interims = bind(this.flush_interims, this);
      this.set_interims = bind(this.set_interims, this);
      this.get_interims = bind(this.get_interims, this);
      this.select_calculation = bind(this.select_calculation, this);
      this.set_calculation = bind(this.set_calculation, this);
      this.get_calculation = bind(this.get_calculation, this);
      this.toggle_use_default_calculation_of_method = bind(this.toggle_use_default_calculation_of_method, this);
      this.use_default_calculation_of_method = bind(this.use_default_calculation_of_method, this);
      this.select_default_instrument = bind(this.select_default_instrument, this);
      this.set_default_instrument = bind(this.set_default_instrument, this);
      this.get_default_instrument = bind(this.get_default_instrument, this);
      this.select_default_method = bind(this.select_default_method, this);
      this.set_default_method = bind(this.set_default_method, this);
      this.get_default_method = bind(this.get_default_method, this);
      this.select_instruments = bind(this.select_instruments, this);
      this.set_instruments = bind(this.set_instruments, this);
      this.get_instruments = bind(this.get_instruments, this);
      this.toggle_instrument_assignment_allowed = bind(this.toggle_instrument_assignment_allowed, this);
      this.is_instrument_assignment_allowed = bind(this.is_instrument_assignment_allowed, this);
      this.select_methods = bind(this.select_methods, this);
      this.set_methods = bind(this.set_methods, this);
      this.get_methods = bind(this.get_methods, this);
      this.toggle_manual_entry_of_results_allowed = bind(this.toggle_manual_entry_of_results_allowed, this);
      this.is_manual_entry_of_results_allowed = bind(this.is_manual_entry_of_results_allowed, this);
      this.init = bind(this.init, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }

    AnalysisServiceEditView.prototype.load = function() {
      var d1, d2;
      console.debug("AnalysisServiceEditView::load");
      jarn.i18n.loadCatalog("bika");
      this._ = window.jarn.i18n.MessageFactory("bika");
      this.all_instruments = {};
      this.invalid_instruments = {};
      d1 = this.load_available_instruments().done(function(instruments) {
        var me;
        me = this;
        return $.each(instruments, function(index, instrument) {
          var uid;
          uid = instrument.UID;
          me.all_instruments[uid] = instrument;
          if (instrument.Valid !== "1") {
            return me.invalid_instruments[uid] = instrument;
          }
        });
      });
      this.manual_interims = [];
      d2 = this.load_manual_interims().done(function(manual_interims) {
        return this.manual_interims = manual_interims;
      });
      this.selected_methods = this.get_methods();
      this.selected_instruments = this.get_instruments();
      this.selected_calculation = this.get_calculation();
      this.selected_default_instrument = this.get_default_instrument();
      this.selected_default_method = this.get_default_method();
      this.methods = this.parse_select_options($("#archetypes-fieldname-Methods #Methods"));
      this.instruments = this.parse_select_options($("#archetypes-fieldname-Instruments #Instruments"));
      this.calculations = this.parse_select_options($("#archetypes-fieldname-Calculation #Calculation"));
      this.bind_eventhandler();
      $.when(d1, d2).then(this.init);
      return window.asv = this;
    };


    /* INITIALIZERS */

    AnalysisServiceEditView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("AnalysisServiceEditView::bind_eventhandler");

      /* METHODS TAB */
      $("body").on("change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", this.on_manual_entry_of_results_change);
      $("body").on("change", "#archetypes-fieldname-Methods #Methods", this.on_methods_change);
      $("body").on("change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", this.on_instrument_assignment_allowed_change);
      $("body").on("change", "#archetypes-fieldname-Instruments #Instruments", this.on_instruments_change);
      $("body").on("change", "#archetypes-fieldname-Instrument #Instrument", this.on_default_instrument_change);
      $("body").on("change", "#archetypes-fieldname-Method #Method", this.on_default_method_change);
      $("body").on("change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", this.on_use_default_calculation_change);
      $("body").on("change", "#archetypes-fieldname-Calculation #Calculation", this.on_calculation_change);

      /* CONTAINER AND PRESERVATION TAB */
      $("body").on("change", "#archetypes-fieldname-Separate #Separate", this.on_separate_container_change);
      $("body").on("change", "#archetypes-fieldname-Preservation #Preservation", this.on_default_preservation_change);
      $("body").on("selected", "#archetypes-fieldname-Container #Container", this.on_default_container_change);
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.sampletype']", this.on_partition_sampletype_change);
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.separate']", this.on_partition_separate_container_change);
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.container']", this.on_partition_container_change);
      return $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.vol']", this.on_partition_required_volume_change);
    };

    AnalysisServiceEditView.prototype.init = function() {

      /**
       * Initialize Form
       */
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("--> Manual Entry of Results is allowed");
        this.set_methods(this.methods);
      } else {
        console.debug("--> Manual Entry of Results is **not** allowed");
        this.set_methods(null);
      }
      if (this.is_instrument_assignment_allowed()) {
        console.debug("--> Instrument assignment is allowed");
        this.set_instruments(this.instruments);
      } else {
        console.debug("--> Instrument assignment is **not** allowed");
        this.set_instruments(null);
      }
      if (this.use_default_calculation_of_method()) {
        return console.debug("--> Use default calculation of method");
      } else {
        return console.debug("--> Use default calculation of instrument");
      }
    };


    /* FIELD GETTERS/SETTERS/SELECTORS */

    AnalysisServiceEditView.prototype.is_manual_entry_of_results_allowed = function() {

      /**
       * Get the value of the checkbox "Instrument assignment is not required"
       *
       * @returns {boolean} True if results can be entered without instrument
       */
      var field;
      field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults");
      return field.is(":checked");
    };

    AnalysisServiceEditView.prototype.toggle_manual_entry_of_results_allowed = function(toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the "Instrument assignment is not required" checkbox
       */
      field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults");
      return this.toggle_checkbox(field, toggle, silent);
    };

    AnalysisServiceEditView.prototype.get_methods = function() {

      /**
       * Get all selected method UIDs from the multiselect field
       *
       * @returns {array} of method objects
       */
      var field;
      field = $("#archetypes-fieldname-Methods #Methods");
      return $.extend([], field.val());
    };

    AnalysisServiceEditView.prototype.set_methods = function(methods, flush) {
      var field, me;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set the methods multiselect field with the given methods
       *
       * @param {array} methods
       *    Array of method objects with at least `title` and `uid` keys set
       *
       * @param {boolean} flush
       *    True to empty all instruments first
       */
      field = $("#archetypes-fieldname-Methods #Methods");
      methods = $.extend([], methods);
      if (flush) {
        field.empty();
      }
      if (methods.length === 0) {
        this.add_select_option(field, null);
      } else {
        me = this;
        $.each(methods, function(index, method) {
          var title, uid;
          if (method.ManualEntryOfResults === false) {
            return;
          }
          title = method.title || method.Title;
          uid = method.uid || method.UID;
          return me.add_select_option(field, title, uid);
        });
      }
      return this.select_methods(this.selected_methods);
    };

    AnalysisServiceEditView.prototype.select_methods = function(uids) {

      /**
       * Select methods by UID
       *
       * @param {Array} uids
       *    UIDs of Methods to select
       */
      var field, me;
      if (!this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual entry of results is not allowed");
        return;
      }
      field = $("#archetypes-fieldname-Methods #Methods");
      this.select_options(field, uids);
      me = this;
      $.each(uids, function(index, uid) {
        var flush, method, option;
        flush = index === 0 && true || false;
        option = field.find("option[value=" + uid + "]");
        method = {
          uid: option.val(),
          title: option.text()
        };
        return me.set_default_method(method, flush = flush);
      });
      this.select_default_method(this.selected_default_method);
      if (this.use_default_calculation_of_method()) {
        return this.set_method_calculation(this.get_default_method());
      }
    };

    AnalysisServiceEditView.prototype.is_instrument_assignment_allowed = function() {

      /**
       * Get the value of the checkbox "Instrument assignment is allowed"
       *
       * @returns {boolean} True if instrument assignment is allowed
       */
      var field;
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      return field.is(":checked");
    };

    AnalysisServiceEditView.prototype.toggle_instrument_assignment_allowed = function(toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the "Instrument assignment is allowed" checkbox
       */
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      return this.toggle_checkbox(field, toggle, silent);
    };

    AnalysisServiceEditView.prototype.get_instruments = function() {

      /**
       * Get all selected instrument UIDs from the multiselect
       *
       * @returns {array} of instrument objects
       */
      var field;
      field = $("#archetypes-fieldname-Instruments #Instruments");
      return $.extend([], field.val());
    };

    AnalysisServiceEditView.prototype.set_instruments = function(instruments, flush) {
      var field, me;
      if (flush == null) {
        flush = true;
      }

      /*
       * Set the instruments to the field
       *
       * @param {array} instruments
       *    Array of instrument objects to set in the multi-select
       *
       * @param {boolean} flush
       *    True to empty all instruments first
       */
      field = $("#archetypes-fieldname-Instruments #Instruments");
      instruments = $.extend([], instruments);
      if (flush) {
        field.empty();
      }
      if (instruments.length === 0) {
        this.add_select_option(field, null);
      } else {
        me = this;
        $.each(instruments, function(index, instrument) {
          var title, uid;
          uid = instrument.uid || instrument.UID;
          title = instrument.title || instrument.Title;
          return me.add_select_option(field, title, uid);
        });
      }
      return this.select_instruments(this.selected_instruments);
    };

    AnalysisServiceEditView.prototype.select_instruments = function(uids) {

      /**
       * Select instruments by UID
       *
       * @param {Array} uids
       *    UIDs of Instruments to select
       */
      var field, invalid_instruments, me, notification, title;
      if (!this.is_instrument_assignment_allowed()) {
        console.debug("Instrument assignment not allowed");
        this.set_default_instrument(null);
        return;
      }
      field = $("#archetypes-fieldname-Instruments #Instruments");
      this.select_options(field, uids);
      invalid_instruments = [];
      me = this;
      $.each(uids, function(index, uid) {
        var flush, instrument;
        flush = index === 0 && true || false;
        instrument = me.all_instruments[uid];
        if (uid in me.invalid_instruments) {
          console.warn("Instrument '" + instrument.Title + "' is invalid");
          invalid_instruments.push(instrument);
        }
        return me.set_default_instrument(instrument, flush = flush);
      });
      if (invalid_instruments.length > 0) {
        notification = $("<dl/>");
        $.each(invalid_instruments, function(index, instrument) {
          return notification.append("<dd>⚠ " + instrument.Title + "</dd>");
        });
        title = this._("Some of the selected instruments are out-of-date, with failed calibration tests or under maintenance");
        this.show_alert({
          title: title,
          message: notification[0].outerHTML
        });
      } else {
        this.show_alert({
          message: ""
        });
      }
      this.select_default_instrument(this.selected_default_instrument);
      return this.set_instrument_methods(this.get_default_instrument());
    };

    AnalysisServiceEditView.prototype.get_default_method = function() {

      /**
       * Get the UID of the selected default method
       *
       * @returns {string} UID of the default method
       */
      var field;
      field = $("#archetypes-fieldname-Method #Method");
      return field.val();
    };

    AnalysisServiceEditView.prototype.set_default_method = function(method, flush) {
      var field, title, uid;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set options for the default method select
       */
      field = $("#archetypes-fieldname-Method #Method");
      method = $.extend({}, method);
      if (flush) {
        field.empty();
      }
      title = method.title || method.Title;
      uid = method.uid || method.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    };

    AnalysisServiceEditView.prototype.select_default_method = function(uid) {

      /**
       * Select method by UID
       *
       * @param {string} uid
       *    UID of Method to select
       */
      var field;
      field = $("#archetypes-fieldname-Method #Method");
      return this.select_options(field, [uid]);
    };

    AnalysisServiceEditView.prototype.get_default_instrument = function() {

      /**
       * Get the UID of the selected default instrument
       *
       * @returns {string} UID of the default instrument
       */
      var field;
      field = $("#archetypes-fieldname-Instrument #Instrument");
      return field.val();
    };

    AnalysisServiceEditView.prototype.set_default_instrument = function(instrument, flush) {
      var field, title, uid;
      if (flush == null) {
        flush = true;
      }

      /*
       * Set options for the default instrument select
       */
      field = $("#archetypes-fieldname-Instrument #Instrument");
      instrument = $.extend({}, instrument);
      if (flush) {
        field.empty();
      }
      title = instrument.title || instrument.Title;
      uid = instrument.uid || instrument.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    };

    AnalysisServiceEditView.prototype.select_default_instrument = function(uid) {

      /**
       * Select instrument by UID
       *
       * @param {string} uid
       *    UID of Instrument to select
       */
      var field;
      field = $("#archetypes-fieldname-Instrument #Instrument");
      return this.select_options(field, [uid]);
    };

    AnalysisServiceEditView.prototype.use_default_calculation_of_method = function() {

      /**
       * Get the value of the checkbox "Use the Default Calculation of Method"
       *
       * @returns {boolean} True if the calculation of the method should be used
       */
      var field;
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return field.is(":checked");
    };

    AnalysisServiceEditView.prototype.toggle_use_default_calculation_of_method = function(toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the "Use the Default Calculation of Method" checkbox
       */
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return this.toggle_checkbox(field, toggle, silent);
    };

    AnalysisServiceEditView.prototype.get_calculation = function() {

      /**
       * Get the UID of the selected default calculation
       *
       * @returns {string} UID of the calculation
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      return field.val();
    };

    AnalysisServiceEditView.prototype.set_calculation = function(calculation, flush) {
      var field, title, uid;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set the calculation field with the given calculation data
       */
      field = $("#archetypes-fieldname-Calculation #Calculation");
      calculation = $.extend({}, calculation);
      if (flush) {
        field.empty();
      }
      title = calculation.title || calculation.Title;
      uid = calculation.uid || calculation.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    };

    AnalysisServiceEditView.prototype.select_calculation = function(uid) {

      /**
       * Select calculation by UID
       *
       * @param {string} uid
       *    UID of Calculation to select
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      this.select_options(field, [uid]);
      return this.load_calculation(uid).done(function(calculation) {
        return this.set_interims(calculation.InterimFields);
      });
    };

    AnalysisServiceEditView.prototype.get_interims = function() {

      /**
       * Extract the interim field values as a list of objects
       *
       * @returns {array} of interim record objects
       */
      var field, interims, rows;
      field = $("#archetypes-fieldname-InterimFields");
      rows = field.find("tr.records_row_InterimFields");
      interims = [];
      $.each(rows, function(index, row) {
        var inputs, values;
        values = {};
        inputs = row.querySelectorAll("td input");
        $.each(inputs, function(index, input) {
          var key, value;
          key = this.name.split(":")[0].split(".")[1];
          value = input.value;
          if (input.type === "checkbox") {
            value = input.checked;
          }
          values[key] = value;
          return true;
        });
        if (values.keyword !== "") {
          interims.push(values);
        }
        return true;
      });
      return interims;
    };

    AnalysisServiceEditView.prototype.set_interims = function(interims, flush) {
      var field, interim_keys, more_button;
      if (flush == null) {
        flush = true;
      }

      /**
       * Set the interim field values
       *
       * Note: This method takes the same input format as returned from get_interims
       */
      interims = $.extend([], interims);
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      if (flush) {
        this.flush_interims();
      }
      interim_keys = interims.map(function(v) {
        return v.keyword;
      });
      $.each(this.manual_interims, function(index, interim) {
        var i;
        i = interim_keys.indexOf(interim.keyword);
        if (i >= 0) {
          return interims[i] = interim;
        } else {
          return interims.push(interim);
        }
      });
      return $.each(interims, function(index, interim) {
        var inputs, last_row;
        last_row = field.find("tr.records_row_InterimFields").last();
        more_button.click();
        inputs = last_row.find("input");
        return $.each(inputs, function(index, input) {
          var key, value;
          key = this.name.split(":")[0].split(".")[1];
          value = interim[key];
          if (input.type === "checkbox") {
            input.checked = value;
            input.value = "on";
          } else {
            if (!value) {
              value = "";
            }
            input.value = value;
          }
          return true;
        });
      });
    };

    AnalysisServiceEditView.prototype.flush_interims = function() {

      /**
       * Flush interim field
       */
      var field, more_button, rows;
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      more_button.click();
      rows = field.find("tr.records_row_InterimFields");
      return rows.not(":last").remove();
    };

    AnalysisServiceEditView.prototype.set_method_calculation = function(method_uid) {

      /**
       * Loads the calculation of the method and set the interims of it
       *
       * @param {string} method_uid
       *    The UID of the method to set the calculations from
       */
      if (!this.is_uid(method_uid)) {
        this.set_interims(null);
        return this.set_calculation(null);
      } else {
        return this.load_method_calculation(method_uid).done(function(calculation) {
          this.set_calculation(calculation);
          return this.set_interims(calculation.InterimFields);
        });
      }
    };

    AnalysisServiceEditView.prototype.set_instrument_methods = function(instrument_uid, flush) {
      var me;
      if (flush == null) {
        flush = true;
      }

      /**
       * Loads the methods of the instrument
       *
       * @param {string} instrument_uid
       *    The UID of the instrument to set the method from
       */
      me = this;
      if (!this.is_uid(instrument_uid)) {
        return;
      }
      return this.load_instrument_methods(instrument_uid).done(function(methods) {
        methods = $.extend([], methods);
        $.each(methods, function(index, method) {
          flush = index === 0 ? true : false;
          return me.set_default_method(method, flush = flush);
        });
        this.select_default_method(this.selected_default_method);
        if (this.use_default_calculation_of_method()) {
          return this.set_method_calculation(this.get_default_method());
        }
      });
    };

    AnalysisServiceEditView.prototype.show_alert = function(options) {

      /*
       * Display a notification box above the content
       */
      var alerts, flush, html, level, message, title;
      title = options.title || "";
      message = options.message || "";
      level = options.level || "warning";
      flush = options.flush || true;
      alerts = $("#viewlet-above-content #alerts");
      if (alerts.length === 0) {
        $("#viewlet-above-content").append("<div id='alerts'></div>");
      }
      alerts = $("#viewlet-above-content #alerts");
      if (flush) {
        alerts.empty();
      }
      if (message === "") {
        alerts.remove();
      }
      html = "<div class=\"alert alert-" + level + " errorbox\" role=\"alert\">\n  <h3>" + title + "</h3>\n  <div>" + message + "</div>\n</div>";
      return alerts.append(html);
    };


    /* ASYNC DATA LOADERS */

    AnalysisServiceEditView.prototype.load_available_instruments = function() {

      /**
       * Load all available and valid instruments
       *
       * @returns {Deferred} Array of all available Instrument objects
       */
      var deferred, options;
      deferred = $.Deferred();
      options = {
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "bika_setup_catalog",
          page_size: 0,
          portal_type: "Instrument"
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!data.objects) {
          return deferred.resolveWith(this, [[]]);
        }
        return deferred.resolveWith(this, [data.objects]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_instrument_methods = function(instrument_uid) {

      /**
       * Load assigned methods of the instrument
       *
       * @param {string} instrument_uid
       *    The UID of the instrument
       * @returns {Deferred} Array of Method objects
       */
      var deferred, options;
      deferred = $.Deferred();
      if (!this.is_uid(instrument_uid)) {
        deferred.resolveWith(this, [[]]);
        return deferred.promise();
      }
      options = {
        url: this.get_portal_url() + "/get_instrument_methods",
        data: {
          uid: instrument_uid
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!data.methods) {
          deferred.resolveWith(this, [[]]);
        }
        return deferred.resolveWith(this, [data.methods]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_method_calculation = function(method_uid) {

      /**
       * Load assigned calculation of the given method UID
       *
       * @param {string} method_uid
       *    The UID of the method
       * @returns {Deferred} Calculation object
       */
      var deferred, options;
      deferred = $.Deferred();
      if (!this.is_uid(method_uid)) {
        deferred.resolveWith(this, [{}]);
        return deferred.promise();
      }
      options = {
        url: this.get_portal_url() + "/get_method_calculation",
        data: {
          uid: method_uid
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!this.is_uid(data.uid)) {
          return deferred.resolveWith(this, [{}]);
        }
        return this.load_calculation(data.uid).done(function(calculation) {
          return deferred.resolveWith(this, [calculation]);
        });
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_calculation = function(calculation_uid) {

      /*
       * Load calculation object from the JSON API for the given UID
       *
       * @param {string} calculation_uid
       *    The UID of the calculation
       * @returns {Deferred} Calculation object
       */
      var deferred, options;
      deferred = $.Deferred();
      if (!this.is_uid(calculation_uid)) {
        deferred.resolveWith(this, [{}]);
        return deferred.promise();
      }
      options = {
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "bika_setup_catalog",
          page_size: 0,
          UID: calculation_uid,
          is_active: true,
          sort_on: "sortable_title"
        }
      };
      this.ajax_submit(options).done(function(data) {
        var calculation;
        calculation = {};
        if (data.objects.length === 1) {
          calculation = data.objects[0];
        } else {
          console.warn("Invalid data returned for calculation UID " + calculation_uid + ": ", data);
        }
        return deferred.resolveWith(this, [calculation]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_manual_interims = function() {

      /**
       * 1. Load the default calculation
       * 2. Subtract calculation interims from the current active interims
       *
       * XXX: This should be better done by the server!
       *
       * @returns {Deferred} Array of manual interims
       */
      var deferred;
      deferred = $.Deferred();
      this.load_calculation(this.get_calculation()).done(function(calculation) {
        var calculation_interim_keys, calculation_interims, manual_interims;
        calculation_interims = $.extend([], calculation.InterimFields);
        calculation_interim_keys = calculation_interims.map(function(v) {
          return v.keyword;
        });
        manual_interims = [];
        $.each(this.get_interims(), function(index, value) {
          var calculation_interim, i, ref;
          if (ref = value.keyword, indexOf.call(calculation_interim_keys, ref) < 0) {
            return manual_interims.push(value);
          } else {
            i = calculation_interim_keys.indexOf(value.keyword);
            calculation_interim = calculation_interims[i];
            return $.each(calculation_interim, function(k, v) {
              if (v !== value[k]) {
                manual_interims.push(value);
                return false;
              }
            });
          }
        });
        return deferred.resolveWith(this, [manual_interims]);
      });
      return deferred.promise();
    };

    AnalysisServiceEditView.prototype.load_object_by_uid = function(uid) {

      /*
       * Load object by UID
       *
       * @returns {Deferred}
       */
      var deferred, options;
      deferred = $.Deferred();
      options = {
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "uid_catalog",
          page_size: 0,
          UID: uid
        }
      };
      this.ajax_submit(options).done(function(data) {
        var object;
        object = {};
        if (data.objects.length === 1) {
          object = data.objects[0];
        }
        return deferred.resolveWith(this, [object]);
      });
      return deferred.promise();
    };


    /* HELPERS */

    AnalysisServiceEditView.prototype.ajax_submit = function(options) {

      /**
       * Ajax Submit with automatic event triggering and some sane defaults
       *
       * @param {object} options
       *    jQuery ajax options
       * @returns {Deferred} XHR request
       */
      var base, done;
      console.debug("°°° ajax_submit °°°");
      if (options == null) {
        options = {};
      }
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_portal_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      if (options.dataType == null) {
        options.dataType = "json";
      }
      if (options.data == null) {
        options.data = {};
      }
      if ((base = options.data)._authenticator == null) {
        base._authenticator = $("input[name='_authenticator']").val();
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = function() {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
    };

    AnalysisServiceEditView.prototype.get_url = function() {

      /**
       * Return the current absolute url
       *
       * @returns {string} current absolute url
       */
      var host, location, pathname, protocol;
      location = window.location;
      protocol = location.protocol;
      host = location.host;
      pathname = location.pathname;
      return protocol + "//" + host + pathname;
    };

    AnalysisServiceEditView.prototype.get_portal_url = function() {

      /**
       * Return the portal url
       *
       * @returns {string} portal url
       */
      return window.portal_url;
    };

    AnalysisServiceEditView.prototype.is_uid = function(str) {

      /**
       * Validate valid UID
       *
       * @returns {boolean} True if the argument is a UID
       */
      var match;
      if (typeof str !== "string") {
        return false;
      }
      match = str.match(/[a-z0-9]{32}/);
      return match !== null;
    };

    AnalysisServiceEditView.prototype.add_select_option = function(select, name, value) {

      /**
       * Adds an option to the select
       */
      var option;
      if (value) {
        option = "<option value='" + value + "'>" + (this._(name)) + "</option>";
      } else {
        option = "<option selected='selected' value=''>" + (this._("None")) + "</option>";
      }
      return $(select).append(option);
    };

    AnalysisServiceEditView.prototype.parse_select_options = function(select) {

      /**
       * Parse UID/Title from the select field
       *
       * @returns {Array} of UID/Title objects
       */
      var options;
      options = [];
      $.each($(select).children(), function(index, option) {
        var title, uid;
        uid = option.value;
        title = option.innerText;
        if (!uid) {
          return;
        }
        return options.push({
          uid: uid,
          title: title
        });
      });
      return options;
    };

    AnalysisServiceEditView.prototype.parse_select_option = function(select, value) {

      /**
       * Return the option by value
       */
      var data, option;
      option = field.find("option[value=" + uid + "]");
      data = {
        uid: option.val() || "",
        title: option.text() || ""
      };
      return data;
    };

    AnalysisServiceEditView.prototype.select_options = function(select, values) {

      /**
       * Select the options of the given select field where the value is in values
       */
      return $.each($(select).children(), function(index, option) {
        var value;
        value = option.value;
        if (indexOf.call(values, value) < 0) {
          return;
        }
        return option.selected = "selected";
      });
    };

    AnalysisServiceEditView.prototype.toggle_checkbox = function(checkbox, toggle, silent) {
      var field;
      if (silent == null) {
        silent = true;
      }

      /**
       * Toggle the checkbox
       *
       * @param {element} checkbox
       *    The checkbox to toggle
       *
       * @param {boolean} toggle
       *    True to check the checkbox
       *
       * @param {boolean} silent
       *    True to trigger a "change" event after set
       */
      field = $(checkbox);
      if (toggle === void 0) {
        toggle = !field.is(":checked");
      }
      field.prop("checked", toggle);
      if (!silent) {
        return field.trigger("change");
      }
    };


    /* EVENT HANDLER */

    AnalysisServiceEditView.prototype.on_manual_entry_of_results_change = function(event) {

      /**
       * Eventhandler when the "Instrument assignment is not required" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°");
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual entry of results is allowed");
        return this.set_methods(this.methods);
      } else {
        console.debug("Manual entry of results is **not** allowed");
        return this.set_methods(null);
      }
    };

    AnalysisServiceEditView.prototype.on_methods_change = function(event) {

      /**
       * Eventhandler when the "Methods" multiselect changed
       */
      var method_uids;
      console.debug("°°° AnalysisServiceEditView::on_methods_change °°°");
      method_uids = this.get_methods();
      if (method_uids.length === 0) {
        console.warn("All methods deselected");
      }
      return this.select_methods(method_uids);
    };

    AnalysisServiceEditView.prototype.on_instrument_assignment_allowed_change = function(event) {

      /**
       * Eventhandler when the "Instrument assignment is allowed" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°");
      if (this.is_instrument_assignment_allowed()) {
        console.debug("Instrument assignment is allowed");
        return this.set_instruments(this.instruments);
      } else {
        console.debug("Instrument assignment is **not** allowed");
        return this.set_instruments(null);
      }
    };

    AnalysisServiceEditView.prototype.on_instruments_change = function(event) {

      /**
       * Eventhandler when the "Instruments" multiselect changed
       */
      var instrument_uids;
      console.debug("°°° AnalysisServiceEditView::on_instruments_change °°°");
      instrument_uids = this.get_instruments();
      if (instrument_uids.length === 0) {
        console.warn("All instruments deselected");
      }
      return this.select_instruments(instrument_uids);
    };

    AnalysisServiceEditView.prototype.on_default_instrument_change = function(event) {

      /**
       * Eventhandler when the "Default Instrument" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_default_instrument_change °°°");
      return this.set_instrument_methods(this.get_default_instrument());
    };

    AnalysisServiceEditView.prototype.on_default_method_change = function(event) {

      /**
       * Eventhandler when the "Default Method" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_default_method_change °°°");
      if (this.use_default_calculation_of_method()) {
        return this.set_method_calculation(this.get_default_method());
      }
    };

    AnalysisServiceEditView.prototype.on_use_default_calculation_change = function(event) {

      /**
       * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
       */
      var me;
      console.debug("°°° AnalysisServiceEditView::on_use_default_calculation_change °°°");
      if (this.use_default_calculation_of_method()) {
        console.debug("Use default calculation");
        return this.set_method_calculation(this.get_default_method());
      } else {
        me = this;
        $.each(this.calculations, function(index, calculation) {
          var flush;
          flush = index === 0 ? true : false;
          return me.set_calculation(calculation, flush = flush);
        });
        if (this.selected_calculation) {
          return this.select_calculation(this.selected_calculation);
        } else {
          return this.select_calculation(this.get_calculation());
        }
      }
    };

    AnalysisServiceEditView.prototype.on_calculation_change = function(event) {

      /**
       * Eventhandler when the "Calculation" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_calculation_change °°°");
      return this.select_calculation(this.get_calculation());
    };

    AnalysisServiceEditView.prototype.on_separate_container_change = function(event) {

      /**
       * Eventhandler when the "Separate Container" checkbox changed
       *
       * This checkbox is located on the "Container and Preservation" Tab
       */
      var value;
      console.debug("°°° AnalysisServiceEditView::on_separate_container_change °°°");
      return value = event.currentTarget.checked;
    };

    AnalysisServiceEditView.prototype.on_default_preservation_change = function(event) {

      /**
       * Eventhandler when the "Default Preservation" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_default_preservation_change °°°");
    };

    AnalysisServiceEditView.prototype.on_default_container_change = function(event) {

      /**
       * Eventhandler when the "Default Container" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      var el, field, uid;
      console.debug("°°° AnalysisServiceEditView::on_default_container_change °°°");
      el = event.currentTarget;
      uid = el.getAttribute("uid");
      field = $("#archetypes-fieldname-Preservation #Preservation");
      return this.load_object_by_uid(uid).done(function(data) {
        if (data) {
          field.val(data.Preservation);
          return field.prop("disabled", true);
        } else {
          field.val("");
          return field.prop("disabled", false);
        }
      });
    };

    AnalysisServiceEditView.prototype.on_partition_sampletype_change = function(event) {

      /**
       * Eventhandler when the "Sample Type" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      var el, uid;
      console.debug("°°° AnalysisServiceEditView::on_partition_sampletype_change °°°");
      el = event.currentTarget;
      uid = el.value;
      return this.load_object_by_uid(uid).done(function(sampletype) {
        var minvol;
        minvol = sampletype.MinimumVolume || "";
        return $(el).parents("tr").find("[name^='PartitionSetup.vol']").val(minvol);
      });
    };

    AnalysisServiceEditView.prototype.on_partition_separate_container_change = function(event) {

      /**
       * Eventhandler when the "Separate Container" checkbox changed
       *
       * This checkbox is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_partition_separate_container_change °°°");
    };

    AnalysisServiceEditView.prototype.on_partition_container_change = function(event) {

      /**
       * Eventhandler when the "Container" multi-select changed
       *
       * This multi select is located on the "Container and Preservation" Tab
       */
      var el, field, uid;
      console.debug("°°° AnalysisServiceEditView::on_partition_container_change °°°");
      el = event.currentTarget;
      uid = el.value;
      field = $(el).parents("tr").find("[name^='PartitionSetup.preservation']");
      return this.load_object_by_uid(uid).done(function(data) {
        if (!$.isEmptyObject(data)) {
          $(el).val(data.UID);
          $(field).val(data.Preservation);
          return $(field).prop("disabled", true);
        } else {
          return $(field).prop("disabled", false);
        }
      });
    };

    AnalysisServiceEditView.prototype.on_partition_required_volume_change = function(event) {

      /**
       * Eventhandler when the "Required Volume" value changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_partition_required_volume_change °°°");
    };

    return AnalysisServiceEditView;

  })();

}).call(this);
