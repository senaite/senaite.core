### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.worksheet.coffee
###


class window.WorksheetFolderView
  ###
  * Controller class for Worksheets Folder
  ###

  load: =>
    console.debug "WorksheetFolderView::load"

    # bind the event handler to the elements
    @bind_eventhandler()


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "WorksheetFolderView::bind_eventhandler"

    # Template changed
    $("body").on "change", "select.template", @on_template_change

    # Instrument changed
    $("body").on "change", "select.instrument", @on_instrument_change


  ### METHODS ###

  get_template_instrument: () =>
    ###
     * TODO: Refactor to get the data directly from the server
     * Returns the JSON parsed value of the HTML element with the class
       `templateinstruments`
    ###
    console.debug "WorksheetFolderView::get_template_instruments"
    input = $("input.templateinstruments")
    value = input.val()
    return JSON.parse value


  select_instrument: (instrument_uid) =>
    ###
     * Select instrument by UID
    ###
    select = $(".instrument")
    option = select.find("option[value='#{instrument_uid}']")
    if option
      option.prop "selected", yes


  ### EVENT HANDLER ###

  on_template_change: (event) =>
    ###
     * Eventhandler for template change
    ###
    console.debug "°°° WorksheetFolderView::on_template_change °°°"

    # The select element for WS Template
    $el = $(event.currentTarget)

    # The option value is the worksheettemplate UID
    template_uid = $el.val()

    # Assigned instrument of this worksheet
    template_instrument = @get_template_instrument()

    # The UID of the assigned instrument in the template
    instrument_uid = template_instrument[template_uid]

    # Select the instrument from the selection
    @select_instrument instrument_uid


  on_instrument_change: (event) =>
    ###
     * Eventhandler for instrument change
    ###
    console.debug "°°° WorksheetFolderView::on_instrument_change °°°"

    # The select element for WS Instrument
    $el = $(event.currentTarget)

    # The option value is the nstrument UID
    instrument_uid = $el.val()

    if instrument_uid
      message = _t("Only the analyses for which the selected instrument is allowed will be added automatically.")
      # actually just a notification, but lacking a proper css class here
      bika.lims.SiteView.notify_in_panel message, "error"



