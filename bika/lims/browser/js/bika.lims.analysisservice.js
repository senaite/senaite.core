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
      /* FIELD GETTERS/SETTERS */
      this.get_calculation = this.get_calculation.bind(this);
      this.set_calculation = this.set_calculation.bind(this);
      this.get_interims = this.get_interims.bind(this);
      this.set_interims = this.set_interims.bind(this);
      this.flush_interims = this.flush_interims.bind(this);
      /* ASYNC DATA LOADERS */
      this.load_available_calculations = this.load_available_calculations.bind(this);
      this.load_instrument_methods = this.load_instrument_methods.bind(this);
      this.load_method_calculation = this.load_method_calculation.bind(this);
      this.load_calculation = this.load_calculation.bind(this);
      /* HELPERS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.is_uid = this.is_uid.bind(this);
      /* ELEMENT HANDLING */
      this.use_default_calculation_of_method = this.use_default_calculation_of_method.bind(this);
      this.get_default_method = this.get_default_method.bind(this);
      this.toggle_visibility_methods_field = this.toggle_visibility_methods_field.bind(this);
      this.toggle_instrument_entry_of_results_checkbox = this.toggle_instrument_entry_of_results_checkbox.bind(this);
      this.add_select_option = this.add_select_option.bind(this);
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
      // Interim values defined by the user (not part of a calculation)
      this.manual_interims = [];
      // bind the event handler to the elements
      this.bind_eventhandler();
      // Initialize default calculation
      this.init_interims();
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

    init_interims() {
      /*
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
        calculation_interims = calculation.InterimFields || [];
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

    get_calculation() {
      /*
       * Get the UID of the selected default calculation
       */
      var field;
      field = $("#archetypes-fieldname-Calculation #Calculation");
      return field.val();
    }

    set_calculation(calculation, flush = true) {
      var field, title, uid;
      /*
       * Set the calculation field with the given ()JSON calculation data
       */
      // create a copy of the calculation
      calculation = $.extend({}, calculation);
      field = $("#archetypes-fieldname-Calculation #Calculation");
      // empty the field first
      if (flush) {
        field.empty();
      }
      // XXX: Workaround for inconsistent data structures of the JSON API v1 and the
      //      return value of `get_method_calculation`
      title = calculation.title || calculation.Title;
      uid = calculation.uid || calculation.UID;
      if (title && uid) {
        return this.add_select_option(field, title, uid);
      } else {
        return this.add_select_option(field, null);
      }
    }

    get_interims() {
      /*
       * Extract the interim field values as a list of objects
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
      /*
       * Set the interim field values
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

    load_available_calculations() {
      /*
       * Load all available calculations to the calculation select box
       */
      var options;
      options = {
        url: this.get_portal_url() + "/get_available_calculations"
      };
      return this.ajax_submit(options);
    }

    load_instrument_methods(instrument_uid) {
      var field, options;
      /*
       * Load assigned methods of the instrument
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
          return this.add_select_option(field, null);
        }
      });
    }

    load_method_calculation(method_uid) {
      /*
       * Load assigned calculation of the given method UID
       * Returns a deferred
       */
      var deferred, me, options;
      me = this;
      deferred = $.Deferred();
      // Immediately if we do not have a valid method UID
      if (!this.is_uid(method_uid)) {
        console.warn(`Method UID '${method_uid}' is invalid`);
        deferred.resolveWith(me, [{}]);
        return deferred.promise();
      }
      options = {
        url: this.get_portal_url() + "/get_method_calculation",
        data: {
          uid: method_uid
        }
      };
      // Fetch the assigned calculations of the method
      this.ajax_submit(options).done(function(data) {
        return deferred.resolveWith(me, [data]);
      });
      return deferred.promise();
    }

    load_calculation(calculation_uid) {
      /*
       * Load calculation object for the given UID
       * Returns a deferred
       */
      var deferred, me, options;
      me = this;
      deferred = $.Deferred();
      // Immediately if we do not have a valid calculation UID
      if (!this.is_uid(calculation_uid)) {
        console.warn(`Calculation UID '${calculation_uid}' is invalid`);
        deferred.resolveWith(me, [{}]);
        return deferred.promise();
      }
      // Load the calculation, so that we can set the interims
      options = {
        catalog_name: "bika_setup_catalog",
        UID: calculation_uid
      };
      this.read(options, function(data) {
        var calculation;
        calculation = {};
        if (data.objects.length === 1) {
          calculation = data.objects[0];
        }
        return deferred.resolveWith(me, [calculation]);
      });
      return deferred.promise();
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

    use_default_calculation_of_method() {
      /*
       * Retrun the value of the "Use the Default Calculation of Method" checkbox
       */
      var field;
      field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation");
      return field.is(":checked");
    }

    get_default_method() {
      /*
       * Get the UID of the selected default method
       */
      var field;
      field = $("#archetypes-fieldname-Method #Method");
      return field.val();
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
      if (!value) {
        name = "None";
      }
      option = `<option value='${value}'>${this._(name)}</option>`;
      return $(select).append(option);
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
      var method_uid;
      /*
       * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
       */
      console.debug("°°° AnalysisServiceEditView::on_use_default_calculation_change °°°");
      // "Use the Default Calculation of Method" checkbox checked
      if (event.currentTarget.checked) {
        // - get the UID of the default method
        // - set the assigned calculation of the method
        // - unselect all previous calculation interims (just keep the manual ones)
        // - set the interims of the new set calculation

        // Get the UID of the default Method
        method_uid = this.get_default_method();
        // Set empty calculation if method UID is not set
        if (!this.is_uid(method_uid)) {
          return this.set_calculation(null);
        }
        return this.load_method_calculation(method_uid).done(function(data) {
          // {uid: "488400e9f5e24a4cbd214056e6b5e2aa", title: "My Calculation"}
          this.set_calculation(data);
          // load the calculation now, to set the interims
          return this.load_calculation(this.get_calculation()).done(function(calculation) {
            return this.set_interims(calculation.InterimFields);
          });
        });
      } else {
        // load all available calculations
        return this.load_available_calculations().done(function(calculations) {
          var me;
          me = this;
          $.each(calculations, function(index, calculation) {
            var flush;
            flush = index === 0 ? true : false;
            return me.set_calculation(calculation, flush);
          });
          // flush interims
          return this.set_interims(null);
        });
      }
    }

    on_calculation_change(event) {
      /*
       * Eventhandler when the "Calculation" selector changed
       */
      console.debug("°°° AnalysisServiceEditView::on_calculation_change °°°");
      // load the calculation now, to set the interims
      return this.load_calculation(this.get_calculation()).done(function(calculation) {
        return this.set_interims(calculation.InterimFields);
      });
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
