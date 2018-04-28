(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
  */
  window.AnalysisServiceEditView = class AnalysisServiceEditView {
    constructor() {
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      /* LOADERS */
      this.load_instrument_methods = this.load_instrument_methods.bind(this);
      this.load_available_calculations = this.load_available_calculations.bind(this);
      this.load_method_calculation = this.load_method_calculation.bind(this);
      /* METHODS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_url = this.get_url.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.get_authenticator = this.get_authenticator.bind(this);
      this.is_uid = this.is_uid.bind(this);
      this.show_methods_field = this.show_methods_field.bind(this);
      this.toggle_instrument_entry_of_results_checkbox = this.toggle_instrument_entry_of_results_checkbox.bind(this);
      this.add_empty_option = this.add_empty_option.bind(this);
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
      jarn.i18n.loadCatalog('bika');
      this._ = window.jarn.i18n.MessageFactory('bika');
      // bind the event handler to the elements
      this.bind_eventhandler();
      // Develpp only
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
        url: this.get_url() + "/get_instrument_methods",
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
          return this.add_empty_option(field);
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
        url: this.get_url() + "/get_available_calculations"
      };
      return this.ajax_submit(options).done(function(data) {
        $.each(data, function(index, item) {
          var option;
          option = `<option value='${item.uid}'>${item.title}</option>`;
          return field.append(option);
        });
        if (field.length === 0) {
          return this.add_empty_option(field);
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
        url: this.get_url() + "/get_method_calculation",
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
          return this.add_empty_option(field);
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
        options.url = this.get_url();
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
        base._authenticator = this.get_authenticator();
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = () => {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
    }

    get_url() {
      /*
       * Return the current URL
       */
      var host, pathname, protocol;
      protocol = location.protocol;
      host = location.host;
      pathname = location.pathname;
      return `${protocol}//${host}${pathname}`;
    }

    get_portal_url() {
      /*
       * Return the portal url
       */
      return window.portal_url;
    }

    get_authenticator() {
      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
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

    show_methods_field(toggle) {
      /*
       * This method toggles the visibility of complete "Methods" field
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

    add_empty_option(select) {
      /*
       * Add an empty option to the select box
       */
      var empty_option;
      empty_option = `<option value=''>${this._('None')}</option>`;
      $(select).append(empty_option);
      return $(select).val("");
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
