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

    # Interim values defined by the user (not part of a calculation)
    @manual_interims = []

    # bind the event handler to the elements
    @bind_eventhandler()

    # Initialize default calculation
    @init_interims()

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


  init_interims: =>
    ###
     * 1. Check if field "Use the Default Calculation of Method" is checked
     * 2. Fetch the selected calculation
     * 3. Replace the calculation select box with the calculations
     * 4. Separate manual set interims from calculation interims
    ###
    me = this

    @load_calculation @get_calculation()
    .done (calculation) ->
      # set the calculation field
      @set_calculation calculation

      # interims of this calculation
      calculation_interims = calculation.InterimFields or []

      # extract the keys of the calculation interims
      calculation_interim_keys = calculation_interims.map (v) -> return v.keyword

      # separate manual interims from calculation interims
      manual_interims = []
      $.each @get_interims(), (index, value) ->
        if value.keyword not in calculation_interim_keys
          manual_interims.push value

      # remember the manual set interims of this AS
      # -> they are kept on calculation change
      @manual_interims = manual_interims


  ### FIELD GETTERS/SETTERS ###

  get_calculation: =>
    ###
     * Get the UID of the selected default calculation
    ###
    field = $("#archetypes-fieldname-Calculation #Calculation")
    return field.val()


  set_calculation: (calculation, flush=yes) =>
    ###
     * Set the calculation field with the given ()JSON calculation data
    ###

    # create a copy of the calculation
    calculation = $.extend {}, calculation

    field = $("#archetypes-fieldname-Calculation #Calculation")

    # empty the field first
    if flush
      field.empty()

    # XXX: Workaround for inconsistent data structures of the JSON API v1 and the
    #      return value of `get_method_calculation`
    title = calculation.title or calculation.Title
    uid = calculation.uid or calculation.UID

    if title and uid
      @add_select_option field, title, uid
    else
      @add_select_option field, null


  get_interims: =>
    ###
     * Extract the interim field values as a list of objects
    ###
    field = $("#archetypes-fieldname-InterimFields")
    rows = field.find("tr.records_row_InterimFields")

    interims = []
    $.each rows, (index, row) ->
      values = {}
      $.each $(row).find("td input"), (index, input) ->
        # Extract the key from the element name
        # InterimFields.keyword:records:ignore_empty
        key = @name.split(":")[0].split(".")[1]
        value = input.value
        if input.type is "checkbox"
          value = input.checked
        values[key] = value
      # Only rows with Keyword set
      if values.keyword isnt ""
        interims.push values
    return interims


  set_interims: (interims, flush=yes) =>
    ###
     * Set the interim field values
     * Note: This method takes the same input format as returned from get_interims
    ###

    # create a copy of the calculation interims
    interims = $.extend [], interims

    field = $("#archetypes-fieldname-InterimFields")
    more_button = field.find("#InterimFields_more")

    # empty all interims
    if flush
      @flush_interims()

    # always keep manual set interims
    $.each @manual_interims, (index, interim) ->
      interims.push interim

    $.each interims, (index, interim) ->
      last_row = field.find("tr.records_row_InterimFields").last()
      more_button.click()
      inputs = last_row.find "input"

      # iterate over all inputs of the interim field
      $.each inputs, (index, input) ->
        key = @name.split(":")[0].split(".")[1]
        value = interim[key]
        if input.type is "checkbox"
          # transform to bool value
          if value then vvalue = yes else value = no
          input.checked = value
        else
          input.value = value


  flush_interims: =>
    ###
     * Flush interim field
    ###
    field = $("#archetypes-fieldname-InterimFields")
    more_button = field.find("#InterimFields_more")
    more_button.click()
    rows = field.find("tr.records_row_InterimFields")
    rows.not(":last").remove()


  ### ASYNC DATA LOADERS ###

  load_available_calculations: =>
    ###
     * Load all available calculations to the calculation select box
    ###
    options =
      url: @get_portal_url() + "/get_available_calculations"
    return @ajax_submit options


  load_instrument_methods: (instrument_uid) =>
    ###
     * Load assigned methods of the instrument
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
        @add_select_option field, null


  load_method_calculation: (method_uid) =>
    ###
     * Load assigned calculation of the given method UID
     * Returns a deferred
    ###

    me = this
    deferred = $.Deferred()

    # Immediately if we do not have a valid method UID
    if not @is_uid method_uid
      console.warn "Method UID '#{method_uid}' is invalid"
      deferred.resolveWith me, [{}]
      return deferred.promise()

    options =
      url: @get_portal_url() + "/get_method_calculation"
      data:
        uid: method_uid

    # Fetch the assigned calculations of the method
    @ajax_submit options
    .done (data) ->
      deferred.resolveWith me, [data]

    return deferred.promise()


  load_calculation: (calculation_uid) =>
    ###
     * Load calculation object for the given UID
     * Returns a deferred
    ###
    me = this
    deferred = $.Deferred()

    # Immediately if we do not have a valid calculation UID
    if not @is_uid calculation_uid
      console.warn "Calculation UID '#{calculation_uid}' is invalid"
      deferred.resolveWith me, [{}]
      return deferred.promise()

    # Load the calculation, so that we can set the interims
    options =
      catalog_name: "bika_setup_catalog"
      UID: calculation_uid

    @read options, (data) ->
      calculation = {}
      if data.objects.length is 1
        calculation = data.objects[0]
      deferred.resolveWith me, [calculation]

    return deferred.promise()


  ### HELPERS ###

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


  ### ELEMENT HANDLING ###

  use_default_calculation_of_method: =>
    ###
     * Retrun the value of the "Use the Default Calculation of Method" checkbox
    ###
    field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation")
    return field.is(":checked")


  get_default_method: =>
    ###
     * Get the UID of the selected default method
    ###
    field = $("#archetypes-fieldname-Method #Method")
    return field.val()


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
    if not value
      name = "None"
    option = "<option value='#{value}'>#{@_(name)}</option>"
    return $(select).append option


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

    # "Use the Default Calculation of Method" checkbox checked
    if event.currentTarget.checked
      # - get the UID of the default method
      # - set the assigned calculation of the method
      # - unselect all previous calculation interims (just keep the manual ones)
      # - set the interims of the new set calculation

      # Get the UID of the default Method
      method_uid = @get_default_method()

      # Set empty calculation if method UID is not set
      if not @is_uid method_uid
        return @set_calculation null

      @load_method_calculation method_uid
      .done (data) ->
        # {uid: "488400e9f5e24a4cbd214056e6b5e2aa", title: "My Calculation"}
        @set_calculation data

        # load the calculation now, to set the interims
        @load_calculation @get_calculation()
        .done (calculation) ->
          @set_interims calculation.InterimFields

    else
      # load all available calculations
      @load_available_calculations()
      .done (calculations) ->
        me = this
        $.each calculations, (index, calculation) ->
          flush = if index is 0 then yes else no
          me.set_calculation calculation, flush
        # flush interims
        @set_interims null


  on_calculation_change: (event) =>
    ###
     * Eventhandler when the "Calculation" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_calculation_change °°°"

    # Always load interims of the calculation
    calculation_uid = event.currentTarget.value


  on_display_detection_limit_selector_change: (event) =>
    ###
     * Eventhandler when the "Display a Detection Limit selector" checkbox changed
     *
     * This checkbox is located on the "Analysis" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°"
