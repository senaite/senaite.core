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
    return $.parseJSON value


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
      message = _("Only the analyses for which the selected instrument is allowed will be added automatically.")
      # actually just a notification, but lacking a proper css class here
      bika.lims.SiteView.notify_in_panel message, "error"


class window.WorksheetAddQCAnalysesView
  ###
   * Controller class for Worksheet's add blank/control views
  ###

  load: =>
    console.debug "WorksheetAddQCAnalysesView::load"

    # bind the event handler to the elements
    @bind_eventhandler()

    # initially load the references
    @load_controls()


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "WorksheetAddQCAnalysesView::bind_eventhandler"

    # Service checkbox clicked
    $("body").on "click", "#worksheet_services input[id*='_cb_']", @on_service_click

    # click a Reference Sample in add_control or add_blank
    $("body").on "click", "#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr", @on_referencesample_row_click


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


  get_base_url: =>
    ###
     * Return the current base url
    ###
    url = window.location.href
    return url.split('?')[0]


  get_authenticator: =>
    ###
     * Get the authenticator value
    ###
    return $("input[name='_authenticator']").val()


  get_selected_services: =>
    ###
     * Returns a list of selected service uids
    ###

    $table = $("table.bika-listing-table")

    services = []
    $("input:checked", $table).each (index, element) ->
      services.push element.value
    return services


  get_control_type: =>
    ###
     * Returns the control type
    ###
    control_type = "b"
    if window.location.href.search("add_control") > -1
      control_type = "c"
    return control_type


  get_postion: =>
    ###
     * Returns the postition
    ###
    position = $("#position").val()
    return position or "new"


  load_controls: =>
    ###
     * Load the controls
    ###
    base_url = @get_base_url()
    base_url = base_url.replace("/add_blank", "").replace("/add_control", "")
    url = "#{base_url}/getWorksheetReferences"

    element = $("#worksheet_add_references")
    if element.length == 0
      console.warn "Element with id='#worksheet_add_references' missing!"
      return

    @ajax_submit
      url: url
      data:
        service_uids: @get_selected_services().join ","
        control_type: @get_control_type()
        _authenticator: @get_authenticator()
    .done (data) ->
      element.html data


  ### EVENT HANDLER ###

  on_service_click: (event) =>
    ###
     * Eventhandler when a service checkbox was clicked
    ###
    console.debug "°°° WorksheetAddQCAnalysesView::on_category_change °°°"
    @load_controls()


  on_referencesample_row_click: (event) =>
    ###
     * Eventhandler for a click on the loaded referencesample listing
     *
     * A reference sample for the service need to be added via
     * Setup -> Supplier -> Referene Samples
    ###
    console.debug "°°° WorksheetAddQCAnalysesView::on_referencesample_row_click °°°"

    # The clicked element is a row from the referencesample listing
    $el = $(event.currentTarget)
    uid = $el.attr "uid"

    # we want to submit to the worksheet.py/add_control or add_blank views.
    $form = $el.parents("form")

    control_type = @get_control_type()
    action = "add_blank"
    if control_type == "c"
      action = "add_control"

    $form.attr "action", action

    selected_services = @get_selected_services().join ","
    $form.append "<input type='hidden' value='#{selected_services}' name='selected_service_uids'/>"

    # tell the form handler which reference UID was clicked
    $form.append "<input type='hidden' value='#{uid}' name='reference_uid'/>"
    # add the position dropdown's value to the form before submitting.
    $form.append "<input type='hidden' value='#{@get_postion()}' name='position'/>"
    # submit the referencesample listing form
    $form.submit()



