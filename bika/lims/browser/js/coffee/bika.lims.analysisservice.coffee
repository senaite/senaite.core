### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
###


class window.AnalysisServiceEditView

  load: =>
    console.debug "AnalysisServiceEditView::load"

    # load translations
    jarn.i18n.loadCatalog 'bika'
    @_ = window.jarn.i18n.MessageFactory('bika')

    # bind the event handler to the elements
    @bind_eventhandler()

    # Develpp only
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


  ### LOADERS ###

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
      url: @get_url() + "/get_instrument_methods"
      data:
        uid: instrument_uid
    @ajax_submit options
    .done (data) ->
      $.each data.methods, (index, item) ->
        option = "<option value='#{item.uid}'>#{item.title}</option>"
        field.append option
      if field.length == 0
        console.warn "Instrument with UID '#{instrument_uid}' has no methods assigned"
        @add_empty_option field


  load_available_calculations: =>
    ###
     * Load all available calculations to the calculation select box
    ###
    field = $("#archetypes-fieldname-Calculation #Calculation")
    field.empty()
    options =
      url: @get_url() + "/get_available_calculations"
    @ajax_submit options
    .done (data) ->
      $.each data, (index, item) ->
        option = "<option value='#{item.uid}'>#{item.title}</option>"
        field.append option
      if field.length == 0
        @add_empty_option field


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
      url: @get_url() + "/get_method_calculation"
      data:
        uid: method_uid

    # Fetch the assigned calculations of the method
    @ajax_submit options
    .done (data) ->
      if not $.isEmptyObject data
        option = "<option value='#{data.uid}'>#{data.title}</option>"
        field.append option
      else
        @add_empty_option field


  ### METHODS ###

  ajax_submit: (options) =>
    ###
     * Ajax Submit with automatic event triggering and some sane defaults
    ###
    console.debug "°°° ajax_submit °°°"

    # some sane option defaults
    options ?= {}
    options.type ?= "POST"
    options.url ?= @get_url()
    options.context ?= this
    options.dataType ?= "json"
    options.data ?= {}
    options.data._authenticator ?= @get_authenticator()

    console.debug ">>> ajax_submit::options=", options

    $(this).trigger "ajax:submit:start"
    done = =>
        $(this).trigger "ajax:submit:end"
    return $.ajax(options).done done


  get_url: =>
    ###
     * Return the current URL
    ###
    protocol = location.protocol
    host = location.host
    pathname = location.pathname
    return "#{protocol}//#{host}#{pathname}"

  get_portal_url: =>
    ###
     * Return the portal url
    ###
    return window.portal_url


  get_authenticator: =>
    ###
     * Get the authenticator value
    ###
    return $("input[name='_authenticator']").val()


  is_uid: (str) =>
    ###
     * Validate valid URL
    ###
    if typeof str isnt "string"
      return no
    match = str.match /[a-z0-9]{32}/
    return match isnt null


  show_methods_field: (toggle) =>
    ###
     * This method toggles the visibility of complete "Methods" field
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


  add_empty_option: (select) =>
    ###
     * Add an empty option to the select box
    ###
    empty_option = "<option value=''>#{@_('None')}</option>"
    $(select).append empty_option
    $(select).val ""


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
