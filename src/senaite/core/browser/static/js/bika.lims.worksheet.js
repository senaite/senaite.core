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
    return JSON.parse(value);
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
      message = _t("Only the analyses for which the selected instrument is allowed will be added automatically.");
      // actually just a notification, but lacking a proper css class here
      return senaite.core.controllers.SiteView.notify_in_panel(message, "error");
    }
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
    /* METHODS */
    this.ajax_submit = this.ajax_submit.bind(this);
    this.get_portal_url = this.get_portal_url.bind(this);
    this.get_base_url = this.get_base_url.bind(this);
    this.get_authenticator = this.get_authenticator.bind(this);
    this.get_analyses_listing = this.get_analyses_listing.bind(this);
    this.reload_analyses_listing = this.reload_analyses_listing.bind(this);
    /* EVENT HANDLER */
    this.on_analyst_change = this.on_analyst_change.bind(this);
    this.on_layout_change = this.on_layout_change.bind(this);
    this.on_instrument_change = this.on_instrument_change.bind(this);
    this.on_wideiterims_analyses_change = this.on_wideiterims_analyses_change.bind(this);
    this.on_wideiterims_interims_change = this.on_wideiterims_interims_change.bind(this);
    this.on_slot_remarks_click = this.on_slot_remarks_click.bind(this);
    this.on_wideinterims_apply_click = this.on_wideinterims_apply_click.bind(this);
  }

  load() {
    console.debug("WorksheetManageResultsView::load");
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
    console.debug("WorksheetManageResultsView::bind_eventhandler");
    // Analyst changed
    $("body").on("change", ".manage_results_header .analyst", this.on_analyst_change);
    // Layout changed
    $("body").on("change", "#resultslayout_form #resultslayout", this.on_layout_change);
    // Instrument changed
    $("body").on("change", ".manage_results_header .instrument", this.on_instrument_change);
    // Wide interims changed
    $("body").on("change", "#wideinterims_analyses", this.on_wideiterims_analyses_change);
    $("body").on("change", "#wideinterims_interims", this.on_wideiterims_interims_change);
    $("body").on("click", "#wideinterims_apply", this.on_wideinterims_apply_click);
    // Sample remarks icon in WS slot header
    return $("body").on("click", "img.slot-remarks", this.on_slot_remarks_click);
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
    url = url.split("?")[0];
    return url.replace("#", "");
  }

  get_authenticator() {
    /*
     * Get the authenticator value
     */
    return $("input[name='_authenticator']").val();
  }

  get_analyses_listing() {
    /*
     * Returns the root element of the analysis listing for results entry
     */
    var listing, selector;
    selector = "#analyses_form div.ajax-contents-table";
    listing = document.querySelector(selector);
    return listing;
  }

  reload_analyses_listing() {
    /*
     * Reloads the analyses listing for results entry
     */
    var event, listing;
    listing = this.get_analyses_listing();
    event = new Event("reload");
    return listing.dispatchEvent(event);
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
      return senaite.core.controllers.SiteView.notify_in_panel(_p("Changes saved."), "succeed");
    }).fail(function() {
      return senaite.core.controllers.SiteView.notify_in_panel(_t("Could not set the selected analyst"), "error");
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
      return this.reload_analyses_listing();
    }).fail(function() {
      return senaite.core.controllers.SiteView.notify_in_panel(_t("Unable to apply the selected instrument"), "error");
    });
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

  on_slot_remarks_click(event) {
    var el;
    /*
     * Eventhandler when the remarks icon was clicked
     */
    console.debug("°°° WorksheetManageResultsView::on_slot_remarks_click °°°");
    el = event.currentTarget;
    // https://jquerytools.github.io/documentation/overlay
    // https://github.com/plone/plone.app.jquerytools/blob/master/plone/app/jquerytools/browser/overlayhelpers.js
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
          // Remove editable elements
          $("h3", overlay).remove();
          $("textarea", overlay).remove();
          $("input", overlay).remove();
          // make the overlay draggable
          return overlay.draggable();
        },
        onLoad: function(event) {
          return $.mask.close();
        }
      }
    });
    // workaround un-understandable overlay api
    return $(el).click();
  }

  on_wideinterims_apply_click(event) {
    var $el, analysis, empty_only, interim, set_value, value;
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
    value = $("#wideinterims_value").val();
    // N.B.: Workaround to notify the ReactJS listing component about the changed
    // values
    set_value = function(input, value) {
      var evt, nativeInputValueSetter;
      // Manually select the checkbox of this row
      // https://github.com/senaite/senaite.core/issues/1202
      // https://stackoverflow.com/questions/23892547/what-is-the-best-way-to-trigger-onchange-event-in-react-js
      // TL;DR: React library overrides input value setter
      nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      nativeInputValueSetter.call(input, value);
      evt = new Event('input', {
        bubbles: true
      });
      return input.dispatchEvent(evt);
    };
    return $(`tr td input[column_key='${interim}']`).each(function(index, input) {
      if (empty_only) {
        if ($(this).val() === "" || $(this).val().match(/\d+/) === "0") {
          set_value(input, value);
        }
      } else {
        set_value(input, value);
      }
      return true;
    });
  }

};
