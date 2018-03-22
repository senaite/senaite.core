(function() {
  /* Please use this command to compile this file into the parent `js` directory:
      coffee --no-header -w -o ../ -c bika.lims.worksheet.coffee
  */
  window.WorksheetFolderView = class WorksheetFolderView {
    constructor() {
      /*
      * Controller class for Worksheets Folder
       */
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      /* METHODS */
      this.get_template_instrument = this.get_template_instrument.bind(this);
      this.select_instrument = this.select_instrument.bind(this);
      /* EVENT HANDLER */
      this.on_template_change = this.on_template_change.bind(this);
      this.on_instrument_change = this.on_instrument_change.bind(this);
    }

    load() {
      console.debug("WorksheetFolderView::load");
      // bind the event handler to the elements
      return this.bind_eventhandler();
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetFolderView::bind_eventhandler");
      // Template changed
      $("body").on("change", "select.template", this.on_template_change);
      // Instrument changed
      return $("body").on("change", "select.instrument", this.on_instrument_change);
    }

    get_template_instrument() {
      var input, value;
      /*
       * TODO: Refactor to get the data directly from the server
       * Returns the JSON parsed value of the HTML element with the class
         `templateinstruments`
       */
      console.debug("WorksheetFolderView::get_template_instruments");
      input = $("input.templateinstruments");
      value = input.val();
      return $.parseJSON(value);
    }

    select_instrument(instrument_uid) {
      /*
       * Select instrument by UID
       */
      var option, select;
      select = $(".instrument");
      option = select.find(`option[value='${instrument_uid}']`);
      if (option) {
        return option.prop("selected", true);
      }
    }

    on_template_change(event) {
      var $el, instrument_uid, template_instrument, template_uid;
      /*
       * Eventhandler for template change
       */
      console.debug("°°° WorksheetFolderView::on_template_change °°°");
      // The select element for WS Template
      $el = $(event.currentTarget);
      // The option value is the worksheettemplate UID
      template_uid = $el.val();
      // Assigned instrument of this worksheet
      template_instrument = this.get_template_instrument();
      // The UID of the assigned instrument in the template
      instrument_uid = template_instrument[template_uid];
      // Select the instrument from the selection
      return this.select_instrument(instrument_uid);
    }

    on_instrument_change(event) {
      var $el, instrument_uid, message;
      /*
       * Eventhandler for instrument change
       */
      console.debug("°°° WorksheetFolderView::on_instrument_change °°°");
      // The select element for WS Instrument
      $el = $(event.currentTarget);
      // The option value is the nstrument UID
      instrument_uid = $el.val();
      if (instrument_uid) {
        message = _("Only the analyses for which the selected instrument is allowed will be added automatically.");
        // actually just a notification, but lacking a proper css class here
        return bika.lims.SiteView.notify_in_panel(message, "error");
      }
    }

  };

  window.WorksheetAddAnalysesView = class WorksheetAddAnalysesView {
    constructor() {
      /*
       * Controller class for Worksheet's add analyses view
       */
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      /* METHODS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_base_url = this.get_base_url.bind(this);
      this.get_authenticator = this.get_authenticator.bind(this);
      this.get_listing_form_id = this.get_listing_form_id.bind(this);
      this.get_listing_form = this.get_listing_form.bind(this);
      this.filter_service_selector_by_category_uid = this.filter_service_selector_by_category_uid.bind(this);
      /* EVENT HANDLER */
      this.on_category_change = this.on_category_change.bind(this);
      this.on_search_click = this.on_search_click.bind(this);
    }

    load() {
      console.debug("WorksheetAddanalysesview::load");
      // bind the event handler to the elements
      return this.bind_eventhandler();
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetAddanalysesview::bind_eventhandler");
      // Category filter changed
      $("body").on("change", "[name='list_FilterByCategory']", this.on_category_change);
      // Search button clicked
      return $("body").on("click", ".ws-analyses-search-button", this.on_search_click);
    }

    ajax_submit(options = {}) {
      var done;
      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
      // some sane option defaults
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_base_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = () => {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
    }

    get_base_url() {
      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    }

    get_authenticator() {
      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    }

    get_listing_form_id() {
      /*
       * Returns the CSS ID of the analyses listing
       */
      return "list";
    }

    get_listing_form() {
      /*
       * Returns the analyses listing form element
       */
      var form_id;
      form_id = this.get_listing_form_id();
      return $(`form[id='${form_id}']`);
    }

    filter_service_selector_by_category_uid(category_uid) {
      var $select, base_url, data, form_id, select_name, url;
      /*
       * Filters the service selector by category
       */
      console.debug(`WorksheetAddanalysesview::filter_service_selector_by_category_uid:${category_uid}`);
      form_id = this.get_listing_form_id();
      select_name = `${form_id}_FilterByService`;
      $select = $(`[name='${select_name}']`);
      base_url = this.get_base_url();
      url = base_url.replace("/add_analyses", "/getServices");
      data = {
        _authenticator: this.get_authenticator()
      };
      if (category_uid !== "any") {
        data["getCategoryUID"] = category_uid;
      }
      return this.ajax_submit({
        url: url,
        data: data,
        dataType: "json"
      }).done(function(data) {
        var any_option;
        $select.empty();
        any_option = `<option value='any'>${_('Any')}</option>`;
        $select.append(any_option);
        return $.each(data, function(index, item) {
          var name, option, uid;
          uid = item[0];
          name = item[1];
          option = `<option value='${uid}'>${name}</option>`;
          return $select.append(option);
        });
      });
    }

    on_category_change(event) {
      var $el, category_uid;
      /*
       * Eventhandler for category change
       */
      console.debug("°°° WorksheetAddanalysesview::on_category_change °°°");
      // The select element for WS Template
      $el = $(event.currentTarget);
      // extract the category UID and filter the services box
      category_uid = $el.val();
      return this.filter_service_selector_by_category_uid(category_uid);
    }

    on_search_click(event) {
      var filter_indexes, form, form_data, form_id;
      /*
       * Eventhandler for the search button
       */
      console.debug("°°° WorksheetAddanalysesview::on_search_click °°°");
      // Prevent form submit
      event.preventDefault();
      form = this.get_listing_form();
      form_id = this.get_listing_form_id();
      filter_indexes = ["FilterByCategory", "FilterByService", "FilterByClient"];
      // The filter elements (Category/Service/Client) belong to another form.
      // Therefore, we need to inject these values into the listing form as hidden
      // input fields.
      $.each(filter_indexes, function(index, filter) {
        var $el, input, name, value;
        name = `${form_id}_${filter}`;
        $el = $(`select[name='${name}']`);
        value = $el.val();
        // get the corresponding input element of the listing form
        input = $(`input[name='${name}']`, form);
        if (input.length === 0) {
          form.append(`<input name='${name}' value='${value}' type='hidden'/>`);
          input = $(`input[name='${name}']`, form);
        }
        input.val(value);
        // omit the field if the value is set to any
        if (value === "any") {
          return input.remove();
        }
      });
      // extract the data of the listing form and post it to the AddAnalysesView
      form_data = new FormData(form[0]);
      form_data.set("table_only", form_id);
      return this.ajax_submit({
        data: form_data,
        processData: false, // do not transform to a query string
        contentType: false // do not set any content type header
      }).done(function(data) {
        var $container, $data;
        $container = $("div.bika-listing-table-container", form);
        $data = $(data);
        if ($data.find("tbody").length === 0) {
          return $container.html(`<div class='discreet info'>0 ${_('Results')}</div>`);
        } else {
          $container.html(data);
          return window.bika.lims.BikaListingTableView.load_transitions();
        }
      });
    }

  };

  window.WorksheetAddQCAnalysesView = class WorksheetAddQCAnalysesView {
    constructor() {
      /*
       * Controller class for Worksheet's add blank/control views
       */
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      /* METHODS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_base_url = this.get_base_url.bind(this);
      this.get_authenticator = this.get_authenticator.bind(this);
      this.get_selected_services = this.get_selected_services.bind(this);
      this.get_control_type = this.get_control_type.bind(this);
      this.get_postion = this.get_postion.bind(this);
      this.load_controls = this.load_controls.bind(this);
      /* EVENT HANDLER */
      this.on_service_click = this.on_service_click.bind(this);
      this.on_referencesample_row_click = this.on_referencesample_row_click.bind(this);
    }

    load() {
      console.debug("WorksheetAddQCAnalysesView::load");
      // bind the event handler to the elements
      this.bind_eventhandler();
      // initially load the references
      return this.load_controls();
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetAddQCAnalysesView::bind_eventhandler");
      // Service checkbox clicked
      $("body").on("click", "#worksheet_services input[id*='_cb_']", this.on_service_click);
      // click a Reference Sample in add_control or add_blank
      return $("body").on("click", "#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr", this.on_referencesample_row_click);
    }

    ajax_submit(options = {}) {
      var done;
      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
      // some sane option defaults
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_base_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      console.debug(">>> ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = () => {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
    }

    get_base_url() {
      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    }

    get_authenticator() {
      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    }

    get_selected_services() {
      /*
       * Returns a list of selected service uids
       */
      var $table, services;
      $table = $("table.bika-listing-table");
      services = [];
      $("input:checked", $table).each(function(index, element) {
        return services.push(element.value);
      });
      return services;
    }

    get_control_type() {
      /*
       * Returns the control type
       */
      var control_type;
      control_type = "b";
      if (window.location.href.search("add_control") > -1) {
        control_type = "c";
      }
      return control_type;
    }

    get_postion() {
      /*
       * Returns the postition
       */
      var position;
      position = $("#position").val();
      return position || "new";
    }

    load_controls() {
      /*
       * Load the controls
       */
      var base_url, element, url;
      base_url = this.get_base_url();
      base_url = base_url.replace("/add_blank", "").replace("/add_control", "");
      url = `${base_url}/getWorksheetReferences`;
      element = $("#worksheet_add_references");
      if (element.length === 0) {
        console.warn("Element with id='#worksheet_add_references' missing!");
        return;
      }
      return this.ajax_submit({
        url: url,
        data: {
          service_uids: this.get_selected_services().join(","),
          control_type: this.get_control_type(),
          _authenticator: this.get_authenticator()
        }
      }).done(function(data) {
        return element.html(data);
      });
    }

    on_service_click(event) {
      /*
       * Eventhandler when a service checkbox was clicked
       */
      console.debug("°°° WorksheetAddQCAnalysesView::on_category_change °°°");
      return this.load_controls();
    }

    on_referencesample_row_click(event) {
      var $el, $form, action, control_type, selected_services, uid;
      /*
       * Eventhandler for a click on the loaded referencesample listing
       *
       * A reference sample for the service need to be added via
       * Setup -> Supplier -> Referene Samples
       */
      console.debug("°°° WorksheetAddQCAnalysesView::on_referencesample_row_click °°°");
      // The clicked element is a row from the referencesample listing
      $el = $(event.currentTarget);
      uid = $el.attr("uid");
      // we want to submit to the worksheet.py/add_control or add_blank views.
      $form = $el.parents("form");
      control_type = this.get_control_type();
      action = "add_blank";
      if (control_type === "c") {
        action = "add_control";
      }
      $form.attr("action", action);
      selected_services = this.get_selected_services().join(",");
      $form.append(`<input type='hidden' value='${selected_services}' name='selected_service_uids'/>`);
      // tell the form handler which reference UID was clicked
      $form.append(`<input type='hidden' value='${uid}' name='reference_uid'/>`);
      // add the position dropdown's value to the form before submitting.
      $form.append(`<input type='hidden' value='${this.get_postion()}' name='position'/>`);
      // submit the referencesample listing form
      return $form.submit();
    }

  };

  window.WorksheetAddDuplicateAnalysesView = class WorksheetAddDuplicateAnalysesView {
    constructor() {
      /*
       * Controller class for Worksheet's add blank/control views
       */
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      /* METHODS */
      this.get_postion = this.get_postion.bind(this);
      /* EVENT HANDLER */
      this.on_duplicate_row_click = this.on_duplicate_row_click.bind(this);
    }

    load() {
      console.debug("WorksheetAddDuplicateAnalysesView::load");
      // bind the event handler to the elements
      return this.bind_eventhandler();
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetAddDuplicateAnalysesView::bind_eventhandler");
      // Service checkbox clicked
      return $("body").on("click", "#worksheet_add_duplicate_ars .bika-listing-table tbody.item-listing-tbody tr", this.on_duplicate_row_click);
    }

    get_postion() {
      /*
       * Returns the postition
       */
      var position;
      position = $("#position").val();
      return position || "new";
    }

    on_duplicate_row_click(event) {
      var $el, $form, uid;
      /*
       * Eventhandler for a click on a row of the loaded dduplicate listing
       */
      console.debug("°°° WorksheetAddDuplicateAnalysesView::on_duplicate_row_click °°°");
      $el = $(event.currentTarget);
      uid = $el.attr("uid");
      // we want to submit to the worksheet.py/add_duplicate view.
      $form = $el.parents("form");
      $form.attr("action", "add_duplicate");
      // add the position dropdown's value to the form before submitting.
      $form.append(`<input type='hidden' value='${uid}' name='ar_uid'/>`);
      $form.append(`<input type='hidden' value='${this.get_postion()}' name='position'/>`);
      return $form.submit();
    }

  };

  window.WorksheetManageResultsView = class WorksheetManageResultsView {
    constructor() {
      /*
       * Controller class for Worksheet's manage results view
       */
      this.load = this.load.bind(this);
      /* INITIALIZERS */
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.init_instruments_and_methods = this.init_instruments_and_methods.bind(this);
      /* METHODS */
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.get_base_url = this.get_base_url.bind(this);
      this.get_authenticator = this.get_authenticator.bind(this);
      this.get_analysis_uids = this.get_analysis_uids.bind(this);
      this.get_method_by_analysis_uid = this.get_method_by_analysis_uid.bind(this);
      this.is_instrument_allowed = this.is_instrument_allowed.bind(this);
      this.load_analysis_method_constraint = this.load_analysis_method_constraint.bind(this);
      /* EVENT HANDLER */
      this.on_constraints_loaded = this.on_constraints_loaded.bind(this);
      this.on_analyst_change = this.on_analyst_change.bind(this);
      this.on_layout_change = this.on_layout_change.bind(this);
      this.on_instrument_change = this.on_instrument_change.bind(this);
      this.on_method_change = this.on_method_change.bind(this);
      this.on_analysis_instrument_focus = this.on_analysis_instrument_focus.bind(this);
      this.on_analysis_instrument_change = this.on_analysis_instrument_change.bind(this);
      this.on_detection_limit_change = this.on_detection_limit_change.bind(this);
      this.on_remarks_balloon_clicked = this.on_remarks_balloon_clicked.bind(this);
      this.on_wideiterims_analyses_change = this.on_wideiterims_analyses_change.bind(this);
      this.on_wideiterims_interims_change = this.on_wideiterims_interims_change.bind(this);
      this.on_wideinterims_apply_click = this.on_wideinterims_apply_click.bind(this);
    }

    load() {
      console.debug("WorksheetManageResultsView::load");
      // load translations
      jarn.i18n.loadCatalog('bika');
      this._ = window.jarn.i18n.MessageFactory('bika');
      this._pmf = window.jarn.i18n.MessageFactory('plone');
      // bind the event handler to the elements
      this.bind_eventhandler();
      // method instrument constraints
      this.constraints = null;
      // initialize
      this.init_instruments_and_methods();
      // dev only
      return window.ws = this;
    }

    bind_eventhandler() {
      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetManageResultsView::bind_eventhandler");
      // Analyst changed
      $("body").on("change", ".manage_results_header .analyst", this.on_analyst_change);
      // Layout changed
      $("body").on("change", "#resultslayout_form #resultslayout", this.on_layout_change);
      // Instrument changed
      $("body").on("change", ".manage_results_header .instrument", this.on_instrument_change);
      // Method changed
      $("body").on("change", "table.bika-listing-table select.listing_select_entry[field='Method']", this.on_method_change);
      // Analysis instrument focused
      $("body").on("focus", "table.bika-listing-table select.listing_select_entry[field='Instrument']", this.on_analysis_instrument_focus);
      // Analysis instrument changed
      $("body").on("change", "table.bika-listing-table select.listing_select_entry[field='Instrument']", this.on_analysis_instrument_change);
      // Detection limit changed
      $("body").on("change", "select[name^='DetectionLimit.']", this.on_detection_limit_change);
      // Remarks balloon clicked
      $("body").on("click", "a.add-remark", this.on_remarks_balloon_clicked);
      // Wide interims changed
      $("body").on("change", "#wideinterims_analyses", this.on_wideiterims_analyses_change);
      $("body").on("change", "#wideinterims_interims", this.on_wideiterims_interims_change);
      $("body").on("click", "#wideinterims_apply", this.on_wideinterims_apply_click);
      /* internal events */
      // handle value changes in the form
      return $(this).on("constraints:loaded", this.on_constraints_loaded);
    }

    init_instruments_and_methods() {
      /*
       * Applies the rules and constraints to each analysis displayed in the
       * manage results view regarding to methods, instruments and results.
       *
       * For example, this service is responsible for disabling the results field
       * if the analysis has no valid instrument available for the selected method,
       * if the service don't allow manual entry of results.
       *
       * Another example is that this service is responsible of populating the
       * list of instruments avialable for an analysis service when the user
       * changes the method to be used.
       *
       * See docs/imm_results_entry_behavior.png for detailed information.
       */
      var analysis_uids;
      analysis_uids = this.get_analysis_uids();
      return this.ajax_submit({
        url: `${this.get_portal_url()}/get_method_instrument_constraints`,
        data: {
          _authenticator: this.get_authenticator,
          uids: $.toJSON(analysis_uids)
        },
        dataType: "json"
      }).done(function(data) {
        this.constraints = data;
        return $(this).trigger("constraints:loaded", data);
      });
    }

    ajax_submit(options = {}) {
      var done;
      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
      // some sane option defaults
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_base_url();
      }
      if (options.context == null) {
        options.context = this;
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
       * Return the portal url (calculated in code)
       */
      var url;
      url = $("input[name=portal_url]").val();
      return url || window.portal_url;
    }

    get_base_url() {
      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    }

    get_authenticator() {
      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    }

    get_analysis_uids() {
      /*
       * Returns a list of analysis UIDs
       */
      var analysis_uids, data;
      analysis_uids = [];
      data = $.parseJSON($("#item_data").val());
      $.each(data, function(uid, value) {
        return analysis_uids.push(uid);
      });
      return analysis_uids;
    }

    get_method_by_analysis_uid(analysis_uid) {
      /*
       * Return the method UID of the analysis identified by analysis_uid
       */
      var $method_field, method_uid;
      $method_field = $(`select.listing_select_entry[field='Method'][uid='${analysis_uid}']`);
      method_uid = $method_field.val();
      return method_uid || "";
    }

    is_instrument_allowed(instrument_uid) {
      /*
       * Check if the Instrument is allowed to appear in Instrument list of Analysis.
       *
       * Returns true if multiple use of an Instrument is enabled for assigned
       * Worksheet Template or UID is not in selected Instruments
       *
       * @param {uid} instrument_uid - UID of Instrument.
       */
      var allowed, i_selectors, multiple_enabled;
      allowed = true;
      multiple_enabled = $("#instrument_multiple_use").attr("value");
      if (multiple_enabled !== "True") {
        i_selectors = $("select.listing_select_entry[field='Instrument']");
        $.each(i_selectors, function(index, element) {
          if (element.value === instrument_uid) {
            return allowed = false;
          }
        });
      }
      return allowed;
    }

    load_analysis_method_constraint(analysis_uid, method_uid) {
      var analysis_constraints, i_selector, ins_old_val, m_selector, me, method_constraints, method_name;
      /*
       * Applies the constraints and rules to the specified analysis regarding to
       * the method specified.
       *
       * If method is null, the function assumes the rules must apply for the
       * currently selected method.
       *
       * The function uses the variable mi_constraints to find out which is the
       * rule to be applied to the analysis and method specified.
       *
       * See init_instruments_and_methods() function for further information
       * about the constraints and rules retrieval and assignment.
       *
       * @param {string} analysis_uid: Analysis UID
       * @param {string} method_uid: Method UID
       *
       * If `method_uid` is null, uses the method that is currently selected for
       * the specified analysis
       */
      console.debug(`WorksheetManageResultsView::load_analysis_method_constraint:analysis_uid=${analysis_uid} method_uid=${method_uid}`);
      // reference to this object for $.each calls
      me = this;
      if (!method_uid) {
        method_uid = this.get_method_by_analysis_uid(analysis_uid);
      }
      analysis_constraints = this.constraints[analysis_uid];
      if (!analysis_constraints) {
        return;
      }
      method_constraints = analysis_constraints[method_uid];
      if (!method_constraints) {
        return;
      }
      if (method_constraints.length < 7) {
        return;
      }
      // method selector
      m_selector = $(`select.listing_select_entry[field='Method'][uid='${analysis_uid}']`);
      // instrument selector
      i_selector = $(`select.listing_select_entry[field='Instrument'][uid='${analysis_uid}']`);
      // Remove None option in method selector
      $(m_selector).find('option[value=""]').remove();
      if (method_constraints[1] === 1) {
        $(m_selector).prepend(`<option value=''>${_('Not defined')}</option>`);
      }
      // Select the method
      $(m_selector).val(method_uid);
      // Method selector visible?
      // 0: no, 1: yes, 2: label, 3: readonly
      $(m_selector).prop("disabled", false);
      $(`.method-label[uid='${analysis_uid}']`).remove();
      if (method_constraints[0] === 0) {
        $(m_selector).hide();
      } else if (method_constraints[0] === 1) {
        $(m_selector).show();
      } else if (method_constraints[0] === 2) {
        // XXX length check of an object??
        if (analysis_constraints.length > 1) {
          $(m_selector).hide();
          method_name = $(m_selector).find(`option[value='${method_uid}']`).innerHtml();
          $(m_selector).after(`<span class='method-label' uid='${analysis_uid}' href='#'>${method_name}</span>`);
        }
      } else if (method_constraints[0] === 3) {
        $(m_selector).show();
      }
      // We are going to reload the instrument list.
      // Enable all disabled options from other Instrument lists which has the same
      // value as old value of this instrument selectbox.
      ins_old_val = $(i_selector).val();
      if (ins_old_val && ins_old_val !== '') {
        $(`table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='${ins_old_val}'] option[value='${ins_old_val}']`).prop("disabled", false);
      }
      // Populate instruments list
      $(i_selector).find("option").remove();
      if (method_constraints[7]) {
        $.each(method_constraints[7], function(key, value) {
          if (me.is_instrument_allowed(key)) {
            return $(i_selector).append(`<option value='${key}'>${value}</option>`);
          } else {
            return $(i_selector).append(`<option value='${key}' disabled='disabled'>${value}</option>`);
          }
        });
      }
      // None option in instrument selector?
      if (method_constraints[3] === 1) {
        $(i_selector).prepend(`<option selected='selected' value=''>${_('None')}</option>`);
      }
      // Select the default instrument
      if (me.is_instrument_allowed(method_constraints[4])) {
        $(i_selector).val(method_constraints[4]);
        // Disable this Instrument in the other Instrument SelectBoxes
        $(`table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='${method_constraints[4]}'] option[value='${method_constraints[4]}']`).prop("disabled", true);
      }
      // Instrument selector visible?
      if (method_constraints[2] === 0) {
        $(i_selector).hide();
      } else if (method_constraints[2] === 1) {
        $(i_selector).show();
      }
      // Allow to edit results?
      if (method_constraints[5] === 0) {
        $(`.interim input[uid='${analysis_uid}']`).val("");
        $(`input[field='Result'][uid='${analysis_uid}']`).val("");
        $(`.interim input[uid='${analysis_uid}']`).prop("disabled", true);
        $(`input[field='Result'][uid='${analysis_uid}']`).prop("disabled", true);
      } else if (method_constraints[5] === 1) {
        $(`.interim input[uid='${analysis_uid}']`).prop("disabled", false);
        $(`input[field='Result'][uid='${analysis_uid}']`).prop("disabled", false);
      }
      // Info/Warn message?
      $(`.alert-instruments-invalid[uid='${analysis_uid}']`).remove();
      if (method_constraints[6] && method_constraints[6] !== "") {
        $(i_selector).after(`<img uid='${analysis_uid}' class='alert-instruments-invalid' src='${this.get_portal_url()}/++resource++bika.lims.images/warning.png' title='${method_constraints[6]}'>`);
      }
      return $(`.amconstr[uid='${analysis_uid}']`).remove();
    }

    on_constraints_loaded(event) {
      var me;
      /*
       * Eventhandler when the instrument and method constraints were loaded from the server
       */
      console.debug("°°° WorksheetManageResultsView::on_constraints_loaded °°°");
      me = this;
      return $.each(this.get_analysis_uids(), function(index, uid) {
        return me.load_analysis_method_constraint(uid, null);
      });
    }

    on_analyst_change(event) {
      var $el, analyst, base_url, url;
      /*
       * Eventhandler when the analyst select changed
       */
      console.debug("°°° WorksheetManageResultsView::on_analyst_change °°°");
      $el = $(event.currentTarget);
      analyst = $el.val();
      if (analyst === "") {
        return false;
      }
      base_url = this.get_base_url();
      url = base_url.replace("/manage_results", "") + "/set_analyst";
      return this.ajax_submit({
        url: url,
        data: {
          value: analyst,
          _authenticator: this.get_authenticator()
        },
        dataType: "json"
      }).done(function(data) {
        return bika.lims.SiteView.notify_in_panel(this._pmf("Changes saved."), "succeed");
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(this._("Could not set the selected analyst"), "error");
      });
    }

    on_layout_change(event) {
      var $el;
      /*
       * Eventhandler when the analyst changed
       */
      console.debug("°°° WorksheetManageResultsView::on_layout_change °°°");
      return $el = $(event.currentTarget);
    }

    on_instrument_change(event) {
      var $el, base_url, instrument_uid, url;
      /*
       * Eventhandler when the instrument changed
       */
      console.debug("°°° WorksheetManageResultsView::on_instrument_change °°°");
      $el = $(event.currentTarget);
      instrument_uid = $el.val();
      if (instrument_uid === "") {
        return false;
      }
      base_url = this.get_base_url();
      url = base_url.replace("/manage_results", "") + "/set_instrument";
      return this.ajax_submit({
        url: url,
        data: {
          value: instrument_uid,
          _authenticator: this.get_authenticator()
        },
        dataType: "json"
      }).done(function(data) {
        bika.lims.SiteView.notify_in_panel(this._pmf("Changes saved."), "succeed");
        // Set the selected instrument to all the analyses which that can be done
        // using that instrument. The rest of of the instrument picklist will not
        // be changed
        $(`select.listing_select_entry[field='Instrument'] option[value='${instrument_uid}']`).parent().find(`option[value='${instrument_uid}']`).prop("selected", false);
        return $(`select.listing_select_entry[field='Instrument'] option[value='${instrument_uid}']`).prop("selected", true);
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(this._("Unable to apply the selected instrument"), "error");
      });
    }

    on_method_change(event) {
      var $el, analysis_uid, method_uid;
      /*
       * Eventhandler when the method changed
       *
       */
      console.debug("°°° WorksheetManageResultsView::on_method_change °°°");
      $el = $(event.currentTarget);
      analysis_uid = $el.attr("uid");
      method_uid = $el.val();
      // Change the instruments to be shown for an analysis when the method selected changes
      return this.load_analysis_method_constraint(analysis_uid, method_uid);
    }

    on_analysis_instrument_focus(event) {
      var $el;
      /*
       * Eventhandler when the instrument of an analysis is focused
       *
       * Only needed to remember the last value
       */
      console.debug("°°° WorksheetManageResultsView::on_analysis_instrument_focus °°°");
      $el = $(event.currentTarget);
      this.previous_instrument = $el.val();
      return console.info(this.previous_instrument);
    }

    on_analysis_instrument_change(event) {
      var $el, analysis_uid, instrument_uid;
      /*
       * Eventhandler when the instrument of an analysis changed
       *
       * If a new instrument is chosen for the analysis, disable this Instrument
       * for the other analyses. Also, remove the restriction of previous
       * Instrument of this analysis to be chosen in the other analyses.
       */
      console.debug("°°° WorksheetManageResultsView::on_analysis_instrument_change °°°");
      $el = $(event.currentTarget);
      analysis_uid = $el.attr("uid");
      instrument_uid = $el.val();
      // Disable New Instrument for rest of the analyses
      $(`table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='${instrument_uid}'] option[value='${instrument_uid}']`).prop("disabled", true);
      // Enable previous Instrument everywhere
      $(`table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='${this.previous_instrument}']`).prop("disabled", false);
      // Enable 'None' option as well.
      return $("table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='']").prop("disabled", false);
    }

    on_detection_limit_change(event) {
      var $el, defdls, resfld, uncfld;
      /*
       * Eventhandler when the detection limit changed
       */
      console.debug("°°° WorksheetManageResultsView::on_detection_limit_change °°°");
      $el = $(event.currentTarget);
      defdls = $el.closest("td").find("input[id^='DefaultDLS.']").first().val();
      resfld = $el.closest("tr").find("input[name^='Result.']")[0];
      uncfld = $el.closest("tr").find("input[name^='Uncertainty.']");
      defdls = $.parseJSON(defdls);
      $(resfld).prop("readonly", !defdls.manual);
      if ($el.val() === "<") {
        $(resfld).val(defdls['min']);
        // Inactivate uncertainty?
        if (uncfld.length > 0) {
          $(uncfld).val("");
          $(uncfld).prop("readonly", true);
          $(uncfld).closest("td").children().hide();
        }
      } else if ($el.val() === ">") {
        $(resfld).val(defdls["max"]);
        // Inactivate uncertainty?
        if (uncfld.length > 0) {
          $(uncfld).val("");
          $(uncfld).prop("readonly", true);
          $(uncfld).closest("td").children().hide();
        }
      } else {
        $(resfld).val("");
        $(resfld).prop("readonly", false);
        // Activate uncertainty?
        if (uncfld.length > 0) {
          $(uncfld).val("");
          $(uncfld).prop("readonly", false);
          $(uncfld).closest("td").children().show();
        }
      }
      // Maybe the result is used in calculations...
      return $(resfld).change();
    }

    on_remarks_balloon_clicked(event) {
      var $el, remarks;
      /*
       * Eventhandler when the remarks balloon was clicked
       */
      console.debug("°°° WorksheetManageResultsView::on_remarks_balloon_clicked °°°");
      $el = $(event.currentTarget);
      event.preventDefault();
      remarks = $el.closest("tr").next("tr").find("td.remarks");
      return $(remarks).find("div.remarks-placeholder").toggle();
    }

    on_wideiterims_analyses_change(event) {
      var $el, category;
      /*
       * Eventhandler when the wide interims analysis selector changed
       *
       * Search all interim fields which begin with the selected category and fill
       *  the analyses interim fields to the selection
       */
      console.debug("°°° WorksheetManageResultsView::on_wideiterims_analyses_change °°°");
      $el = $(event.currentTarget);
      // Empty the wideinterim analysis field
      $("#wideinterims_interims").html("");
      category = $el.val();
      return $(`input[id^='wideinterim_${category}']`).each(function(index, element) {
        var itemval, keyword, name;
        name = $(element).attr("name");
        keyword = $(element).attr("keyword");
        itemval = `<option value='${keyword}'>${name}</option>`;
        return $("#wideinterims_interims").append(itemval);
      });
    }

    on_wideiterims_interims_change(event) {
      var $el, analysis, idinter, interim;
      /*
       * Eventhandler when the wide interims selector changed
       */
      console.debug("°°° WorksheetManageResultsView::on_wideiterims_interims_change °°°");
      $el = $(event.currentTarget);
      analysis = $("#wideinterims_analyses").val();
      interim = $el.val();
      idinter = `#wideinterim_${analysis}_${interim}`;
      return $("#wideinterims_value").val($(idinter).val());
    }

    on_wideinterims_apply_click(event) {
      var $el, analysis, empty_only, interim;
      /*
       * Eventhandler when the wide interim apply button was clicked
       */
      console.debug("°°° WorksheetManageResultsView::on_wideinterims_apply_click °°°");
      // prevent form submission
      event.preventDefault();
      $el = $(event.currentTarget);
      analysis = $("#wideinterims_analyses").val();
      interim = $("#wideinterims_interims").val();
      empty_only = $("#wideinterims_empty").is(":checked");
      return $(`tr[keyword='${analysis}'] input[field='${interim}']`).each(function(index, element) {
        if (empty_only) {
          if ($(this).val() === "" || $(this).val().match(/\d+/) === "0") {
            $(this).val($("#wideinterims_value").val());
            return $(this).change();
          }
        } else {
          $(this).val($("#wideinterims_value").val());
          return $(this).change();
        }
      });
    }

  };

}).call(this);
