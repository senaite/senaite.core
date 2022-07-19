
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
      return JSON.parse(value);
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
        message = _t("Only the analyses for which the selected instrument is allowed will be added automatically.");
        return bika.lims.SiteView.notify_in_panel(message, "error");
      }
    };

    return WorksheetFolderView;

  })();

  window.WorksheetManageResultsView = (function() {
    function WorksheetManageResultsView() {
      this.on_wideinterims_apply_click = bind(this.on_wideinterims_apply_click, this);
      this.on_slot_remarks_click = bind(this.on_slot_remarks_click, this);
      this.on_wideiterims_interims_change = bind(this.on_wideiterims_interims_change, this);
      this.on_wideiterims_analyses_change = bind(this.on_wideiterims_analyses_change, this);
      this.on_instrument_change = bind(this.on_instrument_change, this);
      this.on_layout_change = bind(this.on_layout_change, this);
      this.on_analyst_change = bind(this.on_analyst_change, this);
      this.reload_analyses_listing = bind(this.reload_analyses_listing, this);
      this.get_analyses_listing = bind(this.get_analyses_listing, this);
      this.get_authenticator = bind(this.get_authenticator, this);
      this.get_base_url = bind(this.get_base_url, this);
      this.get_portal_url = bind(this.get_portal_url, this);
      this.ajax_submit = bind(this.ajax_submit, this);
      this.bind_eventhandler = bind(this.bind_eventhandler, this);
      this.load = bind(this.load, this);
    }


    /*
     * Controller class for Worksheet's manage results view
     */

    WorksheetManageResultsView.prototype.load = function() {
      console.debug("WorksheetManageResultsView::load");
      return this.bind_eventhandler();
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
      $("body").on("change", "#wideinterims_analyses", this.on_wideiterims_analyses_change);
      $("body").on("change", "#wideinterims_interims", this.on_wideiterims_interims_change);
      $("body").on("click", "#wideinterims_apply", this.on_wideinterims_apply_click);
      return $("body").on("click", "img.slot-remarks", this.on_slot_remarks_click);
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
      url = url.split("?")[0];
      return url.replace("#", "");
    };

    WorksheetManageResultsView.prototype.get_authenticator = function() {

      /*
       * Get the authenticator value
       */
      return $("input[name='_authenticator']").val();
    };

    WorksheetManageResultsView.prototype.get_analyses_listing = function() {

      /*
       * Returns the root element of the analysis listing for results entry
       */
      var listing, selector;
      selector = "#analyses_form div.ajax-contents-table";
      listing = document.querySelector(selector);
      return listing;
    };

    WorksheetManageResultsView.prototype.reload_analyses_listing = function() {

      /*
       * Reloads the analyses listing for results entry
       */
      var event, listing;
      listing = this.get_analyses_listing();
      event = new Event("reload");
      return listing.dispatchEvent(event);
    };


    /* EVENT HANDLER */

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
        return bika.lims.SiteView.notify_in_panel(_p("Changes saved."), "succeed");
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(_t("Could not set the selected analyst"), "error");
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
        return this.reload_analyses_listing();
      }).fail(function() {
        return bika.lims.SiteView.notify_in_panel(_t("Unable to apply the selected instrument"), "error");
      });
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
            $("div.pb-ajax>div", overlay).addClass("container-fluid");
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
