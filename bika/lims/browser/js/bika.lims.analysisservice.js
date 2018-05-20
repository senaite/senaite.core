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
      this.init = this.init.bind(this);
      /* FIELD GETTERS/SETTERS/SELECTORS */
      this.is_manual_entry_of_results_allowed = this.is_manual_entry_of_results_allowed.bind(this);
      this.toggle_manual_entry_of_results_allowed = this.toggle_manual_entry_of_results_allowed.bind(this);
      this.get_methods = this.get_methods.bind(this);
      this.set_methods = this.set_methods.bind(this);
      this.select_methods = this.select_methods.bind(this);
      this.is_instrument_assignment_allowed = this.is_instrument_assignment_allowed.bind(this);
      this.toggle_instrument_assignment_allowed = this.toggle_instrument_assignment_allowed.bind(this);
      this.get_instruments = this.get_instruments.bind(this);
      this.set_instruments = this.set_instruments.bind(this);
      this.select_instruments = this.select_instruments.bind(this);
      this.get_default_method = this.get_default_method.bind(this);
      this.set_default_method = this.set_default_method.bind(this);
      this.select_default_method = this.select_default_method.bind(this);
      this.get_default_instrument = this.get_default_instrument.bind(this);
      this.set_default_instrument = this.set_default_instrument.bind(this);
      this.select_default_instrument = this.select_default_instrument.bind(this);
      this.use_default_calculation_of_method = this.use_default_calculation_of_method.bind(this);
      this.toggle_use_default_calculation_of_method = this.toggle_use_default_calculation_of_method.bind(this);
      this.get_calculation = this.get_calculation.bind(this);
      this.set_calculation = this.set_calculation.bind(this);
      this.select_calculation = this.select_calculation.bind(this);
      this.get_interims = this.get_interims.bind(this);
      this.set_interims = this.set_interims.bind(this);
      this.flush_interims = this.flush_interims.bind(this);
      this.set_method_calculation = this.set_method_calculation.bind(this);
      this.set_instrument_methods = this.set_instrument_methods.bind(this);
      this.display_detection_limit_selector = this.display_detection_limit_selector.bind(this);
      this.toggle_display_detection_limit_selector = this.toggle_display_detection_limit_selector.bind(this);
      this.show_alert = this.show_alert.bind(this);
      /* ASYNC DATA LOADERS */
      this.load_available_instruments = this.load_available_instruments.bind(this);
      this.load_instrument_methods = this.load_instrument_methods.bind(this);
      this.load_method_calculation = this.load_method_calculation.bind(this);
      this.load_calculation = this.load_calculation.bind(this);
      this.load_manual_interims = this.load_manual_interims.bind(this);
      this.load_object_by_uid = this.load_object_by_uid.bind(this);
      /* HELPERS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_url = this.get_url.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.is_uid = this.is_uid.bind(this);
      this.add_select_option = this.add_select_option.bind(this);
      this.parse_select_options = this.parse_select_options.bind(this);
      this.parse_select_option = this.parse_select_option.bind(this);
      this.select_options = this.select_options.bind(this);
      this.toggle_checkbox = this.toggle_checkbox.bind(this);
      /* EVENT HANDLER */
      this.on_manual_entry_of_results_change = this.on_manual_entry_of_results_change.bind(this);
      this.on_methods_change = this.on_methods_change.bind(this);
      this.on_instrument_assignment_allowed_change = this.on_instrument_assignment_allowed_change.bind(this);
      this.on_instruments_change = this.on_instruments_change.bind(this);
      this.on_default_instrument_change = this.on_default_instrument_change.bind(this);
      this.on_default_method_change = this.on_default_method_change.bind(this);
      this.on_use_default_calculation_change = this.on_use_default_calculation_change.bind(this);
      this.on_calculation_change = this.on_calculation_change.bind(this);
      this.on_display_detection_limit_selector_change = this.on_display_detection_limit_selector_change.bind(this);
      this.on_separate_container_change = this.on_separate_container_change.bind(this);
      this.on_default_preservation_change = this.on_default_preservation_change.bind(this);
      this.on_default_container_change = this.on_default_container_change.bind(this);
      this.on_partition_sampletype_change = this.on_partition_sampletype_change.bind(this);
      this.on_partition_separate_container_change = this.on_partition_separate_container_change.bind(this);
      this.on_partition_container_change = this.on_partition_container_change.bind(this);
      this.on_partition_required_volume_change = this.on_partition_required_volume_change.bind(this);
    }

    load() {
      var d1, d2;
      console.debug("AnalysisServiceEditView::load");
      // load translations
      jarn.i18n.loadCatalog("bika");
      this._ = window.jarn.i18n.MessageFactory("bika");
      // All available instruments by UID
      this.all_instruments = {};
      // All invalid instruments by UID
      this.invalid_instruments = {};
      // Load available instruments
      d1 = this.load_available_instruments().done(function(instruments) {
        var me;
        me = this;
        return $.each(instruments, function(index, instrument) {
          var uid;
          uid = instrument.UID;
          // remember the instrument
          me.all_instruments[uid] = instrument;
          if (instrument.Valid !== "1") {
            // remember invalid instrument
            return me.invalid_instruments[uid] = instrument;
          }
        });
      });
      // Interim values defined by the user (not part of the current calculation)
      this.manual_interims = [];
      // Calculate manual set interims
      d2 = this.load_manual_interims().done(function(manual_interims) {
        return this.manual_interims = manual_interims;
      });
      // UIDs of the initial selected methods
      this.selected_methods = this.get_methods();
      // UIDs of the initial selected instruments
      this.selected_instruments = this.get_instruments();
      // UID of the initial selected calculation
      this.selected_calculation = this.get_calculation();
      // UID of the initial selected default instrument
      this.selected_default_instrument = this.get_default_instrument();
      // UID of the initial selected default method
      this.selected_default_method = this.get_default_method();
      // Array of UID/Title objects of the initial options from the methods field
      this.methods = this.parse_select_options($("#archetypes-fieldname-Methods #Methods"));
      // Array of UID/Title objects of the initial options from the instrument field
      this.instruments = this.parse_select_options($("#archetypes-fieldname-Instruments #Instruments"));
      // Array of UID/Title objects of the initial options from the calculations field
      this.calculations = this.parse_select_options($("#archetypes-fieldname-Calculation #Calculation"));
      // bind the event handler to the elements
      this.bind_eventhandler();
      // initialize the form when all data is loaded
      $.when(d1, d2).then(this.init);
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
      $("body").on("change", "#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector", this.on_display_detection_limit_selector_change);
      /* CONTAINER AND PRESERVATION TAB */
      // The "Separate Container" checkbox changed
      $("body").on("change", "#archetypes-fieldname-Separate #Separate", this.on_separate_container_change);
      // The "Default Preservation" select changed
      $("body").on("change", "#archetypes-fieldname-Preservation #Preservation", this.on_default_preservation_change);
      // The "Default Container" select changed
      $("body").on("selected", "#archetypes-fieldname-Container #Container", this.on_default_container_change);
      // The "Sample Type" select changed in the Partition setup
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.sampletype']", this.on_partition_sampletype_change);
      // The "Separate Container" checkbox changed in the Partition setup
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.separate']", this.on_partition_separate_container_change);
      // The "Container" checkbox changed in the Partition setup
      $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.container']", this.on_partition_container_change);
      // The "Required Volume" value changed in the Partition setup
      return $("body").on("change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.vol']", this.on_partition_required_volume_change);
    }

    init() {
      /**
       * Initialize Form
       */
      // Set "Instrument assignment is not required" checkbox
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("--> Manual Entry of Results is allowed");
        // restore all initial set methods in the method multi-select
        this.set_methods(this.methods);
      } else {
        console.debug("--> Manual Entry of Results is **not** allowed");
        // flush all methods and add only the "None" option
        this.set_methods(null);
      }
      // Set "Instrument assignment is allowed" checkbox
      if (this.is_instrument_assignment_allowed()) {
        console.debug("--> Instrument assignment is allowed");
        // restore all initial set instruments
        this.set_instruments(this.instruments);
      } else {
        console.debug("--> Instrument assignment is **not** allowed");
        // flush all instruments and add only the "None" option
        this.set_instruments(null);
      }
      // Set "Use the Default Calculation of Method" checkbox
      if (this.use_default_calculation_of_method()) {
        console.debug("--> Use default calculation of method");
      } else {
        console.debug("--> Use default calculation of instrument");
      }
      // Set "Display a Detection Limit selector" checkbox
      if (this.display_detection_limit_selector()) {
        console.debug("--> Allow detection limit selector");
        return this.toggle_display_detection_limit_selector(true);
      } else {
        console.debug("--> Disallow detection limit selector");
        return this.toggle_display_detection_limit_selector(false);
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

    toggle_manual_entry_of_results_allowed(toggle, silent = true) {
      /**
       * Toggle the "Instrument assignment is not required" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults");
      return this.toggle_checkbox(field, toggle, silent);
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
       *
       * @param {boolean} flush
       *    True to empty all instruments first
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
        this.add_select_option(field, null);
      } else {
        me = this;
        $.each(methods, function(index, method) {
          var title, uid;
          // ensure only "methods with allow manual entry"
          if (method.ManualEntryOfResults === false) {
            return;
          }
          title = method.title || method.Title;
          uid = method.uid || method.UID;
          return me.add_select_option(field, title, uid);
        });
      }
      // restore initial selection
      return this.select_methods(this.selected_methods);
    }

    select_methods(uids) {
      var field, me;
      /**
       * Select methods by UID
       *
       * @param {Array} uids
       *    UIDs of Methods to select
       */
      if (!this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual entry of results is not allowed");
        return;
      }
      field = $("#archetypes-fieldname-Methods #Methods");
      // set selected attribute to the options
      this.select_options(field, uids);
      // Set selected value to the default method select box
      me = this;
      $.each(uids, function(index, uid) {
        var flush, method, option;
        // flush the field for the first element
        flush = index === 0 && true || false;
        // extract the title and uid from the option element
        option = field.find(`option[value=${uid}]`);
        method = {
          uid: option.val(),
          title: option.text()
        };
        // append option to the default method select box
        return me.set_default_method(method, flush = flush);
      });
      // restore initial selected default method
      this.select_default_method(this.selected_default_method);
      if (this.use_default_calculation_of_method()) {
        // set the calculation of the default method
        return this.set_method_calculation(this.get_default_method());
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

    toggle_instrument_assignment_allowed(toggle, silent = true) {
      /**
       * Toggle the "Instrument assignment is allowed" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      return this.toggle_checkbox(field, toggle, silent);
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
       *
       * @param {boolean} flush
       *    True to empty all instruments first
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
        this.add_select_option(field, null);
      } else {
        // set the instruments
        me = this;
        $.each(instruments, function(index, instrument) {
          var title, uid;
          uid = instrument.uid || instrument.UID;
          title = instrument.title || instrument.Title;
          return me.add_select_option(field, title, uid);
        });
      }
      // restore initial selection
      return this.select_instruments(this.selected_instruments);
    }

    select_instruments(uids) {
      var field, invalid_instruments, me, notification, title;
      /**
       * Select instruments by UID
       *
       * @param {Array} uids
       *    UIDs of Instruments to select
       */
      if (!this.is_instrument_assignment_allowed()) {
        console.debug("Instrument assignment not allowed");
        this.set_default_instrument(null);
        return;
      }
      field = $("#archetypes-fieldname-Instruments #Instruments");
      // set selected attribute to the options
      this.select_options(field, uids);
      invalid_instruments = [];
      // Set selected instruments to the list of the default instruments
      me = this;
      $.each(uids, function(index, uid) {
        var flush, instrument;
        flush = index === 0 && true || false;
        // get the instrument
        instrument = me.all_instruments[uid];
        if (uid in me.invalid_instruments) {
          console.warn(`Instrument '${instrument.Title}' is invalid`);
          invalid_instruments.push(instrument);
        }
        return me.set_default_instrument(instrument, flush = flush);
      });
      // show invalid instruments
      if (invalid_instruments.length > 0) {
        notification = $("<dl/>");
        $.each(invalid_instruments, function(index, instrument) {
          return notification.append(`<dd>⚠ ${instrument.Title}</dd>`);
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
      // restore initially selected default instrument
      this.select_default_instrument(this.selected_default_instrument);
      // set the instrument methods of the default instrument
      return this.set_instrument_methods(this.get_default_instrument());
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

    select_default_method(uid) {
      /**
       * Select method by UID
       *
       * @param {string} uid
       *    UID of Method to select
       */
      var field;
      field = $("#archetypes-fieldname-Method #Method");
      return this.select_options(field, [uid]);
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
      title = instrument.title || instrument.Title;
      uid = instrument.uid || instrument.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    }

    select_default_instrument(uid) {
      /**
       * Select instrument by UID
       *
       * @param {string} uid
       *    UID of Instrument to select
       */
      var field;
      field = $("#archetypes-fieldname-Instrument #Instrument");
      return this.select_options(field, [uid]);
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

    toggle_use_default_calculation_of_method(toggle, silent = true) {
      /**
       * Toggle the "Use the Default Calculation of Method" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return this.toggle_checkbox(field, toggle, silent);
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

    select_calculation(uid) {
      /**
       * Select calculation by UID
       *
       * @param {string} uid
       *    UID of Calculation to select
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      this.select_options(field, [uid]);
      // load the calculation now, to set the interims
      return this.load_calculation(uid).done(function(calculation) {
        return this.set_interims(calculation.InterimFields);
      });
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
      var field, interim_keys, more_button;
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
      // extract the keys of the calculation interims
      interim_keys = interims.map(function(v) {
        return v.keyword;
      });
      // always keep manual set interims
      $.each(this.manual_interims, function(index, interim) {
        var i;
        // the keyword of the manual interim is in the keys of the calculation
        // interims -> overwrite calculation interim with the manual interim
        i = interim_keys.indexOf(interim.keyword);
        if (i >= 0) {
          return interims[i] = interim;
        } else {
          // append the manual interim at the end
          return interims.push(interim);
        }
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
       * Loads the methods of the instrument
       *
       * @param {string} instrument_uid
       *    The UID of the instrument to set the method from
       */
      var me;
      me = this;
      // Leave default method if the "None" instrument was selected
      if (!this.is_uid(instrument_uid)) {
        return;
      }
      return this.load_instrument_methods(instrument_uid).done(function(methods) {
        methods = $.extend([], methods);
        // Extend the default methods with the instrument methods
        $.each(methods, function(index, method) {
          flush = index === 0 ? true : false;
          return me.set_default_method(method, flush = flush);
        });
        // restore the initially selected method
        this.select_default_method(this.selected_default_method);
        // set the calculation of the method
        if (this.use_default_calculation_of_method()) {
          return this.set_method_calculation(this.get_default_method());
        }
      });
    }

    display_detection_limit_selector() {
      /**
       * Get the value of the checkbox "Display a Detection Limit selector"
       *
       * @returns {boolean} True if detection limit selector should be displayed
       */
      var field;
      field = $("#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector");
      return field.is(":checked");
    }

    toggle_display_detection_limit_selector(toggle, silent = true) {
      /**
       * Toggle the "Display detection limit selector" checkbox
       *
       * If it is checked, display the "Allow manual detection limit input" field below
       * If it is unchecked, hide and uncheck the "Allow manual detection limit input" field below
       */
      var field, field2;
      field = $("#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector");
      // control the visiblity of the dependent field
      field2 = $("#archetypes-fieldname-AllowManualDetectionLimit #AllowManualDetectionLimit");
      if (toggle === true) {
        field2.parent().show();
      } else {
        field2.parent().hide();
        field2.prop("checked", false);
      }
      return this.toggle_checkbox(field, toggle, silent);
    }

    show_alert(options) {
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
      html = `<div class="alert alert-${level} errorbox" role="alert">\n  <h3>${title}</h3>\n  <div>${message}</div>\n</div>`;
      return alerts.append(html);
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
          portal_type: "Instrument"
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

    load_manual_interims() {
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
        // interims of this calculation
        calculation_interims = $.extend([], calculation.InterimFields);
        // extract the keys of the calculation interims
        calculation_interim_keys = calculation_interims.map(function(v) {
          return v.keyword;
        });
        // separate manual interims from calculation interims
        manual_interims = [];
        $.each(this.get_interims(), function(index, value) {
          var calculation_interim, i, ref;
          // manual interim is not part of the calculation interims
          if (ref = value.keyword, indexOf.call(calculation_interim_keys, ref) < 0) {
            return manual_interims.push(value);
          } else {
            // manual interim is also located in the calculaiton interims
            // -> check for interim override, e.g. different value, unit etc.

            // get the calculation interim
            i = calculation_interim_keys.indexOf(value.keyword);
            calculation_interim = calculation_interims[i];
            // check for different values
            return $.each(calculation_interim, function(k, v) {
              if (v !== value[k]) {
                manual_interims.push(value);
                // stop iteration
                return false;
              }
            });
          }
        });
        return deferred.resolveWith(this, [manual_interims]);
      });
      return deferred.promise();
    }

    load_object_by_uid(uid) {
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
        // Resolve the deferred with the parsed calculation
        return deferred.resolveWith(this, [object]);
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

    get_url() {
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
      return `${protocol}//${host}${pathname}`;
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
      if (value) {
        option = `<option value='${value}'>${this._(name)}</option>`;
      } else {
        // empty option (selected by default)
        option = `<option selected='selected' value=''>${this._("None")}</option>`;
      }
      return $(select).append(option);
    }

    parse_select_options(select) {
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
    }

    parse_select_option(select, value) {
      /**
       * Return the option by value
       */
      var data, option;
      option = field.find(`option[value=${uid}]`);
      data = {
        uid: option.val() || "",
        title: option.text() || ""
      };
      return data;
    }

    select_options(select, values) {
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
    }

    toggle_checkbox(checkbox, toggle, silent = true) {
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
      var field;
      field = $(checkbox);
      if (toggle === void 0) {
        toggle = !field.is(":checked");
      }
      field.prop("checked", toggle);
      // trigger change event
      if (!silent) {
        return field.trigger("change");
      }
    }

    on_manual_entry_of_results_change(event) {
      /**
       * Eventhandler when the "Instrument assignment is not required" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°");
      // Results can be set by "hand"
      if (this.is_manual_entry_of_results_allowed()) {
        console.debug("Manual entry of results is allowed");
        // restore all initial set methods
        return this.set_methods(this.methods);
      } else {
        // Results can be only set by an instrument
        console.debug("Manual entry of results is **not** allowed");
        // flush all methods and add only the "None" option
        return this.set_methods(null);
      }
    }

    on_methods_change(event) {
      var method_uids;
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
      // Select the methods
      return this.select_methods(method_uids);
    }

    on_instrument_assignment_allowed_change(event) {
      /**
       * Eventhandler when the "Instrument assignment is allowed" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°");
      if (this.is_instrument_assignment_allowed()) {
        console.debug("Instrument assignment is allowed");
        // restore the instruments multi-select to the initial value
        return this.set_instruments(this.instruments);
      } else {
        console.debug("Instrument assignment is **not** allowed");
        return this.set_instruments(null);
      }
    }

    on_instruments_change(event) {
      var instrument_uids;
      /**
       * Eventhandler when the "Instruments" multiselect changed
       */
      console.debug("°°° AnalysisServiceEditView::on_instruments_change °°°");
      // selected instrument UIDs
      instrument_uids = this.get_instruments();
      if (instrument_uids.length === 0) {
        console.warn("All instruments deselected");
      }
      // Select the instruments
      return this.select_instruments(instrument_uids);
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
      /**
       * Eventhandler when the "Default Method" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_default_method_change °°°");
      // Load the calculation of the method if the checkbox "Use the Default
      // Calculation of Method" is checked
      if (this.use_default_calculation_of_method()) {
        // set the calculation of the method
        return this.set_method_calculation(this.get_default_method());
      }
    }

    on_use_default_calculation_change(event) {
      var me;
      /**
       * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_use_default_calculation_change °°°");
      // "Use the Default Calculation of Method" checkbox checked
      if (this.use_default_calculation_of_method()) {
        console.debug("Use default calculation");
        // set the calculation of the method
        return this.set_method_calculation(this.get_default_method());
      } else {
        // restore all initial set calculations
        me = this;
        $.each(this.calculations, function(index, calculation) {
          var flush;
          flush = index === 0 ? true : false;
          return me.set_calculation(calculation, flush = flush);
        });
        // select initial set calculation
        return this.select_calculation(this.selected_calculation);
      }
    }

    on_calculation_change(event) {
      /**
       * Eventhandler when the "Calculation" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_calculation_change °°°");
      return this.select_calculation(this.get_calculation());
    }

    on_display_detection_limit_selector_change(event) {
      /**
       * Eventhandler when the "Display a Detection Limit selector" checkbox changed
       *
       * This checkbox is located on the "Analysis" Tab
       */
      console.debug("°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°");
      if (this.display_detection_limit_selector()) {
        console.debug("Allow detection limit selector");
        return this.toggle_display_detection_limit_selector(true);
      } else {
        console.debug("Disallow detection limit selector");
        return this.toggle_display_detection_limit_selector(false);
      }
    }

    on_separate_container_change(event) {
      var value;
      /**
       * Eventhandler when the "Separate Container" checkbox changed
       *
       * This checkbox is located on the "Container and Preservation" Tab
       */
      console.debug("°°° AnalysisServiceEditView::on_separate_container_change °°°");
      return value = event.currentTarget.checked;
    }

    on_default_preservation_change(event) {
      /**
       * Eventhandler when the "Default Preservation" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_default_preservation_change °°°");
    }

    on_default_container_change(event) {
      var el, field, uid;
      /**
       * Eventhandler when the "Default Container" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
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
    }

    on_partition_sampletype_change(event) {
      var el, uid;
      /**
       * Eventhandler when the "Sample Type" selection changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      console.debug("°°° AnalysisServiceEditView::on_partition_sampletype_change °°°");
      el = event.currentTarget;
      uid = el.value;
      return this.load_object_by_uid(uid).done(function(sampletype) {
        var minvol;
        minvol = sampletype.MinimumVolume || "";
        // set the minimum volume to the partition
        return $(el).parents("tr").find("[name^='PartitionSetup.vol']").val(minvol);
      });
    }

    on_partition_separate_container_change(event) {
      /**
       * Eventhandler when the "Separate Container" checkbox changed
       *
       * This checkbox is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_partition_separate_container_change °°°");
    }

    on_partition_container_change(event) {
      var el, field, uid;
      /**
       * Eventhandler when the "Container" multi-select changed
       *
       * This multi select is located on the "Container and Preservation" Tab
       */
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
    }

    on_partition_required_volume_change(event) {
      /**
       * Eventhandler when the "Required Volume" value changed
       *
       * This field is located on the "Container and Preservation" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_partition_required_volume_change °°°");
    }

  };

}).call(this);
