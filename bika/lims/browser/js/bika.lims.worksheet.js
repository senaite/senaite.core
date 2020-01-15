
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.worksheet.coffee
 */

(function() {
  var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

  window.WorksheetFolderView = (function() {
    function WorksheetFolderView() {
      this.on_instrument_change = bind(this.on_instrument_change, this);
      this.on_template_change = bind(this.on_template_change, this);
      this.select_instrument = bind(this.select_instrument, this);
      this.get_template_instrument = bind(this.get_template_instrument, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
    * Controller class for Worksheets Folder
     */

    WorksheetFolderView.prototype.load = function() {
      console.debug("WorksheetFolderView::load");
      return this.bind_eventhandler();
    };


    /* INITIALIZERS */

    WorksheetFolderView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetFolderView::bind_eventhandler");
      $("body").on("change", "select.template", this.on_template_change);
      return $("body").on("change", "select.instrument", this.on_instrument_change);
    };


    /* METHODS */

    WorksheetFolderView.prototype.get_template_instrument = function() {

      /*
       * TODO: Refactor to get the data directly from the server
       * Returns the JSON parsed value of the HTML element with the class
         `templateinstruments`
       */
      var input, value;
      console.debug("WorksheetFolderView::get_template_instruments");
      input = $("input.templateinstruments");
      value = input.val();
      return $.parseJSON(value);
    };

    WorksheetFolderView.prototype.select_instrument = function(instrument_uid) {

      /*
       * Select instrument by UID
       */
      var option, select;
      select = $(".instrument");
      option = select.find("option[value='" + instrument_uid + "']");
      if (option) {
        return option.prop("selected", true);
      }
    };


    /* EVENT HANDLER */

    WorksheetFolderView.prototype.on_template_change = function(event) {

      /*
       * Eventhandler for template change
       */
      var $el, instrument_uid, template_instrument, template_uid;
      console.debug("°°° WorksheetFolderView::on_template_change °°°");
      $el = $(event.currentTarget);
      template_uid = $el.val();
      template_instrument = this.get_template_instrument();
      instrument_uid = template_instrument[template_uid];
      return this.select_instrument(instrument_uid);
    };

    WorksheetFolderView.prototype.on_instrument_change = function(event) {

      /*
       * Eventhandler for instrument change
       */
      var $el, instrument_uid, message;
      console.debug("°°° WorksheetFolderView::on_instrument_change °°°");
      $el = $(event.currentTarget);
      instrument_uid = $el.val();
      if (instrument_uid) {
        message = _("Only the analyses for which the selected instrument is allowed will be added automatically.");
        return bika.lims.SiteView.notify_in_panel(message, "error");
      }
    };

    return WorksheetFolderView;

  })();

  window.WorksheetAddQCAnalysesView = (function() {
    function WorksheetAddQCAnalysesView() {
      this.on_referencesample_row_click = bind(this.on_referencesample_row_click, this);
      this.on_service_click = bind(this.on_service_click, this);
      this.load_controls = bind(this.load_controls, this);
      this.get_postion = bind(this.get_postion, this);
      this.get_control_type = bind(this.get_control_type, this);
      this.get_selected_services = bind(this.get_selected_services, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's add blank/control views
     */

    WorksheetAddQCAnalysesView.prototype.load = function() {
      console.debug("WorksheetAddQCAnalysesView::load");
      this.bind_eventhandler();
      return this.load_controls();
    };


    /* INITIALIZERS */

    WorksheetAddQCAnalysesView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetAddQCAnalysesView::bind_eventhandler");
      $("body").on("click", "#worksheet_services input[id*='_cb_']", this.on_service_click);
      return $("body").on("click", "#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr", this.on_referencesample_row_click);
    };


    /* METHODS */

    WorksheetAddQCAnalysesView.prototype.ajax_submit = function(options) {
      var done;
      if (options == null) {
        options = {};
      }

      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
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
      done = (function(_this) {
        return function() {
          return $(_this).trigger("ajax:submit:end");
        };
      })(this);
      return $.ajax(options).done(done);
    };

    WorksheetAddQCAnalysesView.prototype.get_base_url = function() {

      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    };

    WorksheetAddQCAnalysesView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    WorksheetAddQCAnalysesView.prototype.get_selected_services = function() {

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
    };

    WorksheetAddQCAnalysesView.prototype.get_control_type = function() {

      /*
       * Returns the control type
       */
      var control_type;
      control_type = "b";
      if (window.location.href.search("add_control") > -1) {
        control_type = "c";
      }
      return control_type;
    };

    WorksheetAddQCAnalysesView.prototype.get_postion = function() {

      /*
       * Returns the postition
       */
      var position;
      position = $("#position").val();
      return position || "new";
    };

    WorksheetAddQCAnalysesView.prototype.load_controls = function() {

      /*
       * Load the controls
       */
      var base_url, element, url;
      base_url = this.get_base_url();
      base_url = base_url.replace("/add_blank", "").replace("/add_control", "");
      url = base_url + "/getWorksheetReferences";
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
    };


    /* EVENT HANDLER */

    WorksheetAddQCAnalysesView.prototype.on_service_click = function(event) {

      /*
       * Eventhandler when a service checkbox was clicked
       */
      console.debug("°°° WorksheetAddQCAnalysesView::on_category_change °°°");
      return this.load_controls();
    };

    WorksheetAddQCAnalysesView.prototype.on_referencesample_row_click = function(event) {

      /*
       * Eventhandler for a click on the loaded referencesample listing
       *
       * A reference sample for the service need to be added via
       * Setup -> Supplier -> Referene Samples
       */
      var $el, $form, action, control_type, selected_services, uid;
      console.debug("°°° WorksheetAddQCAnalysesView::on_referencesample_row_click °°°");
      $el = $(event.currentTarget);
      uid = $el.attr("uid");
      $form = $el.parents("form");
      control_type = this.get_control_type();
      action = "add_blank";
      if (control_type === "c") {
        action = "add_control";
      }
      $form.attr("action", action);
      selected_services = this.get_selected_services().join(",");
      $form.append("<input type='hidden' value='" + selected_services + "' name='selected_service_uids'/>");
      $form.append("<input type='hidden' value='" + uid + "' name='reference_uid'/>");
      $form.append("<input type='hidden' value='" + (this.get_postion()) + "' name='position'/>");
      return $form.submit();
    };

    return WorksheetAddQCAnalysesView;

  })();

  window.WorksheetAddDuplicateAnalysesView = (function() {
    function WorksheetAddDuplicateAnalysesView() {
      this.on_duplicate_row_click = bind(this.on_duplicate_row_click, this);
      this.get_postion = bind(this.get_postion, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's add blank/control views
     */

    WorksheetAddDuplicateAnalysesView.prototype.load = function() {
      console.debug("WorksheetAddDuplicateAnalysesView::load");
      return this.bind_eventhandler();
    };


    /* INITIALIZERS */

    WorksheetAddDuplicateAnalysesView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetAddDuplicateAnalysesView::bind_eventhandler");
      return $("body").on("click", "#worksheet_add_duplicate_ars .bika-listing-table tbody.item-listing-tbody tr", this.on_duplicate_row_click);
    };


    /* METHODS */

    WorksheetAddDuplicateAnalysesView.prototype.get_postion = function() {

      /*
       * Returns the postition
       */
      var position;
      position = $("#position").val();
      return position || "new";
    };


    /* EVENT HANDLER */

    WorksheetAddDuplicateAnalysesView.prototype.on_duplicate_row_click = function(event) {

      /*
       * Eventhandler for a click on a row of the loaded dduplicate listing
       */
      var $el, $form, uid;
      console.debug("°°° WorksheetAddDuplicateAnalysesView::on_duplicate_row_click °°°");
      $el = $(event.currentTarget);
      uid = $el.attr("uid");
      $form = $el.parents("form");
      $form.attr("action", "add_duplicate");
      $form.append("<input type='hidden' value='" + uid + "' name='ar_uid'/>");
      $form.append("<input type='hidden' value='" + (this.get_postion()) + "' name='position'/>");
      return $form.submit();
    };

    return WorksheetAddDuplicateAnalysesView;

  })();

  window.WorksheetManageResultsView = (function() {
    function WorksheetManageResultsView() {
      this.on_wideinterims_apply_click = bind(this.on_wideinterims_apply_click, this);
      this.on_slot_remarks_click = bind(this.on_slot_remarks_click, this);
      this.on_wideiterims_interims_change = bind(this.on_wideiterims_interims_change, this);
      this.on_wideiterims_analyses_change = bind(this.on_wideiterims_analyses_change, this);
      this.on_remarks_balloon_clicked = bind(this.on_remarks_balloon_clicked, this);
      this.on_analysis_instrument_change = bind(this.on_analysis_instrument_change, this);
      this.on_analysis_instrument_focus = bind(this.on_analysis_instrument_focus, this);
      this.on_method_change = bind(this.on_method_change, this);
      this.on_instrument_change = bind(this.on_instrument_change, this);
      this.on_layout_change = bind(this.on_layout_change, this);
      this.on_analyst_change = bind(this.on_analyst_change, this);
      this.on_constraints_loaded = bind(this.on_constraints_loaded, this);
      this.load_analysis_method_constraint = bind(this.load_analysis_method_constraint, this);
      this.is_instrument_allowed = bind(this.is_instrument_allowed, this);
      this.get_method_by_analysis_uid = bind(this.get_method_by_analysis_uid, this);
      this.get_analysis_uids = bind(this.get_analysis_uids, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.init_instruments_and_methods = bind(this.init_instruments_and_methods, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's manage results view
     */

    WorksheetManageResultsView.prototype.load = function() {
      console.debug("WorksheetManageResultsView::load");
      jarn.i18n.loadCatalog("senaite.core");
      this._ = window.jarn.i18n.MessageFactory("senaite.core");
      this._pmf = window.jarn.i18n.MessageFactory('plone');
      this.bind_eventhandler();
      this.constraints = null;
      this.init_instruments_and_methods();
      return window.ws = this;
    };


    /* INITIALIZERS */

    WorksheetManageResultsView.prototype.bind_eventhandler = function() {

      /*
       * Binds callbacks on elements
       *
       * N.B. We attach all the events to the form and refine the selector to
       * delegate the event: https://learn.jquery.com/events/event-delegation/
       *
       */
      console.debug("WorksheetManageResultsView::bind_eventhandler");
      $("body").on("change", ".manage_results_header .analyst", this.on_analyst_change);
      $("body").on("change", "#resultslayout_form #resultslayout", this.on_layout_change);
      $("body").on("change", ".manage_results_header .instrument", this.on_instrument_change);
      $("body").on("change", "table.bika-listing-table select.listing_select_entry[field='Method']", this.on_method_change);
      $("body").on("focus", "table.bika-listing-table select.listing_select_entry[field='Instrument']", this.on_analysis_instrument_focus);
      $("body").on("change", "table.bika-listing-table select.listing_select_entry[field='Instrument']", this.on_analysis_instrument_change);
      $("body").on("click", "a.add-remark", this.on_remarks_balloon_clicked);
      $("body").on("change", "#wideinterims_analyses", this.on_wideiterims_analyses_change);
      $("body").on("change", "#wideinterims_interims", this.on_wideiterims_interims_change);
      $("body").on("click", "#wideinterims_apply", this.on_wideinterims_apply_click);
      $("body").on("click", "img.slot-remarks", this.on_slot_remarks_click);

      /* internal events */
      return $(this).on("constraints:loaded", this.on_constraints_loaded);
    };

    WorksheetManageResultsView.prototype.init_instruments_and_methods = function() {

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
        url: (this.get_portal_url()) + "/get_method_instrument_constraints",
        data: {
          _authenticator: this.get_authenticator,
          uids: $.toJSON(analysis_uids)
        },
        dataType: "json"
      }).done(function(data) {
        this.constraints = data;
        return $(this).trigger("constraints:loaded", data);
      });
    };


    /* METHODS */

    WorksheetManageResultsView.prototype.ajax_submit = function(options) {
      var done;
      if (options == null) {
        options = {};
      }

      /*
       * Ajax Submit with automatic event triggering and some sane defaults
       */
      console.debug("°°° ajax_submit °°°");
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
      done = (function(_this) {
        return function() {
          return $(_this).trigger("ajax:submit:end");
        };
      })(this);
      return $.ajax(options).done(done);
    };

    WorksheetManageResultsView.prototype.get_portal_url = function() {

      /*
       * Return the portal url (calculated in code)
       */
      var url;
      url = $("input[name=portal_url]").val();
      return url || window.portal_url;
    };

    WorksheetManageResultsView.prototype.get_base_url = function() {

      /*
       * Return the current base url
       */
      var url;
      url = window.location.href;
      return url.split('?')[0];
    };

    WorksheetManageResultsView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    WorksheetManageResultsView.prototype.get_analysis_uids = function() {

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
    };

    WorksheetManageResultsView.prototype.get_method_by_analysis_uid = function(analysis_uid) {

      /*
       * Return the method UID of the analysis identified by analysis_uid
       */
      var $method_field, method_uid;
      $method_field = $("select.listing_select_entry[field='Method'][uid='" + analysis_uid + "']");
      method_uid = $method_field.val();
      return method_uid || "";
    };

    WorksheetManageResultsView.prototype.is_instrument_allowed = function(instrument_uid) {

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
    };

    WorksheetManageResultsView.prototype.load_analysis_method_constraint = function(analysis_uid, method_uid) {

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
      var analysis_constraints, i_selector, ins_old_val, m_selector, me, method_constraints, method_name;
      console.debug("WorksheetManageResultsView::load_analysis_method_constraint:analysis_uid=" + analysis_uid + " method_uid=" + method_uid);
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
      m_selector = $("select.listing_select_entry[field='Method'][uid='" + analysis_uid + "']");
      i_selector = $("select.listing_select_entry[field='Instrument'][uid='" + analysis_uid + "']");
      $(m_selector).find('option[value=""]').remove();
      if (method_constraints[1] === 1) {
        $(m_selector).prepend("<option value=''>" + (_('Not defined')) + "</option>");
      }
      $(m_selector).val(method_uid);
      $(m_selector).prop("disabled", false);
      $(".method-label[uid='" + analysis_uid + "']").remove();
      if (method_constraints[0] === 0) {
        $(m_selector).hide();
      } else if (method_constraints[0] === 1) {
        $(m_selector).show();
      } else if (method_constraints[0] === 2) {
        if (analysis_constraints.length > 1) {
          $(m_selector).hide();
          method_name = $(m_selector).find("option[value='" + method_uid + "']").innerHtml();
          $(m_selector).after("<span class='method-label' uid='" + analysis_uid + "' href='#'>" + method_name + "</span>");
        }
      } else if (method_constraints[0] === 3) {
        $(m_selector).show();
      }
      ins_old_val = $(i_selector).val();
      if (ins_old_val && ins_old_val !== '') {
        $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='" + ins_old_val + "'] option[value='" + ins_old_val + "']").prop("disabled", false);
      }
      $(i_selector).find("option").remove();
      if (method_constraints[7]) {
        $.each(method_constraints[7], function(key, value) {
          if (me.is_instrument_allowed(key)) {
            return $(i_selector).append("<option value='" + key + "'>" + value + "</option>");
          } else {
            return $(i_selector).append("<option value='" + key + "' disabled='disabled'>" + value + "</option>");
          }
        });
      }
      if (method_constraints[3] === 1) {
        $(i_selector).prepend("<option selected='selected' value=''>" + (_('None')) + "</option>");
      }
      if (me.is_instrument_allowed(method_constraints[4])) {
        $(i_selector).val(method_constraints[4]);
        $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='" + method_constraints[4] + "'] option[value='" + method_constraints[4] + "']").prop("disabled", true);
      }
      if (method_constraints[2] === 0) {
        $(i_selector).hide();
      } else if (method_constraints[2] === 1) {
        $(i_selector).show();
      }
      if (method_constraints[5] === 0) {
        $(".interim input[uid='" + analysis_uid + "']").val("");
        $("input[field='Result'][uid='" + analysis_uid + "']").val("");
        $(".interim input[uid='" + analysis_uid + "']").prop("disabled", true);
        $("input[field='Result'][uid='" + analysis_uid + "']").prop("disabled", true);
      } else if (method_constraints[5] === 1) {
        $(".interim input[uid='" + analysis_uid + "']").prop("disabled", false);
        $("input[field='Result'][uid='" + analysis_uid + "']").prop("disabled", false);
      }
      $(".alert-instruments-invalid[uid='" + analysis_uid + "']").remove();
      if (method_constraints[6] && method_constraints[6] !== "") {
        $(i_selector).after("<img uid='" + analysis_uid + "' class='alert-instruments-invalid' src='" + (this.get_portal_url()) + "/++resource++bika.lims.images/warning.png' title='" + method_constraints[6] + "'>");
      }
      return $(".amconstr[uid='" + analysis_uid + "']").remove();
    };


    /* EVENT HANDLER */

    WorksheetManageResultsView.prototype.on_constraints_loaded = function(event) {

      /*
       * Eventhandler when the instrument and method constraints were loaded from the server
       */
      var me;
      console.debug("°°° WorksheetManageResultsView::on_constraints_loaded °°°");
      me = this;
      return $.each(this.get_analysis_uids(), function(index, uid) {
        return me.load_analysis_method_constraint(uid, null);
      });
    };

    WorksheetManageResultsView.prototype.on_analyst_change = function(event) {

      /*
       * Eventhandler when the analyst select changed
       */
      var $el, analyst, base_url, url;
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
    };

    WorksheetManageResultsView.prototype.on_layout_change = function(event) {

      /*
       * Eventhandler when the analyst changed
       */
      var $el;
      console.debug("°°° WorksheetManageResultsView::on_layout_change °°°");
      return $el = $(event.currentTarget);
    };

    WorksheetManageResultsView.prototype.on_instrument_change = function(event) {

      /*
       * Eventhandler when the instrument changed
       */
      var $el, base_url, instrument_uid, url;
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
        $("select.listing_select_entry[field='Instrument'] option[value='" + instrument_uid + "']").parent().find("option[value='" + instrument_uid + "']").prop("selected", false);
        return $("select.listing_select_entry[field='Instrument'] option[value='" + instrument_uid + "']").prop("selected", true);
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(this._("Unable to apply the selected instrument"), "error");
      });
    };

    WorksheetManageResultsView.prototype.on_method_change = function(event) {

      /*
       * Eventhandler when the method changed
       *
       */
      var $el, analysis_uid, method_uid;
      console.debug("°°° WorksheetManageResultsView::on_method_change °°°");
      $el = $(event.currentTarget);
      analysis_uid = $el.attr("uid");
      method_uid = $el.val();
      return this.load_analysis_method_constraint(analysis_uid, method_uid);
    };

    WorksheetManageResultsView.prototype.on_analysis_instrument_focus = function(event) {

      /*
       * Eventhandler when the instrument of an analysis is focused
       *
       * Only needed to remember the last value
       */
      var $el;
      console.debug("°°° WorksheetManageResultsView::on_analysis_instrument_focus °°°");
      $el = $(event.currentTarget);
      this.previous_instrument = $el.val();
      return console.info(this.previous_instrument);
    };

    WorksheetManageResultsView.prototype.on_analysis_instrument_change = function(event) {

      /*
       * Eventhandler when the instrument of an analysis changed
       *
       * If a new instrument is chosen for the analysis, disable this Instrument
       * for the other analyses. Also, remove the restriction of previous
       * Instrument of this analysis to be chosen in the other analyses.
       */
      var $el, analysis_uid, instrument_uid;
      console.debug("°°° WorksheetManageResultsView::on_analysis_instrument_change °°°");
      $el = $(event.currentTarget);
      analysis_uid = $el.attr("uid");
      instrument_uid = $el.val();
      $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='" + instrument_uid + "'] option[value='" + instrument_uid + "']").prop("disabled", true);
      $("table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='" + this.previous_instrument + "']").prop("disabled", false);
      return $("table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='']").prop("disabled", false);
    };

    WorksheetManageResultsView.prototype.on_remarks_balloon_clicked = function(event) {

      /*
       * Eventhandler when the remarks balloon was clicked
       */
      var $el, remarks;
      console.debug("°°° WorksheetManageResultsView::on_remarks_balloon_clicked °°°");
      $el = $(event.currentTarget);
      event.preventDefault();
      remarks = $el.closest("tr").next("tr").find("td.remarks");
      return $(remarks).find("div.remarks-placeholder").toggle();
    };

    WorksheetManageResultsView.prototype.on_wideiterims_analyses_change = function(event) {

      /*
       * Eventhandler when the wide interims analysis selector changed
       *
       * Search all interim fields which begin with the selected category and fill
       *  the analyses interim fields to the selection
       */
      var $el, category;
      console.debug("°°° WorksheetManageResultsView::on_wideiterims_analyses_change °°°");
      $el = $(event.currentTarget);
      $("#wideinterims_interims").html("");
      category = $el.val();
      return $("input[id^='wideinterim_" + category + "']").each(function(index, element) {
        var itemval, keyword, name;
        name = $(element).attr("name");
        keyword = $(element).attr("keyword");
        itemval = "<option value='" + keyword + "'>" + name + "</option>";
        return $("#wideinterims_interims").append(itemval);
      });
    };

    WorksheetManageResultsView.prototype.on_wideiterims_interims_change = function(event) {

      /*
       * Eventhandler when the wide interims selector changed
       */
      var $el, analysis, idinter, interim;
      console.debug("°°° WorksheetManageResultsView::on_wideiterims_interims_change °°°");
      $el = $(event.currentTarget);
      analysis = $("#wideinterims_analyses").val();
      interim = $el.val();
      idinter = "#wideinterim_" + analysis + "_" + interim;
      return $("#wideinterims_value").val($(idinter).val());
    };

    WorksheetManageResultsView.prototype.on_slot_remarks_click = function(event) {

      /*
       * Eventhandler when the remarks icon was clicked
       */
      var el;
      console.debug("°°° WorksheetManageResultsView::on_slot_remarks_click °°°");
      el = event.currentTarget;
      $(el).prepOverlay({
        subtype: "ajax",
        filter: "h1,div.remarks-widget",
        config: {
          closeOnClick: true,
          closeOnEsc: true,
          onBeforeLoad: function(event) {
            var overlay;
            overlay = this.getOverlay();
            $("div.pb-ajax>div", overlay).addClass("container");
            $("h3", overlay).remove();
            $("textarea", overlay).remove();
            $("input", overlay).remove();
            return overlay.draggable();
          },
          onLoad: function(event) {
            return $.mask.close();
          }
        }
      });
      return $(el).click();
    };

    WorksheetManageResultsView.prototype.on_wideinterims_apply_click = function(event) {

      /*
       * Eventhandler when the wide interim apply button was clicked
       */
      var $el, analysis, empty_only, interim, set_value, value;
      console.debug("°°° WorksheetManageResultsView::on_wideinterims_apply_click °°°");
      event.preventDefault();
      $el = $(event.currentTarget);
      analysis = $("#wideinterims_analyses").val();
      interim = $("#wideinterims_interims").val();
      empty_only = $("#wideinterims_empty").is(":checked");
      value = $("#wideinterims_value").val();
      set_value = function(input, value) {
        var evt, nativeInputValueSetter;
        nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(input, value);
        evt = new Event('input', {
          bubbles: true
        });
        return input.dispatchEvent(evt);
      };
      return $("tr td input[column_key='" + interim + "']").each(function(index, input) {
        if (empty_only) {
          if ($(this).val() === "" || $(this).val().match(/\d+/) === "0") {
            set_value(input, value);
          }
        } else {
          set_value(input, value);
        }
        return true;
      });
    };

    return WorksheetManageResultsView;

  })();

}).call(this);
