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
      this.init_default_calculation = this.init_default_calculation.bind(this);
      /* INTERIM FIELD HANDLING */
      this.get_interims = this.get_interims.bind(this);
      this.set_interims = this.set_interims.bind(this);
      this.flush_interims = this.flush_interims.bind(this);
      /* LOADERS */
      this.load_interims = this.load_interims.bind(this);
      this.load_instrument_methods = this.load_instrument_methods.bind(this);
      this.load_available_calculations = this.load_available_calculations.bind(this);
      this.load_method_calculation = this.load_method_calculation.bind(this);
      /* METHODS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.is_uid = this.is_uid.bind(this);
      this.toggle_visibility_methods_field = this.toggle_visibility_methods_field.bind(this);
      this.toggle_instrument_entry_of_results_checkbox = this.toggle_instrument_entry_of_results_checkbox.bind(this);
      this.add_select_option = this.add_select_option.bind(this);
      /* ELEMENT HANDLING */
      this.use_default_calculation_of_method = this.use_default_calculation_of_method.bind(this);
      this.get_default_calculation = this.get_default_calculation.bind(this);
      /* EVENT HANDLER */
      this.on_default_method_change = this.on_default_method_change.bind(this);
      this.on_methods_change = this.on_methods_change.bind(this);
      this.on_instruments_change = this.on_instruments_change.bind(this);
      this.on_default_instrument_change = this.on_default_instrument_change.bind(this);
      this.on_instrument_assignment_allowed_change = this.on_instrument_assignment_allowed_change.bind(this);
      this.on_manual_entry_of_results_change = this.on_manual_entry_of_results_change.bind(this);
      this.on_use_default_calculation_change = this.on_use_default_calculation_change.bind(this);
      this.on_calculation_change = this.on_calculation_change.bind(this);
      this.on_display_detection_limit_selector_change = this.on_display_detection_limit_selector_change.bind(this);
    }

    load() {
      console.debug("AnalysisServiceEditView::load");
      // load translations
      jarn.i18n.loadCatalog("bika");
      this._ = window.jarn.i18n.MessageFactory("bika");
      // JSONAPI v1 access
      this.read = window.bika.lims.jsonapi_read;
      // Interim values defined in default Calculation
      this.calculation_interims = [];
      // Interim values defined by the user (not part of a calculation)
      this.manual_interims = [];
      // bind the event handler to the elements
      this.bind_eventhandler();
      // Initialize default calculation
      this.init_default_calculation();
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
      // The "Default Method" select changed
      $("body").on("change", "#archetypes-fieldname-Method #Method", this.on_default_method_change);
      // The "Methods" multiselect changed
      $("body").on("change", "#archetypes-fieldname-Methods #Methods", this.on_methods_change);
      // The "Default Instrument" selector changed
      $("body").on("change", "#archetypes-fieldname-Instrument #Instrument", this.on_default_instrument_change);
      // The "Instruments" multiselect changed
      $("body").on("change", "#archetypes-fieldname-Instruments #Instruments", this.on_instruments_change);
      // The "Instrument assignment is allowed" checkbox changed
      $("body").on("change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", this.on_instrument_assignment_allowed_change);
      // The "Instrument assignment is not required" checkbox changed
      $("body").on("change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", this.on_manual_entry_of_results_change);
      // The "Use the Default Calculation of Method" checkbox changed
      $("body").on("change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", this.on_use_default_calculation_change);
      // The "Calculation" selector changed
      $("body").on("change", "#archetypes-fieldname-Calculation #Calculation", this.on_calculation_change);
      /* ANALYSIS TAB */
      // The "Display a Detection Limit selector" checkbox changed
      return $("body").on("change", "#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector", this.on_display_detection_limit_selector_change);
    }

    init_default_calculation() {
      /*
       * 1. Check if field "Use the Default Calculation of Method" is checked
       * 2. Fetch the selected calculation
       * 3. Replace the calculation select box with the calculations
       */
      var calculation_uid, me, options;
      me = this;
      calculation_uid = this.get_default_calculation();
      // nothing to do if we do not have a calculation uid set
      if (!this.is_uid(calculation_uid)) {
        return;
      }
      options = {
        catalog_name: "bika_setup_catalog",
        UID: calculation_uid
      };
      return this.read(options, function(data) {
        var calculation, calculation_interim_keys, calculation_interims, field, manual_interims;
        if (data.objects.length !== 1) {
          console.warn(`No Calculation found for UID '${calculation_uid}'`);
          return;
        }
        // Calculation data
        calculation = data.objects[0];
        // limit the calculation select box to this calculation
        field = $("#archetypes-fieldname-Calculation #Calculation");
        field.empty();
        me.add_select_option(field, calculation.Title, calculation.UID);
        // process interims of this calculation
        calculation_interims = [];
        $.each(calculation.InterimFields, function(index, value) {
          // we use the same format as expected by `set_interims`
          return calculation_interims.push([
            value.keyword,
            value.title,
            value.value,
            value.unit,
            false, // Hidden (missing here)
            false // Apply wide (missing here)
          ]);
        });
        // remember the interims of this calculation
        me.calculation_interims = calculation_interims;
        // Calculate which interims were manually set (not part of the calculation)
        manual_interims = [];
        calculation_interim_keys = calculation_interims.map(function(v) {
          return v[0];
        });
        $.each(me.get_interims(), function(index, value) {
          var ref;
          if (ref = value[0], indexOf.call(calculation_interim_keys, ref) < 0) {
            return manual_interims.push(value);
          }
        });
        // remember the manual set interims of this AS
        return me.manual_interims = manual_interims;
      });
    }

    get_interims() {
      /*
       * Extract the interim field values as a list of lists
       * [['MG', 'Magnesium', 'g' ...], [], ...]
       */
      var field, interims, rows;
      field = $("#archetypes-fieldname-InterimFields");
      rows = field.find("tr.records_row_InterimFields");
      interims = [];
      $.each(rows, function(index, row) {
        var values;
        values = [];
        $.each($(row).find("td input"), function(index, input) {
          var value;
          value = input.value;
          if (input.type === "checkbox") {
            value = input.checked;
          }
          return values.push(value);
        });
        // Only rows with Keyword set
        if (values && values[0] !== "") {
          return interims.push(values);
        }
      });
      return interims;
    }

    set_interims(values) {
      var field, more_button;
      /*
       * Set the interim field values
       * Note: This method takes the same input format as returned from get_interims
       */
      // empty all interims
      this.flush_interims();
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      return $.each(values, function(index, value) {
        var inputs, last_row;
        last_row = field.find("tr.records_row_InterimFields").last();
        more_button.click();
        inputs = last_row.find("input");
        return $.each(value, function(i, v) {
          var input;
          input = inputs[i];
          if (input.type === "checkbox") {
            return input.checked = v;
          } else {
            return input.value = v;
          }
        });
      });
    }

    flush_interims() {
      /*
       * Flush interim field
       */
      var field, more_button, rows;
      field = $("#archetypes-fieldname-InterimFields");
      more_button = field.find("#InterimFields_more");
      more_button.click();
      rows = field.find("tr.records_row_InterimFields");
      return rows.not(":last").remove();
    }

    load_interims(calculation_uid) {
      var options;
      /*
       * Load interims assigned to the calculation
       */
      if (!this.is_uid(calculation_uid)) {
        console.warn(`Calculation UID '${calculation_uid}' is invalid`);
        return;
      }
      options = {
        catalog_name: "bika_setup_catalog",
        UID: calculation_uid
      };
      return window.bika.lims.jsonapi_read(options, function(data) {
        var interims, ref;
        return interims = data != null ? (ref = data.objects) != null ? ref[0].InterimFields : void 0 : void 0;
      });
    }

    load_instrument_methods(instrument_uid) {
      var field, options;
      /*
       * Load methods assigned to the instrument
       */
      if (!this.is_uid(instrument_uid)) {
        console.warn(`Instrument UID '${instrument_uid}' is invalid`);
        return;
      }
      field = $('#archetypes-fieldname-Method #Method');
      field.empty();
      options = {
        url: this.get_portal_url() + "/get_instrument_methods",
        data: {
          uid: instrument_uid
        }
      };
      return this.ajax_submit(options).done(function(data) {
        $.each(data.methods, function(index, item) {
          var option;
          option = `<option value='${item.uid}'>${item.title}</option>`;
          return field.append(option);
        });
        if (field.length === 0) {
          console.warn(`Instrument with UID '${instrument_uid}' has no methods assigned`);
          return this.add_select_option(field, "");
        }
      });
    }

    load_available_calculations() {
      /*
       * Load all available calculations to the calculation select box
       */
      var field, options;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      field.empty();
      options = {
        url: this.get_portal_url() + "/get_available_calculations"
      };
      return this.ajax_submit(options).done(function(data) {
        $.each(data, function(index, item) {
          var option;
          option = `<option value='${item.uid}'>${item.title}</option>`;
          return field.append(option);
        });
        if (field.length === 0) {
          return this.add_select_option(field, "");
        }
      });
    }

    load_method_calculation(method_uid) {
      var field, options;
      /*
       * Load calculations for the given method UID
       */
      if (!this.is_uid(method_uid)) {
        console.warn(`Method UID '${method_uid}' is invalid`);
        return;
      }
      field = $("#archetypes-fieldname-Calculation #Calculation");
      field.empty();
      options = {
        url: this.get_portal_url() + "/get_method_calculation",
        data: {
          uid: method_uid
        }
      };
      // Fetch the assigned calculations of the method
      return this.ajax_submit(options).done(function(data) {
        var option;
        if (!$.isEmptyObject(data)) {
          option = `<option value='${data.uid}'>${data.title}</option>`;
          return field.append(option);
        } else {
          return this.add_select_option(field, "");
        }
      });
    }

    ajax_submit(options) {
      var base, done;
      /*
       * Ajax Submit with automatic event triggering and some sane defaults
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
      done = () => {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
    }

    get_portal_url() {
      /*
       * Return the portal url
       */
      return window.portal_url;
    }

    is_uid(str) {
      var match;
      /*
       * Validate valid URL
       */
      if (typeof str !== "string") {
        return false;
      }
      match = str.match(/[a-z0-9]{32}/);
      return match !== null;
    }

    toggle_visibility_methods_field(toggle) {
      /*
       * This method toggles the visibility of the "Methods" field
       */
      var field;
      field = $("#archetypes-fieldname-Methods");
      if (toggle === void 0) {
        field.fadeToggle("fast");
      } else if (toggle === true) {
        field.fadeIn("fast");
      } else {
        field.fadeOut("fast");
      }
      return field;
    }

    toggle_instrument_entry_of_results_checkbox(toggle) {
      /*
       * This method toggles the "Instrument assignment is allowed" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults");
      if (toggle === void 0) {
        toggle = !field.prop("checked");
      }
      field.prop("checked", toggle);
      return field;
    }

    add_select_option(select, name, value) {
      var option;
      /*
       * Adds an option to the select
       */
      // empty option
      if (value === "") {
        name = "None";
      }
      option = `<option value='${value}'>${this._(name)}</option>`;
      return $(select).append(option);
    }

    use_default_calculation_of_method() {
      /*
       * Retrun the value of the "Use the Default Calculation of Method" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return field.is(":checked");
    }

    get_default_calculation() {
      /*
       * Get the UID of the selected default calculation
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      return field.val();
    }

    on_default_method_change(event) {
      /*
       * Eventhandler when the "Default Method" selector changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_default_method_change °°°");
    }

    on_methods_change(event) {
      /*
       * Eventhandler when the "Methods" multiselect changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_methods_change °°°");
    }

    on_instruments_change(event) {
      /*
       * Eventhandler when the "Instruments" multiselect changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_instruments_change °°°");
    }

    on_default_instrument_change(event) {
      /*
       * Eventhandler when the "Default Instrument" selector changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_default_instrument_change °°°");
    }

    on_instrument_assignment_allowed_change(event) {
      /*
       * Eventhandler when the "Instrument assignment is allowed" checkbox changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°");
    }

    on_manual_entry_of_results_change(event) {
      /*
       * Eventhandler when the "Instrument assignment is not required" checkbox changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°");
    }

    on_use_default_calculation_change(event) {
      /*
       * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_use_default_calculation_change °°°");
    }

    on_calculation_change(event) {
      /*
       * Eventhandler when the "Calculation" selector changed
       */
      return console.debug("°°° AnalysisServiceEditView::on_calculation_change °°°");
    }

    on_display_detection_limit_selector_change(event) {
      /*
       * Eventhandler when the "Display a Detection Limit selector" checkbox changed
       *
       * This checkbox is located on the "Analysis" Tab
       */
      return console.debug("°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°");
    }

  };

}).call(this);