class window.WorksheetAddDuplicateAnalysesView
  ###
   * Controller class for Worksheet's add blank/control views
  ###

  load: =>
    console.debug "WorksheetAddDuplicateAnalysesView::load"

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
    console.debug "WorksheetAddDuplicateAnalysesView::bind_eventhandler"

    # Service checkbox clicked
    $("body").on "click", "#worksheet_add_duplicate_ars .bika-listing-table tbody.item-listing-tbody tr", @on_duplicate_row_click


  ### METHODS ###

  get_postion: =>
    ###
     * Returns the postition
    ###
    position = $("#position").val()
    return position or "new"


  ### EVENT HANDLER ###

  on_duplicate_row_click: (event) =>
    ###
     * Eventhandler for a click on a row of the loaded dduplicate listing
    ###
    console.debug "°°° WorksheetAddDuplicateAnalysesView::on_duplicate_row_click °°°"

    $el = $(event.currentTarget)
    uid = $el.attr "uid"

    # we want to submit to the worksheet.py/add_duplicate view.
    $form = $el.parents("form")
    $form.attr "action", "add_duplicate"

    # add the position dropdown's value to the form before submitting.
    $form.append "<input type='hidden' value='#{uid}' name='ar_uid'/>"
    $form.append "<input type='hidden' value='#{@get_postion()}' name='position'/>"
    $form.submit()



