/**
 * Worksheet Folder View Controller
 *
 * This controller is loaded for the worksheets folder, e.g `/senaite/worksheets`.
 */
window.WorksheetFolderView = class WorksheetFolderView {
  constructor() {
    this.load = this.load.bind(this);
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.get_template_instrument = this.get_template_instrument.bind(this);
    this.select_instrument = this.select_instrument.bind(this);
    this.on_template_change = this.on_template_change.bind(this);
    this.on_instrument_change = this.on_instrument_change.bind(this);
  }

  load() {
    console.debug("WorksheetFolderView::load");
    this.bind_eventhandler();
  }

  bind_eventhandler() {
    console.debug("WorksheetFolderView::bind_eventhandler");
    $(document).on("change", "select.template", this.on_template_change);
    $(document).on("change", "select.instrument", this.on_instrument_change);
  }

  get_template_instrument() {
    const value = $("input.templateinstruments").val();
    return JSON.parse(value);
  }

  select_instrument(instrument_uid) {
    const $select = $(".instrument");
    const exists = $select.find(`option[value='${instrument_uid}']`).length > 0;
    if (exists) {
      $select.val(instrument_uid);
      $select.selectpicker("refresh");
    }
  }

  on_template_change(event) {
    const template_uid = $(event.currentTarget).val();
    const template_instrument = this.get_template_instrument();
    const instrument_uid = template_instrument[template_uid];
    this.select_instrument(instrument_uid);
  }

  on_instrument_change(event) {
    const instrument_uid = $(event.currentTarget).val();
    if (instrument_uid) {
      const message = _t("Only the analyses for which the selected instrument is allowed will be added automatically.");
      senaite.core.controllers.SiteView.notify_in_panel(message, "error");
    }
  }
}


/**
 * Worksheet Manage Results View Controller
 *
 * This controller is loaded for single worksheets, e.g `/senaite/worksheets/WS-001`.
 */
window.WorksheetManageResultsView = class WorksheetManageResultsView {
  constructor() {
    this.load = this.load.bind(this);
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.ajax_submit = this.ajax_submit.bind(this);
    this.get_portal_url = this.get_portal_url.bind(this);
    this.get_base_url = this.get_base_url.bind(this);
    this.get_authenticator = this.get_authenticator.bind(this);
    this.get_analyses_listing = this.get_analyses_listing.bind(this);
    this.reload_analyses_listing = this.reload_analyses_listing.bind(this);
    this.on_analyst_change = this.on_analyst_change.bind(this);
    this.on_instrument_change = this.on_instrument_change.bind(this);
    this.on_wideiterims_analyses_change = this.on_wideiterims_analyses_change.bind(this);
    this.on_wideiterims_interims_change = this.on_wideiterims_interims_change.bind(this);
    this.on_slot_remarks_click = this.on_slot_remarks_click.bind(this);
    this.on_wideinterims_apply_click = this.on_wideinterims_apply_click.bind(this);
  }

  load() {
    console.debug("WorksheetManageResultsView::load");
    this.bind_eventhandler();
  }

  bind_eventhandler() {
    $(document).on("change", ".manage_results_header .analyst", this.on_analyst_change);
    $(document).on("change", ".manage_results_header .instrument", this.on_instrument_change);
    $(document).on("change", "#wideinterims_analyses", this.on_wideiterims_analyses_change);
    $(document).on("change", "#wideinterims_interims", this.on_wideiterims_interims_change);
    $(document).on("click", "#wideinterims_apply", this.on_wideinterims_apply_click);
    $(document).on("click", "img.slot-remarks", this.on_slot_remarks_click);
  }

  ajax_submit(options = {}) {
    options.type = options.type || "POST";
    options.url = options.url || this.get_base_url();
    options.context = this;
    $(this).trigger("ajax:submit:start");
    return $.ajax(options).done(() => $(this).trigger("ajax:submit:end"));
  }

  get_portal_url() {
    return $("input[name='portal_url']").val() || window.portal_url;
  }

  get_base_url() {
    return window.location.href.split("?")[0].replace("#", "");
  }

  get_authenticator() {
    return $("input[name='_authenticator']").val();
  }

  get_analyses_listing() {
    return document.querySelector("#analyses_form div.ajax-contents-table");
  }

  reload_analyses_listing() {
    const listing = this.get_analyses_listing();
    if (listing) listing.dispatchEvent(new Event("reload"));
  }

  on_analyst_change(event) {
    const analyst = $(event.currentTarget).val();
    if (!analyst) return;
    const url = `${this.get_base_url().replace("/manage_results", "")}/set_analyst`;
    this.ajax_submit({
      url,
      data: {
        value: analyst,
        _authenticator: this.get_authenticator()
      },
      dataType: "json"
    }).done(() => {
      senaite.core.controllers.SiteView.notify_in_panel(_p("Changes saved."), "succeed");
    }).fail(() => {
      senaite.core.controllers.SiteView.notify_in_panel(_t("Could not set the selected analyst"), "error");
    });
  }

  on_instrument_change(event) {
    const instrument_uid = $(event.currentTarget).val();
    if (!instrument_uid) return;
    const url = `${this.get_base_url().replace("/manage_results", "")}/set_instrument`;
    this.ajax_submit({
      url,
      data: {
        value: instrument_uid,
        _authenticator: this.get_authenticator()
      },
      dataType: "json"
    }).done(() => {
      this.reload_analyses_listing();
    }).fail(() => {
      senaite.core.controllers.SiteView.notify_in_panel(_t("Unable to apply the selected instrument"), "error");
    });
  }

  on_wideiterims_analyses_change(event) {
    const category = $(event.currentTarget).val();
    const $interims = $("#wideinterims_interims").empty();
    $(`input[id^='wideinterim_${category}']`).each(function () {
      const keyword = $(this).attr("keyword");
      const name = $(this).attr("name");
      $interims.append(`<option value='${keyword}'>${name}</option>`);
    });
  }

  on_wideiterims_interims_change(event) {
    const analysis = $("#wideinterims_analyses").val();
    const interim = $(event.currentTarget).val();
    const idinter = `#wideinterim_${analysis}_${interim}`;
    $("#wideinterims_value").val($(idinter).val());
  }

  on_slot_remarks_click(event) {
    const el = event.currentTarget;
    $(el).prepOverlay({
      subtype: "ajax",
      filter: "h1,div.remarks-widget",
      config: {
        closeOnClick: true,
        closeOnEsc: true,
        onBeforeLoad: function () {
          const overlay = this.getOverlay();
          $("div.pb-ajax>div", overlay).addClass("container-fluid");
          $("h3, textarea, input", overlay).remove();
          overlay.draggable();
        },
        onLoad: () => $.mask.close()
      }
    });
    $(el).click();
  }

  on_wideinterims_apply_click(event) {
    event.preventDefault();
    const analysis = $("#wideinterims_analyses").val();
    const interim = $("#wideinterims_interims").val();
    const value = $("#wideinterims_value").val();
    const empty_only = $("#wideinterims_empty").is(":checked");
    const set_value = (input, value) => {
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
      nativeInputValueSetter.call(input, value);
      input.dispatchEvent(new Event("input", { bubbles: true }));
    };
    $(`tr td input[column_key='${interim}']`).each(function () {
      if (empty_only) {
        const val = $(this).val();
        if (!val || val === "0") {
          set_value(this, value);
        }
      } else {
        set_value(this, value);
      }
    });
  }
}