class window.WorksheetManageResultsView
  ###
   * Controller class for Worksheet's manage results view
  ###

  load: =>
    console.debug "WorksheetManageResultsView::load"

    # bind the event handler to the elements
    @bind_eventhandler()

  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "WorksheetManageResultsView::bind_eventhandler"

    # Analyst changed
    $("body").on "change", ".manage_results_header .analyst", @on_analyst_change

    # Layout changed
    $("body").on "change", "#resultslayout_form #resultslayout", @on_layout_change

    # Instrument changed
    $("body").on "change", ".manage_results_header .instrument", @on_instrument_change

    # Wide interims changed
    $("body").on "change", "#wideinterims_analyses", @on_wideiterims_analyses_change
    $("body").on "change", "#wideinterims_interims", @on_wideiterims_interims_change
    $("body").on "click", "#wideinterims_apply", @on_wideinterims_apply_click

    # Sample remarks icon in WS slot header
    $("body").on "click", "img.slot-remarks", @on_slot_remarks_click

  ### METHODS ###

  ajax_submit: (options={}) =>
    ###
     * Ajax Submit with automatic event triggering and some sane defaults
    ###
    console.debug "°°° ajax_submit °°°"

    # some sane option defaults
    options.type ?= "POST"
    options.url ?= @get_base_url()
    options.context ?= this

    console.debug ">>> ajax_submit::options=", options

    $(this).trigger "ajax:submit:start"
    done = =>
        $(this).trigger "ajax:submit:end"
    return $.ajax(options).done done


  get_portal_url: =>
    ###
     * Return the portal url (calculated in code)
    ###
    url = $("input[name=portal_url]").val()
    return url or window.portal_url


  get_base_url: =>
    ###
     * Return the current base url
    ###
    url = window.location.href
    url = url.split("?")[0]
    return url.replace("#", "")


  get_authenticator: =>
    ###
     * Get the authenticator value
    ###
    return $("input[name='_authenticator']").val()


  get_analyses_listing: =>
    ###
     * Returns the root element of the analysis listing for results entry
    ###
    selector = "#analyses_form div.ajax-contents-table";
    listing = document.querySelector selector
    return listing


  reload_analyses_listing: () =>
    ###
     * Reloads the analyses listing for results entry
    ###
    listing = @get_analyses_listing()
    event = new Event "reload"
    listing.dispatchEvent event


  ### EVENT HANDLER ###

  on_analyst_change: (event) =>
    ###
     * Eventhandler when the analyst select changed
    ###
    console.debug "°°° WorksheetManageResultsView::on_analyst_change °°°"

    $el = $(event.currentTarget)
    analyst = $el.val()

    if analyst == ""
      return false

    base_url = @get_base_url()
    url = base_url.replace("/manage_results", "") + "/set_analyst"

    @ajax_submit
      url: url
      data:
        value: analyst
        _authenticator: @get_authenticator()
      dataType: "json"
    .done (data) ->
      bika.lims.SiteView.notify_in_panel _p("Changes saved."), "succeed"
    .fail () ->
        bika.lims.SiteView.notify_in_panel _t("Could not set the selected analyst"), "error"

  on_layout_change: (event) =>
    ###
     * Eventhandler when the analyst changed
    ###
    console.debug "°°° WorksheetManageResultsView::on_layout_change °°°"
    $el = $(event.currentTarget)

  on_instrument_change: (event) =>
    ###
     * Eventhandler when the instrument changed
    ###
    console.debug "°°° WorksheetManageResultsView::on_instrument_change °°°"

    $el = $(event.currentTarget)
    instrument_uid = $el.val()

    if instrument_uid == ""
      return false

    base_url = @get_base_url()
    url = base_url.replace("/manage_results", "") + "/set_instrument"

    @ajax_submit
      url: url
      data:
        value: instrument_uid
        _authenticator: @get_authenticator()
      dataType: "json"
    .done (data) ->
      @reload_analyses_listing()
    .fail () ->
        bika.lims.SiteView.notify_in_panel _t("Unable to apply the selected instrument"), "error"


  on_wideiterims_analyses_change: (event) =>
    ###
     * Eventhandler when the wide interims analysis selector changed
     *
     * Search all interim fields which begin with the selected category and fill
     *  the analyses interim fields to the selection
    ###
    console.debug "°°° WorksheetManageResultsView::on_wideiterims_analyses_change °°°"
    $el = $(event.currentTarget)

    # Empty the wideinterim analysis field
    $("#wideinterims_interims").html ""

    category = $el.val()
    $("input[id^='wideinterim_#{category}']").each (index, element) ->
      name = $(element).attr "name"
      keyword = $(element).attr "keyword"
      itemval = "<option value='#{keyword}'>#{name}</option>"
      $("#wideinterims_interims").append itemval


  on_wideiterims_interims_change: (event) =>
    ###
     * Eventhandler when the wide interims selector changed
    ###
    console.debug "°°° WorksheetManageResultsView::on_wideiterims_interims_change °°°"

    $el = $(event.currentTarget)
    analysis = $("#wideinterims_analyses").val()
    interim = $el.val()
    idinter = "#wideinterim_#{analysis}_#{interim}"
    $("#wideinterims_value").val $(idinter).val()


  on_slot_remarks_click: (event) =>
    ###
     * Eventhandler when the remarks icon was clicked
    ###
    console.debug "°°° WorksheetManageResultsView::on_slot_remarks_click °°°"
    el = event.currentTarget

    # https://jquerytools.github.io/documentation/overlay
    # https://github.com/plone/plone.app.jquerytools/blob/master/plone/app/jquerytools/browser/overlayhelpers.js
    $(el).prepOverlay
      subtype: "ajax"
      filter: "h1,div.remarks-widget"
      config:
        closeOnClick: yes
        closeOnEsc: yes
        onBeforeLoad: (event) ->
          overlay = this.getOverlay()
          $("div.pb-ajax>div", overlay).addClass("container-fluid")
          # Remove editable elements
          $("h3", overlay).remove()
          $("textarea", overlay).remove()
          $("input", overlay).remove()
          # make the overlay draggable
          overlay.draggable()
        onLoad: (event) ->
          $.mask.close()

    # workaround un-understandable overlay api
    $(el).click()


  on_wideinterims_apply_click: (event) =>
    ###
     * Eventhandler when the wide interim apply button was clicked
    ###
    console.debug "°°° WorksheetManageResultsView::on_wideinterims_apply_click °°°"

    # prevent form submission
    event.preventDefault()
    $el = $(event.currentTarget)

    analysis = $("#wideinterims_analyses").val()
    interim = $("#wideinterims_interims").val()
    empty_only = $("#wideinterims_empty").is(":checked")
    value = $("#wideinterims_value").val()

    # N.B.: Workaround to notify the ReactJS listing component about the changed
    # values
    set_value = (input, value) ->
      # Manually select the checkbox of this row
      # https://github.com/senaite/senaite.core/issues/1202
      # https://stackoverflow.com/questions/23892547/what-is-the-best-way-to-trigger-onchange-event-in-react-js
      # TL;DR: React library overrides input value setter
      nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set
      nativeInputValueSetter.call(input, value)
      evt = new Event('input', {bubbles: true})
      input.dispatchEvent(evt)

    $("tr td input[column_key='#{interim}']").each (index, input) ->
      if empty_only
        if $(this).val() == "" or $(this).val().match(/\d+/) == "0"
          set_value input, value
      else
        set_value input, value
      return true