class window.WorksheetManageResultsView
  ###
   * Controller class for Worksheet's manage results view
  ###

  load: =>
    console.debug "WorksheetManageResultsView::load"

    # load translations
    jarn.i18n.loadCatalog "senaite.core"
    @_ = window.jarn.i18n.MessageFactory("senaite.core")
    @_pmf = window.jarn.i18n.MessageFactory('plone')

    # bind the event handler to the elements
    @bind_eventhandler()

    # method instrument constraints
    @constraints = null

    # initialize
    @init_instruments_and_methods()

    # dev only
    window.ws = @


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

    # Method changed
    $("body").on "change", "table.bika-listing-table select.listing_select_entry[field='Method']", @on_method_change

    # Analysis instrument focused
    $("body").on "focus", "table.bika-listing-table select.listing_select_entry[field='Instrument']", @on_analysis_instrument_focus

    # Analysis instrument changed
    $("body").on "change", "table.bika-listing-table select.listing_select_entry[field='Instrument']", @on_analysis_instrument_change

    # Remarks balloon clicked
    $("body").on "click", "a.add-remark", @on_remarks_balloon_clicked

    # Wide interims changed
    $("body").on "change", "#wideinterims_analyses", @on_wideiterims_analyses_change
    $("body").on "change", "#wideinterims_interims", @on_wideiterims_interims_change
    $("body").on "click", "#wideinterims_apply", @on_wideinterims_apply_click

    $("body").on "click", "img.slot-remarks", @on_slot_remarks_click

    ### internal events ###

    # handle value changes in the form
    $(this).on "constraints:loaded", @on_constraints_loaded


  init_instruments_and_methods: =>
    ###
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
    ###

    analysis_uids = @get_analysis_uids()

    @ajax_submit
      url: "#{@get_portal_url()}/get_method_instrument_constraints"
      data:
        _authenticator: @get_authenticator
        uids: $.toJSON analysis_uids
      dataType: "json"
    .done (data) ->
      @constraints = data
      $(@).trigger "constraints:loaded", data


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
    return url.split('?')[0]


  get_authenticator: =>
    ###
     * Get the authenticator value
    ###
    return $("input[name='_authenticator']").val()


  get_analysis_uids: =>
    ###
     * Returns a list of analysis UIDs
    ###
    analysis_uids = []
    data = $.parseJSON $("#item_data").val()
    $.each data, (uid, value) ->
      analysis_uids.push uid
    return analysis_uids

  get_method_by_analysis_uid: (analysis_uid) =>
    ###
     * Return the method UID of the analysis identified by analysis_uid
    ###
    $method_field = $("select.listing_select_entry[field='Method'][uid='#{analysis_uid}']")
    method_uid = $method_field.val()
    return method_uid or ""


   is_instrument_allowed: (instrument_uid) =>
     ###
      * Check if the Instrument is allowed to appear in Instrument list of Analysis.
      *
      * Returns true if multiple use of an Instrument is enabled for assigned
      * Worksheet Template or UID is not in selected Instruments
      *
      * @param {uid} instrument_uid - UID of Instrument.
     ###
     allowed = yes
     multiple_enabled = $("#instrument_multiple_use").attr("value")
     if multiple_enabled isnt "True"
       i_selectors = $("select.listing_select_entry[field='Instrument']")
       $.each i_selectors, (index, element) ->
         if element.value == instrument_uid
           allowed = no
     return allowed


  load_analysis_method_constraint: (analysis_uid, method_uid) =>
    ###
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
    ###

    console.debug "WorksheetManageResultsView::load_analysis_method_constraint:analysis_uid=#{analysis_uid} method_uid=#{method_uid}"

    # reference to this object for $.each calls
    me = @

    if not method_uid
      method_uid = @get_method_by_analysis_uid analysis_uid

    analysis_constraints = @constraints[analysis_uid]

    if not analysis_constraints
      return

    method_constraints = analysis_constraints[method_uid]

    if not method_constraints
      return

    if method_constraints.length < 7
      return

    # method selector
    m_selector = $("select.listing_select_entry[field='Method'][uid='#{analysis_uid}']")
    # instrument selector
    i_selector = $("select.listing_select_entry[field='Instrument'][uid='#{analysis_uid}']")

    # Remove None option in method selector
    $(m_selector).find('option[value=""]').remove()

    if method_constraints[1] == 1
      $(m_selector).prepend "<option value=''>#{_('Not defined')}</option>"

    # Select the method
    $(m_selector).val method_uid

    # Method selector visible?
    # 0: no, 1: yes, 2: label, 3: readonly
    $(m_selector).prop "disabled", no

    $(".method-label[uid='#{analysis_uid}']").remove()
    if method_constraints[0] == 0
      $(m_selector).hide()
    else if method_constraints[0] == 1
      $(m_selector).show()
    else if method_constraints[0] == 2
      # XXX length check of an object??
      if analysis_constraints.length > 1
        $(m_selector).hide()
        method_name = $(m_selector).find("option[value='#{method_uid}']").innerHtml()
        $(m_selector).after "<span class='method-label' uid='#{analysis_uid}' href='#'>#{method_name}</span>"
    else if method_constraints[0] == 3
      $(m_selector).show()

    # We are going to reload the instrument list.
    # Enable all disabled options from other Instrument lists which has the same
    # value as old value of this instrument selectbox.
    ins_old_val = $(i_selector).val()
    if ins_old_val and ins_old_val != ''
      $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='#{ins_old_val}'] option[value='#{ins_old_val}']").prop "disabled", no

    # Populate instruments list
    $(i_selector).find("option").remove()
    if method_constraints[7]
      $.each method_constraints[7], (key, value) ->
        if me.is_instrument_allowed(key)
          $(i_selector).append "<option value='#{key}'>#{value}</option>"
        else
          $(i_selector).append "<option value='#{key}' disabled='disabled'>#{value}</option>"

    # None option in instrument selector?
    if method_constraints[3] == 1
      $(i_selector).prepend "<option selected='selected' value=''>#{_('None')}</option>"

    # Select the default instrument
    if me.is_instrument_allowed method_constraints[4]
      $(i_selector).val method_constraints[4]
      # Disable this Instrument in the other Instrument SelectBoxes
      $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='#{method_constraints[4]}'] option[value='#{method_constraints[4]}']").prop "disabled", yes

    # Instrument selector visible?
    if method_constraints[2] == 0
      $(i_selector).hide()
    else if method_constraints[2] == 1
      $(i_selector).show()

    # Allow to edit results?
    if method_constraints[5] == 0
      $(".interim input[uid='#{analysis_uid}']").val ""
      $("input[field='Result'][uid='#{analysis_uid}']").val ""
      $(".interim input[uid='#{analysis_uid}']").prop "disabled", yes
      $("input[field='Result'][uid='#{analysis_uid}']").prop "disabled", yes
    else if method_constraints[5] == 1
      $(".interim input[uid='#{analysis_uid}']").prop "disabled", no
      $("input[field='Result'][uid='#{analysis_uid}']").prop "disabled", no

    # Info/Warn message?
    $(".alert-instruments-invalid[uid='#{analysis_uid}']").remove()
    if method_constraints[6] and method_constraints[6] != ""
      $(i_selector).after "<img uid='#{analysis_uid}' class='alert-instruments-invalid' src='#{@get_portal_url()}/++resource++bika.lims.images/warning.png' title='#{method_constraints[6]}'>"
    $(".amconstr[uid='#{analysis_uid}']").remove()


  ### EVENT HANDLER ###

  on_constraints_loaded: (event) =>
    ###
     * Eventhandler when the instrument and method constraints were loaded from the server
    ###
    console.debug "°°° WorksheetManageResultsView::on_constraints_loaded °°°"

    me = @
    $.each @get_analysis_uids(), (index, uid) ->
      me.load_analysis_method_constraint uid, null


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
      bika.lims.SiteView.notify_in_panel @_pmf("Changes saved."), "succeed"
    .fail () ->
        bika.lims.SiteView.notify_in_panel @_("Could not set the selected analyst"), "error"


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
      bika.lims.SiteView.notify_in_panel @_pmf("Changes saved."), "succeed"
      # Set the selected instrument to all the analyses which that can be done
      # using that instrument. The rest of of the instrument picklist will not
      # be changed
      $("select.listing_select_entry[field='Instrument'] option[value='#{instrument_uid}']").parent().find("option[value='#{instrument_uid}']").prop "selected", no
      $("select.listing_select_entry[field='Instrument'] option[value='#{instrument_uid}']").prop "selected", yes
    .fail () ->
        bika.lims.SiteView.notify_in_panel @_("Unable to apply the selected instrument"), "error"


  on_method_change: (event) =>
    ###
     * Eventhandler when the method changed
     *
    ###
    console.debug "°°° WorksheetManageResultsView::on_method_change °°°"
    $el = $(event.currentTarget)

    analysis_uid = $el.attr "uid"
    method_uid = $el.val()

    # Change the instruments to be shown for an analysis when the method selected changes
    @load_analysis_method_constraint analysis_uid, method_uid


  on_analysis_instrument_focus: (event) =>
    ###
     * Eventhandler when the instrument of an analysis is focused
     *
     * Only needed to remember the last value
    ###
    console.debug "°°° WorksheetManageResultsView::on_analysis_instrument_focus °°°"

    $el = $(event.currentTarget)
    @previous_instrument = $el.val()
    console.info @previous_instrument


  on_analysis_instrument_change: (event) =>
    ###
     * Eventhandler when the instrument of an analysis changed
     *
     * If a new instrument is chosen for the analysis, disable this Instrument
     * for the other analyses. Also, remove the restriction of previous
     * Instrument of this analysis to be chosen in the other analyses.
    ###
    console.debug "°°° WorksheetManageResultsView::on_analysis_instrument_change °°°"
    $el = $(event.currentTarget)

    analysis_uid = $el.attr "uid"
    instrument_uid = $el.val()

    # Disable New Instrument for rest of the analyses
    $("table.bika-listing-table select.listing_select_entry[field='Instrument'][value!='#{instrument_uid}'] option[value='#{instrument_uid}']").prop "disabled", yes

    # Enable previous Instrument everywhere
    $("table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='#{@previous_instrument}']").prop "disabled", no

    # Enable 'None' option as well.
    $("table.bika-listing-table select.listing_select_entry[field='Instrument'] option[value='']").prop "disabled", no


  on_remarks_balloon_clicked: (event) =>
    ###
     * Eventhandler when the remarks balloon was clicked
    ###
    console.debug "°°° WorksheetManageResultsView::on_remarks_balloon_clicked °°°"
    $el = $(event.currentTarget)

    event.preventDefault()
    remarks = $el.closest("tr").next("tr").find("td.remarks")
    $(remarks).find("div.remarks-placeholder").toggle()


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
          $("div.pb-ajax>div", overlay).addClass("container")
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
