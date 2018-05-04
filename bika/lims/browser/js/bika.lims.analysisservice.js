(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
  */
  var indexOf = [].indexOf;

  window.AnalysisServiceEditView = class AnalysisServiceEditView {
    constructor() {
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.init_interims = this.init_interims.bind(this);
      this.init_form = this.init_form.bind(this);
      /* FIELD GETTERS/SETTERS */
      this.is_manual_entry_of_results_allowed = this.is_manual_entry_of_results_allowed.bind(this);
      this.toggle_manual_entry_of_results_allowed = this.toggle_manual_entry_of_results_allowed.bind(this);
      this.get_methods = this.get_methods.bind(this);
      this.set_methods = this.set_methods.bind(this);
      this.is_instrument_assignment_allowed = this.is_instrument_assignment_allowed.bind(this);
      this.toggle_instrument_assignment_allowed = this.toggle_instrument_assignment_allowed.bind(this);
      this.get_instruments = this.get_instruments.bind(this);
      this.set_instruments = this.set_instruments.bind(this);
      this.get_default_method = this.get_default_method.bind(this);
      this.set_default_method = this.set_default_method.bind(this);
      this.get_default_instrument = this.get_default_instrument.bind(this);
      this.set_default_instrument = this.set_default_instrument.bind(this);
      this.use_default_calculation_of_method = this.use_default_calculation_of_method.bind(this);
      this.toggle_use_default_calculation_of_method = this.toggle_use_default_calculation_of_method.bind(this);
      this.get_calculation = this.get_calculation.bind(this);
      this.set_calculation = this.set_calculation.bind(this);
      this.get_interims = this.get_interims.bind(this);
      this.set_interims = this.set_interims.bind(this);
      this.flush_interims = this.flush_interims.bind(this);
      this.set_method_calculation = this.set_method_calculation.bind(this);
      this.set_instrument_methods = this.set_instrument_methods.bind(this);
      this.set_all_methods = this.set_all_methods.bind(this);
      this.set_all_instruments = this.set_all_instruments.bind(this);
      this.set_all_calculations = this.set_all_calculations.bind(this);
      /* ASYNC DATA LOADERS */
      this.load_available_calculations = this.load_available_calculations.bind(this);
      this.load_available_instruments = this.load_available_instruments.bind(this);
      this.load_available_methods = this.load_available_methods.bind(this);
      this.load_instrument_methods = this.load_instrument_methods.bind(this);
      this.load_method_calculation = this.load_method_calculation.bind(this);
      this.load_calculation = this.load_calculation.bind(this);
      /* HELPERS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.is_uid = this.is_uid.bind(this);
      this.add_select_option = this.add_select_option.bind(this);
      this.select_first = this.select_first.bind(this);
      /* EVENT HANDLER */
      this.on_manual_entry_of_results_change = this.on_manual_entry_of_results_change.bind(this);
      this.on_methods_change = this.on_methods_change.bind(this);
      this.on_instrument_assignment_allowed_change = this.on_instrument_assignment_allowed_change.bind(this);
      // XXX Which instrument to load now?
      this.on_instruments_change = this.on_instruments_change.bind(this);
      this.on_default_instrument_change = this.on_default_instrument_change.bind(this);
      this.on_default_method_change = this.on_default_method_change.bind(this);
      this.on_use_default_calculation_change = this.on_use_default_calculation_change.bind(this);
      this.on_calculation_change = this.on_calculation_change.bind(this);
      this.on_display_detection_limit_selector_change = this.on_display_detection_limit_selector_change.bind(this);
    }

    load() {
      console.debug("AnalysisServiceEditView::load");
      // load translations
      jarn.i18n.loadCatalog("bika");
      this._ = window.jarn.i18n.MessageFactory("bika");
      // Interim values defined by the user (not part of a calculation)
      this.manual_interims = [];
      // bind the event handler to the elements
      this.bind_eventhandler();
      // Initialize the interims
      this.init_interims();
      // Initialize the form
      this.init_form();
      // Dev only
      return window.asv = this;
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       */
      console.debug("AnalysisServiceEditView::bind_eventhandler");
      /* METHODS TAB */
      // The "Instrument assignment is not required" checkbox changed
      $("body").on("change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", this.on_manual_entry_of_results_change);
      // The "Methods" multiselect changed
      $("body").on("change", "#archetypes-fieldname-Methods #Methods", this.on_methods_change);
      // The "Instrument assignment is allowed" checkbox changed
      $("body").on("change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", this.on_instrument_assignment_allowed_change);
      // The "Instruments" multiselect changed
      $("body").on("change", "#archetypes-fieldname-Instruments #Instruments", this.on_instruments_change);
      // The "Default Instrument" selector changed
      $("body").on("change", "#archetypes-fieldname-Instrument #Instrument", this.on_default_instrument_change);
      // The "Default Method" select changed
      $("body").on("change", "#archetypes-fieldname-Method #Method", this.on_default_method_change);
      // The "Use the Default Calculation of Method" checkbox changed
      $("body").on("change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", this.on_use_default_calculation_change);
      // The "Calculation" selector changed
      $("body").on("change", "#archetypes-fieldname-Calculation #Calculation", this.on_calculation_change);
      /* ANALYSIS TAB */
      // The "Display a Detection Limit selector" checkbox changed
      return $("body").on("change", "#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector", this.on_display_detection_limit_selector_change);
    }

    init_interims() {
      /**
       * 1. Check if field "Use the Default Calculation of Method" is checked
       * 2. Fetch the selected calculation
       * 3. Replace the calculation select box with the calculations
       * 4. Separate manual set interims from calculation interims
       */
      var me;
      me = this;
      return this.load_calculation(this.get_calculation()).done(function(calculation) {
        var calculation_interim_keys, calculation_interims, manual_interims;
        // set the calculation field
        this.set_calculation(calculation);
        // interims of this calculation
        calculation_interims = $.extend([], calculation.InterimFields);
        // extract the keys of the calculation interims
        calculation_interim_keys = calculation_interims.map(function(v) {
          return v.keyword;
        });
        // separate manual interims from calculation interims
        manual_interims = [];
        $.each(this.get_interims(), function(index, value) {
          var ref;
          if (ref = value.keyword, indexOf.call(calculation_interim_keys, ref) < 0) {
            return manual_interims.push(value);
          }
        });
        // remember the manual set interims of this AS
        // -> they are kept on calculation change
        return this.manual_interims = manual_interims;
      });
    }

    init_form() {
      /**
       * Initialize form
       */
      // Init "Instrument assignment is not required" checkbox
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual Entry of Results is allowed");
        this.toggle_instrument_assignment_allowed(true);
      } else {
        console.debug("Manual Entry of Results is **not** allowed");
        // flush all methods and add only the "None" option
        this.set_methods(null);
      }
      // Init "Instrument assignment is allowed" checkbox
      if (this.is_instrument_assignment_allowed()) {
        return console.debug("Instrument assignment is allowed");
      } else {
        console.debug("Instrument assignment is **not** allowed");
        // flush all instruments and add only the "None" option
        return this.set_instruments(null);
      }
    }

    is_manual_entry_of_results_allowed() {
      /**
       * Get the value of the checkbox "Instrument assignment is not required"
       *
       * @returns {boolean} True if results can be entered without instrument
       */
      var field;
      field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults");
      return field.is(":checked");
    }

    toggle_manual_entry_of_results_allowed(toggle, silent = false) {
      /**
       * Toggle the "Instrument assignment is not required" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults");
      if (toggle === void 0) {
        toggle = !field.is(":checked");
      }
      field.prop("checked", toggle);
      // trigger change event
      if (!silent) {
        return field.trigger("change");
      }
    }

    get_methods() {
      /**
       * Get all selected method UIDs from the multiselect field
       *
       * @returns {array} of method objects
       */
      var field;
      field = $("#archetypes-fieldname-Methods #Methods");
      return $.extend([], field.val());
    }

    set_methods(methods, flush = true) {
      /**
       * Set the methods multiselect field with the given methods
       *
       * @param {array} methods
       *    Array of method objects with at least `title` and `uid` keys set
       */
      var field, me;
      field = $("#archetypes-fieldname-Methods #Methods");
      // create a copy of the methods array
      methods = $.extend([], methods);
      // empty the field if the `flush` flag is set
      if (flush) {
        field.empty();
      }
      if (methods.length === 0) {
        return this.add_select_option(field, null);
      } else {
        me = this;
        return $.each(methods, function(index, method) {
          var title, uid;
          title = method.title || method.Title;
          uid = method.uid || method.UID;
          return me.add_select_option(field, title, uid);
        });
      }
    }

    is_instrument_assignment_allowed() {
      /**
       * Get the value of the checkbox "Instrument assignment is allowed"
       *
       * @returns {boolean} True if instrument assignment is allowed
       */
      var field;
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      return field.is(":checked");
    }

    toggle_instrument_assignment_allowed(toggle, silent = false) {
      /**
       * Toggle the "Instrument assignment is allowed" checkbox
       *
       * @param {boolean} toggle
       *    True to check the checkbox, False to uncheck the checkbox
       */
      var field;
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      if (toggle === void 0) {
        toggle = !field.is(":checked");
      }
      field.prop("checked", toggle);
      // trigger change event
      if (!silent) {
        return field.trigger("change");
      }
    }

    get_instruments() {
      /**
       * Get all selected instrument UIDs from the multiselect
       *
       * @returns {array} of instrument objects
       */
      var field;
      field = $("#archetypes-fieldname-Instruments #Instruments");
      return $.extend([], field.val());
    }

    set_instruments(instruments, flush = true) {
      /*
       * Set the instruments to the field
       *
       * @param {array} instruments
       *    Array of instrument objects to set in the multi-select
       */
      var field, me;
      field = $("#archetypes-fieldname-Instruments #Instruments");
      // create a copy of the instruments array
      instruments = $.extend([], instruments);
      // empty the field if the `flush` flag is set
      if (flush) {
        field.empty();
      }
      if (instruments.length === 0) {
        return this.add_select_option(field, null);
      } else {
        // set the instruments
        me = this;
        return $.each(instruments, function(index, instrument) {
          var title, uid;
          uid = instrument.uid || instrument.UID;
          title = instrument.title || instrument.Title;
          return me.add_select_option(field, title, uid);
        });
      }
    }

    get_default_method() {
      /**
       * Get the UID of the selected default method
       *
       * @returns {string} UID of the default method
       */
      var field;
      field = $("#archetypes-fieldname-Method #Method");
      return field.val();
    }

    set_default_method(method, flush = true) {
      /**
       * Set options for the default method select
       */
      var field, title, uid;
      field = $("#archetypes-fieldname-Method #Method");
      // create a copy of the method
      method = $.extend({}, method);
      // empty the field first
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
    }

    get_default_instrument() {
      /**
       * Get the UID of the selected default instrument
       *
       * @returns {string} UID of the default instrument
       */
      var field;
      field = $("#archetypes-fieldname-Instrument #Instrument");
      return field.val();
    }

    set_default_instrument(instrument, flush = true) {
      /*
       * Set options for the default instrument select
       */
      var field, title, uid;
      field = $("#archetypes-fieldname-Instrument #Instrument");
      // create a copy of the instrument
      instrument = $.extend({}, instrument);
      // empty the field first
      if (flush) {
        field.empty();
      }
      title = instrument.title;
      uid = instrument.uid;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    }

    use_default_calculation_of_method() {
      /**
       * Get the value of the checkbox "Use the Default Calculation of Method"
       *
       * @returns {boolean} True if the calculation of the method should be used
       */
      var field;
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return field.is(":checked");
    }

    toggle_use_default_calculation_of_method(toggle, silent = false) {
      /**
       * Toggle the "Use the Default Calculation of Method" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      if (toggle === void 0) {
        toggle = !field.is(":checked");
      }
      field.prop("checked", toggle);
      // trigger change event
      if (!silent) {
        return field.trigger("change");
      }
    }

    get_calculation() {
      /**
       * Get the UID of the selected default calculation
       *
       * @returns {string} UID of the calculation
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      return field.val();
    }

    set_calculation(calculation, flush = true) {
      /**
       * Set the calculation field with the given calculation data
       */
      var field, title, uid;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      // create a copy of the calculation
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
    }

    get_interims() {
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
        var values;
        values = {};
        $.each($(row).find("td input"), function(index, input) {
          var key, value;
          // Extract the key from the element name
          // InterimFields.keyword:records:ignore_empty
          key = this.name.split(":")[0].split(".")[1];
          value = input.value;
          if (input.type === "checkbox") {
            value = input.checked;
          }
          return values[key] = value;
        });
        // Only rows with Keyword set
        if (values.keyword !== "") {
          return interims.push(values);
        }
      });
      return interims;
    }

    set_interims(interims, flush = true) {
      var field, more_button;
      /**
       * Set the interim field values
       *
       * Note: This method takes the same input format as returned from get_interims
       */
      // create a copy of the calculation interims
      interims = $.extend([], interims);
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      // empty all interims
      if (flush) {
        this.flush_interims();
      }
      // always keep manual set interims
      $.each(this.manual_interims, function(index, interim) {
        return interims.push(interim);
      });
      return $.each(interims, function(index, interim) {
        var inputs, last_row;
        last_row = field.find("tr.records_row_InterimFields").last();
        more_button.click();
        inputs = last_row.find("input");
        // iterate over all inputs of the interim field
        return $.each(inputs, function(index, input) {
          var key, value;
          key = this.name.split(":")[0].split(".")[1];
          value = interim[key];
          if (input.type === "checkbox") {
            // transform to bool value
            if (value) {
              value = true;
            } else {
              value = false;
            }
            return input.checked = value;
          } else {
            if (!value) {
              value = "";
            }
            return input.value = value;
          }
        });
      });
    }

    flush_interims() {
      /**
       * Flush interim field
       */
      var field, more_button, rows;
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      more_button.click();
      rows = field.find("tr.records_row_InterimFields");
      return rows.not(":last").remove();
    }

    set_method_calculation(method_uid) {
      /**
       * Loads the calculation of the method and set the interims of it
       *
       * @param {string} method_uid
       *    The UID of the method to set the calculations from
       */
      if (!this.is_uid(method_uid)) {
        // remove all calculation interims
        this.set_interims(null);
        // Set empty calculation
        return this.set_calculation(null);
      } else {
        // load the assigned calculation of the method
        return this.load_method_calculation(method_uid).done(function(calculation) {
          // set the default calculation
          this.set_calculation(calculation);
          // set the interims of the default calculation
          return this.set_interims(calculation.InterimFields);
        });
      }
    }

    set_instrument_methods(instrument_uid, flush = true) {
      /**
       * Loads the calculation of the method and set the interims of it
       *
       * @param {string} instrument_uid
       *    The UID of the instrument to set the method from
       */
      var me;
      me = this;
      // Set empty instrument if method UID is not set
      if (!this.is_uid(instrument_uid)) {
        return this.set_methods(null);
      }
      return this.load_instrument_methods(instrument_uid).done(function(methods) {
        methods = $.extend([], methods);
        return $.each(methods, function(index, method) {
          flush = index === 0 ? true : false;
          return me.set_default_method(method, flush = flush);
        });
      });
    }

    set_all_methods() {
      var methods;
      /**
       * Load and set all available methods
       */
      if (this._methods) {
        methods = $.extend([], this._methods);
        return this.set_methods(methods);
      } else {
        return this.load_available_methods().done(function(methods) {
          this.set_methods(methods);
          // cache
          return this._methods = methods;
        });
      }
    }

    set_all_instruments() {
      var instruments;
      /**
       * Load and set all available instruments
       */
      if (this._instruments) {
        instruments = $.extend([], this._instruments);
        return this.set_instruments(instruments);
      } else {
        return this.load_available_instruments().done(function(instruments) {
          this.set_instruments(instruments);
          // cache
          return this._instruments = instruments;
        });
      }
    }

    set_all_calculations() {
      /*
       * Load and set all available calculations
       */
      return this.load_available_calculations().done(function(calculations) {
        var me;
        me = this;
        $.each(calculations, function(index, calculation) {
          var flush;
          // flush only initially
          flush = index === 0 ? true : false;
          return me.set_calculation(calculation, flush);
        });
        // flush interims
        return this.set_interims(null);
      });
    }

    load_available_calculations() {
      /**
       * Load all available calculations
       *
       * @returns {Deferred} Array of all available Calculation objects
       */
      var deferred, options;
      deferred = $.Deferred();
      options = {
        url: this.get_portal_url() + "/get_available_calculations"
      };
      return this.ajax_submit(options).done(function(data) {
        if (!data.objects) {
          // resolve with an empty array
          return deferred.resolveWith(this, [[]]);
        }
        // resolve with data objects
        return deferred.resolveWith(this, [data.objects]);
      });
    }

    load_available_instruments() {
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
          portal_type: "Instrument",
          inactive_state: "active",
          sort_on: "sortable_title"
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!data.objects) {
          // resolve with an empty array
          return deferred.resolveWith(this, [[]]);
        }
        // resolve with data objects
        return deferred.resolveWith(this, [data.objects]);
      });
      return deferred.promise();
    }

    load_available_methods() {
      /**
       * Load all available and valid instruments
       *
       * @returns {Deferred} Array of all available Method objects
       */
      var deferred, options;
      deferred = $.Deferred();
      options = {
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "bika_setup_catalog",
          page_size: 0,
          portal_type: "Method",
          inactive_state: "active",
          sort_on: "sortable_title"
        }
      };
      this.ajax_submit(options).done(function(data) {
        if (!data.objects) {
          // resolve with an empty array
          return deferred.resolveWith(this, [[]]);
        }
        return deferred.resolveWith(this, [data.objects]);
      });
      return deferred.promise();
    }

    load_instrument_methods(instrument_uid) {
      /**
       * Load assigned methods of the instrument
       *
       * @param {string} instrument_uid
       *    The UID of the instrument
       * @returns {Deferred} Array of Method objects
       */
      var deferred, options;
      deferred = $.Deferred();
      // return immediately if we do not have a valid UID
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
        // {instrument: "51ebff9bf1314d00a7731b2f765dac37", methods: Array(3), title: "My Instrument"}
        // where `methods` is an array of {uid: "3a85b7bc0430496ba7d0a6bcb9cdc5d5", title: "My Method"}
        if (!data.methods) {
          // resolve with an empty array
          deferred.resolveWith(this, [[]]);
        }
        return deferred.resolveWith(this, [data.methods]);
      });
      return deferred.promise();
    }

    load_method_calculation(method_uid) {
      /**
       * Load assigned calculation of the given method UID
       *
       * @param {string} method_uid
       *    The UID of the method
       * @returns {Deferred} Calculation object
       */
      var deferred, options;
      deferred = $.Deferred();
      // return immediately if we do not have a valid UID
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
        // /get_method_calculation returns just this structure:
        // {uid: "488400e9f5e24a4cbd214056e6b5e2aa", title: "My Calculation"}
        if (!this.is_uid(data.uid)) {
          return deferred.resolveWith(this, [{}]);
        }
        // load the full calculation object
        return this.load_calculation(data.uid).done(function(calculation) {
          // resolve with the full calculation object
          return deferred.resolveWith(this, [calculation]);
        });
      });
      return deferred.promise();
    }

    load_calculation(calculation_uid) {
      /*
       * Load calculation object from the JSON API for the given UID
       *
       * @param {string} calculation_uid
       *    The UID of the calculation
       * @returns {Deferred} Calculation object
       */
      var deferred, options;
      deferred = $.Deferred();
      // return immediately if we do not have a valid UID
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
          inactive_state: "active",
          sort_on: "sortable_title"
        }
      };
      this.ajax_submit(options).done(function(data) {
        var calculation;
        calculation = {};
        // Parse the calculation object from the response data
        if (data.objects.length === 1) {
          calculation = data.objects[0];
        } else {
          console.warn(`Invalid data returned for calculation UID ${calculation_uid}: `, data);
        }
        // Resolve the deferred with the parsed calculation
        return deferred.resolveWith(this, [calculation]);
      });
      return deferred.promise();
    }

    ajax_submit(options) {
      var base, done;
      /**
       * Ajax Submit with automatic event triggering and some sane defaults
       *
       * @param {object} options
       *    jQuery ajax options
       * @returns {Deferred} XHR request
       */
      console.debug("°°° ajax_submit °°°");
      // some sane option defaults
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
    }

    get_portal_url() {
      /**
       * Return the portal url
       *
       * @returns {string} portal url
       */
      return window.portal_url;
    }

    is_uid(str) {
      var match;
      /**
       * Validate valid UID
       *
       * @returns {boolean} True if the argument is a UID
       */
      if (typeof str !== "string") {
        return false;
      }
      match = str.match(/[a-z0-9]{32}/);
      return match !== null;
    }

    add_select_option(select, name, value) {
      var option;
      /**
       * Adds an option to the select
       */
      // empty option
      if (!value) {
        name = "None";
      }
      option = `<option value='${value}'>${this._(name)}</option>`;
      return $(select).append(option);
    }

    select_first(select) {
      /**
       * Select the first option of the select element
       */
      return $(select).children().first().prop("selected", true);
    }

    on_manual_entry_of_results_change(event) {
      /**
       * Eventhandler when the "Instrument assignment is not required" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°");
      // Results can be set by "hand"
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual entry of results is allowed");
        // load all methods to the methods multi-select
        this.set_all_methods();
        // set the methods of the default instrument
        return this.set_instrument_methods(this.get_default_instrument());
      } else {
        // Results can be only set by an instrument
        console.debug("Manual entry of results is **not** allowed");
        // Flush all methods ()
        this.set_methods(null);
        // Flush default method
        this.set_default_method(null);
        // Flush default instrument
        this.set_default_instrument(null);
        // Enable instrument assignment
        this.toggle_instrument_assignment_allowed(true);
        // Disable "Use the Default Calculation of Method"
        return this.toggle_use_default_calculation_of_method(false);
      }
    }

    on_methods_change(event) {
      var me, method_uids;
      /**
       * Eventhandler when the "Methods" multiselect changed
       */
      console.debug("°°° AnalysisServiceEditView::on_methods_change °°°");
      // selected method UIDs
      method_uids = this.get_methods();
      // All methods deselected
      if (method_uids.length === 0) {
        console.warn("All methods deselected");
      }
      // Set selected methods to the list of the default methods
      me = this;
      $.each(method_uids, function(index, uid) {
        var $el, flush, method, option;
        flush = index === 0 && true || false;
        // extract the title and uid from the option element
        $el = $(event.currentTarget);
        option = $el.find(`option[value=${uid}]`);
        method = {
          uid: option.val(),
          title: option.text()
        };
        return me.set_default_method(method, flush = flush);
      });
      // set the calculation of the default method
      return this.set_method_calculation(this.get_default_method());
    }

    on_instrument_assignment_allowed_change(event) {
      /**
       * Eventhandler when the "Instrument assignment is allowed" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°");
      if (this.is_instrument_assignment_allowed()) {
        console.debug("Instrument assignment is allowed");
        // load all instruments to the instruments multi-select
        return this.set_all_instruments();
      } else {
        console.debug("Instrument assignment is **not** allowed");
        this.set_instruments(null);
        return this.set_default_instrument(null);
      }
    }

    on_instruments_change(event) {
      var instrument_uids, me;
      /**
       * Eventhandler when the "Instruments" multiselect changed
       */
      console.debug("°°° AnalysisServiceEditView::on_instruments_change °°°");
      // selected instrument UIDs
      instrument_uids = this.get_instruments();
      if (instrument_uids.length === 0) {
        console.warn("All instruments deselected");
      }
      // Set selected instruments to the list of the default instruments
      me = this;
      $.each(instrument_uids, function(index, uid) {
        var $el, flush, instrument, option;
        flush = index === 0 && true || false;
        // extract the title and uid from the option element
        $el = $(event.currentTarget);
        option = $el.find(`option[value=${uid}]`);
        instrument = {
          uid: option.val(),
          title: option.text()
        };
        return me.set_default_instrument(instrument, flush = flush);
      });
      // set the instrument methods of the default instrument
      return this.set_instrument_methods(this.get_default_instrument());
    }

    on_default_instrument_change(event) {
      /**
       * Eventhandler when the "Default Instrument" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_default_instrument_change °°°");
      // set the instrument methods of the default instrument
      return this.set_instrument_methods(this.get_default_instrument());
    }

    on_default_method_change(event) {
      var method_uid;
      /**
       * Eventhandler when the "Default Method" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_default_method_change °°°");
      // Load the calculation of the method if the checkbox "Use the Default
      // Calculation of Method" is checked
      if (this.use_default_calculation_of_method()) {
        // Get the UID of the default Method
        method_uid = this.get_default_method();
        // set the calculation of the method
        return this.set_method_calculation(method_uid);
      }
    }

    on_use_default_calculation_change(event) {
      /**
       * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_use_default_calculation_change °°°");
      // "Use the Default Calculation of Method" checkbox checked
      if (this.use_default_calculation_of_method()) {
        // set the calculation of the method
        return this.set_method_calculation(this.get_default_method());
      } else {
        // load all available calculations
        return this.set_all_calculations();
      }
    }

    on_calculation_change(event) {
      /**
       * Eventhandler when the "Calculation" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_calculation_change °°°");
      // load the calculation now, to set the interims
      return this.load_calculation(this.get_calculation()).done(function(calculation) {
        return this.set_interims(calculation.InterimFields);
      });
    }

    on_display_detection_limit_selector_change(event) {
      /**
       * Eventhandler when the "Display a Detection Limit selector" checkbox changed
       *
       * This checkbox is located on the "Analysis" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°");
    }

  };

}).call(this);
