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
