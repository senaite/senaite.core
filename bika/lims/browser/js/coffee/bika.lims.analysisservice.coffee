### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
###


class window.AnalysisServiceEditView

  load: =>
    console.debug "AnalysisServiceEditView::load"

    # load translations
    jarn.i18n.loadCatalog "bika"
    @_ = window.jarn.i18n.MessageFactory "bika"

    # JSONAPI v1 access
    @read = window.bika.lims.jsonapi_read

    # Interim values defined in default Calculation
    @calculation_interims = []

    # Interim values defined by the user (not part of a calculation)
    @manual_interims = []

    # bind the event handler to the elements
    @bind_eventhandler()

    # Initialize default calculation
    @init_default_calculation()

    # Dev only
    window.asv = @


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
    ###
    console.debug "AnalysisServiceEditView::bind_eventhandler"

    ### METHODS TAB ###

    # The "Default Method" select changed
    $("body").on "change", "#archetypes-fieldname-Method #Method", @on_default_method_change

    # The "Methods" multiselect changed
    $("body").on "change", "#archetypes-fieldname-Methods #Methods", @on_methods_change

    # The "Default Instrument" selector changed
    $("body").on "change", "#archetypes-fieldname-Instrument #Instrument", @on_default_instrument_change

    # The "Instruments" multiselect changed
    $("body").on "change", "#archetypes-fieldname-Instruments #Instruments", @on_instruments_change

    # The "Instrument assignment is allowed" checkbox changed
    $("body").on "change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", @on_instrument_assignment_allowed_change

    # The "Instrument assignment is not required" checkbox changed
    $("body").on "change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", @on_manual_entry_of_results_change

    # The "Use the Default Calculation of Method" checkbox changed
    $("body").on "change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", @on_use_default_calculation_change

    # The "Calculation" selector changed
    $("body").on "change", "#archetypes-fieldname-Calculation #Calculation", @on_calculation_change

    ### ANALYSIS TAB ###

    # The "Display a Detection Limit selector" checkbox changed
    $("body").on "change", "#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector", @on_display_detection_limit_selector_change


  init_default_calculation: =>
    ###
     * 1. Check if field "Use the Default Calculation of Method" is checked
     * 2. Fetch the selected calculation
     * 3. Replace the calculation select box with the calculations
    ###
    me = this

    calculation_uid = @get_default_calculation()

    # nothing to do if we do not have a calculation uid set
    if not @is_uid calculation_uid
      return

    options =
      catalog_name: "bika_setup_catalog"
      UID: calculation_uid

    @read options, (data) ->
      if data.objects.length isnt 1
        console.warn "No Calculation found for UID '#{calculation_uid}'"
        return

      # Calculation data
      calculation = data.objects[0]

      # limit the calculation select box to this calculation
      field = $("#archetypes-fieldname-Calculation #Calculation")
      field.empty()
      me.add_select_option field, calculation.Title, calculation.UID

      # process interims of this calculation
      calculation_interims = []
      $.each calculation.InterimFields, (index, value) ->
        # we use the same format as expected by `set_interims`
        calculation_interims.push([
          value.keyword
          value.title
          value.value
          value.unit
          false  # Hidden (missing here)
          false  # Apply wide (missing here)
        ])
      # remember the interims of this calculation
      me.calculation_interims = calculation_interims

      # Calculate which interims were manually set (not part of the calculation)
      manual_interims = []
      calculation_interim_keys = calculation_interims.map (v) -> return v[0]
      $.each me.get_interims(), (index, value) ->
        if value[0] not in calculation_interim_keys
          manual_interims.push value
      # remember the manual set interims of this AS
      me.manual_interims = manual_interims


  ### INTERIM FIELD HANDLING ###

  get_interims: =>
    ###
     * Extract the interim field values as a list of lists
     * [['MG', 'Magnesium', 'g' ...], [], ...]
    ###
    field = $("#archetypes-fieldname-InterimFields")
    rows = field.find("tr.records_row_InterimFields")

    interims = []
    $.each rows, (index, row) ->
      values = []
      $.each $(row).find("td input"), (index, input) ->
        value = input.value
        if input.type is "checkbox"
          value = input.checked
        values.push value
      # Only rows with Keyword set
      if values and values[0] isnt ""
        interims.push values
    return interims


  set_interims: (values) =>
    ###
     * Set the interim field values
     * Note: This method takes the same input format as returned from get_interims
    ###

    # empty all interims
    @flush_interims()
    field = $("#archetypes-fieldname-InterimFields")
    more_button = field.find("#InterimFields_more")

    $.each values, (index, value) ->
      last_row = field.find("tr.records_row_InterimFields").last()
      more_button.click()
      inputs = last_row.find "input"

      $.each value, (i, v) ->
        input = inputs[i]
        if input.type is "checkbox"
          input.checked = v
        else
          input.value = v


  flush_interims: =>
    ###
     * Flush interim field
    ###
    field = $("#archetypes-fieldname-InterimFields")
    more_button = field.find("#InterimFields_more")
    more_button.click()
    rows = field.find("tr.records_row_InterimFields")
    rows.not(":last").remove()


  ### LOADERS ###

  load_interims: (calculation_uid) =>
    ###
     * Load interims assigned to the calculation
    ###
    if not @is_uid calculation_uid
      console.warn "Calculation UID '#{calculation_uid}' is invalid"
      return

    options =
      catalog_name: "bika_setup_catalog"
      UID: calculation_uid
    window.bika.lims.jsonapi_read options, (data) ->
      interims = data?.objects?[0].InterimFields


  load_instrument_methods: (instrument_uid) =>
    ###
     * Load methods assigned to the instrument
    ###
    if not @is_uid instrument_uid
      console.warn "Instrument UID '#{instrument_uid}' is invalid"
      return

    field = $('#archetypes-fieldname-Method #Method')
    field.empty()
    options =
      url: @get_portal_url() + "/get_instrument_methods"
      data:
        uid: instrument_uid
    @ajax_submit options
    .done (data) ->
      $.each data.methods, (index, item) ->
        option = "<option value='#{item.uid}'>#{item.title}</option>"
        field.append option
      if field.length == 0
        console.warn "Instrument with UID '#{instrument_uid}' has no methods assigned"
        @add_select_option field, ""


  load_available_calculations: =>
    ###
     * Load all available calculations to the calculation select box
    ###
    field = $("#archetypes-fieldname-Calculation #Calculation")
    field.empty()
    options =
      url: @get_portal_url() + "/get_available_calculations"
    @ajax_submit options
    .done (data) ->
      $.each data, (index, item) ->
        option = "<option value='#{item.uid}'>#{item.title}</option>"
        field.append option
      if field.length == 0
        @add_select_option field, ""


  load_method_calculation: (method_uid) =>
    ###
     * Load calculations for the given method UID
    ###

    if not @is_uid method_uid
      console.warn "Method UID '#{method_uid}' is invalid"
      return

    field = $("#archetypes-fieldname-Calculation #Calculation")
    field.empty()

    options =
      url: @get_portal_url() + "/get_method_calculation"
      data:
        uid: method_uid

    # Fetch the assigned calculations of the method
    @ajax_submit options
    .done (data) ->
      if not $.isEmptyObject data
        option = "<option value='#{data.uid}'>#{data.title}</option>"
        field.append option
      else
        @add_select_option field, ""


  ### METHODS ###

  ajax_submit: (options) =>
    ###
     * Ajax Submit with automatic event triggering and some sane defaults
    ###
    console.debug "°°° ajax_submit °°°"

    # some sane option defaults
    options ?= {}
    options.type ?= "POST"
    options.url ?= @get_portal_url()
    options.context ?= this
    options.dataType ?= "json"
    options.data ?= {}
    options.data._authenticator ?= $("input[name='_authenticator']").val()

    console.debug ">>> ajax_submit::options=", options

    $(this).trigger "ajax:submit:start"
    done = =>
        $(this).trigger "ajax:submit:end"
    return $.ajax(options).done done


  get_portal_url: =>
    ###
     * Return the portal url
    ###
    return window.portal_url


  is_uid: (str) =>
    ###
     * Validate valid URL
    ###
    if typeof str isnt "string"
      return no
    match = str.match /[a-z0-9]{32}/
    return match isnt null


  toggle_visibility_methods_field: (toggle) =>
    ###
     * This method toggles the visibility of the "Methods" field
    ###
    field = $("#archetypes-fieldname-Methods")
    if toggle is undefined
      field.fadeToggle "fast"
    else if toggle is yes
      field.fadeIn "fast"
    else
      field.fadeOut "fast"
    return field


  toggle_instrument_entry_of_results_checkbox: (toggle) =>
    ###
     * This method toggles the "Instrument assignment is allowed" checkbox
    ###
    field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults")
    if toggle is undefined
      toggle = not field.prop "checked"
    field.prop "checked", toggle
    return field


  add_select_option: (select, name, value) =>
    ###
     * Adds an option to the select
    ###

    # empty option
    if value is ""
      name = "None"
    option = "<option value='#{value}'>#{@_(name)}</option>"
    return $(select).append option


  ### ELEMENT HANDLING ###

  use_default_calculation_of_method: =>
    ###
     * Retrun the value of the "Use the Default Calculation of Method" checkbox
    ###
    field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation")
    return field.is(":checked")


  get_default_calculation: =>
    ###
     * Get the UID of the selected default calculation
    ###
    field = $("#archetypes-fieldname-Calculation #Calculation")
    return field.val()


  ### EVENT HANDLER ###

  on_default_method_change: (event) =>
    ###
     * Eventhandler when the "Default Method" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_method_change °°°"


  on_methods_change: (event) =>
    ###
     * Eventhandler when the "Methods" multiselect changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_methods_change °°°"


  on_instruments_change: (event) =>
    ###
     * Eventhandler when the "Instruments" multiselect changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instruments_change °°°"


  on_default_instrument_change: (event) =>
    ###
     * Eventhandler when the "Default Instrument" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_instrument_change °°°"


  on_instrument_assignment_allowed_change: (event) =>
    ###
     * Eventhandler when the "Instrument assignment is allowed" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°"


  on_manual_entry_of_results_change: (event) =>
    ###
     * Eventhandler when the "Instrument assignment is not required" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°"


  on_use_default_calculation_change: (event) =>
    ###
     * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_use_default_calculation_change °°°"


  on_calculation_change: (event) =>
    ###
     * Eventhandler when the "Calculation" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_calculation_change °°°"


  on_display_detection_limit_selector_change: (event) =>
    ###
     * Eventhandler when the "Display a Detection Limit selector" checkbox changed
     *
     * This checkbox is located on the "Analysis" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°"
