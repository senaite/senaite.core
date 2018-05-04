### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
###


class window.AnalysisServiceEditView

  load: =>
    console.debug "AnalysisServiceEditView::load"

    # load translations
    jarn.i18n.loadCatalog "bika"
    @_ = window.jarn.i18n.MessageFactory "bika"

    # Interim values defined by the user (not part of a calculation)
    @manual_interims = []

    # bind the event handler to the elements
    @bind_eventhandler()

    # Initialize the interims
    @init_interims()

    # Initialize the form
    @init_form()

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

    # The "Instrument assignment is not required" checkbox changed
    $("body").on "change", "#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults", @on_manual_entry_of_results_change

    # The "Methods" multiselect changed
    $("body").on "change", "#archetypes-fieldname-Methods #Methods", @on_methods_change

    # The "Instrument assignment is allowed" checkbox changed
    $("body").on "change", "#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults", @on_instrument_assignment_allowed_change

    # The "Instruments" multiselect changed
    $("body").on "change", "#archetypes-fieldname-Instruments #Instruments", @on_instruments_change

    # The "Default Instrument" selector changed
    $("body").on "change", "#archetypes-fieldname-Instrument #Instrument", @on_default_instrument_change

    # The "Default Method" select changed
    $("body").on "change", "#archetypes-fieldname-Method #Method", @on_default_method_change

    # The "Use the Default Calculation of Method" checkbox changed
    $("body").on "change", "#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation", @on_use_default_calculation_change

    # The "Calculation" selector changed
    $("body").on "change", "#archetypes-fieldname-Calculation #Calculation", @on_calculation_change

    ### ANALYSIS TAB ###

    # The "Display a Detection Limit selector" checkbox changed
    $("body").on "change", "#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector", @on_display_detection_limit_selector_change


  init_interims: =>
    ###*
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
      calculation_interims = $.extend [], calculation.InterimFields

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


  init_form: =>
    ###*
     * Initialize form
    ###

    # Init "Instrument assignment is not required" checkbox
    if @is_manual_entry_of_results_allowed()
      console.debug "Manual Entry of Results is allowed"
      @toggle_instrument_assignment_allowed on
    else
      console.debug "Manual Entry of Results is **not** allowed"
      # flush all methods and add only the "None" option
      @set_methods null

    # Init "Instrument assignment is allowed" checkbox
    if @is_instrument_assignment_allowed()
      console.debug "Instrument assignment is allowed"
    else
      console.debug "Instrument assignment is **not** allowed"
      # flush all instruments and add only the "None" option
      @set_instruments null


  ### FIELD GETTERS/SETTERS ###

  is_manual_entry_of_results_allowed: =>
    ###*
     * Get the value of the checkbox "Instrument assignment is not required"
     *
     * @returns {boolean} True if results can be entered without instrument
    ###
    field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults")
    return field.is ":checked"


  toggle_manual_entry_of_results_allowed: (toggle, silent=no) =>
    ###*
     * Toggle the "Instrument assignment is not required" checkbox
    ###
    field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults")
    if toggle is undefined
      toggle = not field.is ":checked"
    field.prop "checked", toggle
    # trigger change event
    if not silent then field.trigger "change"


  get_methods: =>
    ###*
     * Get all selected method UIDs from the multiselect field
     *
     * @returns {array} of method objects
    ###
    field = $("#archetypes-fieldname-Methods #Methods")
    return $.extend [], field.val()


  set_methods: (methods, flush=yes) =>
    ###*
     * Set the methods multiselect field with the given methods
     *
     * @param {array} methods
     *    Array of method objects with at least `title` and `uid` keys set
    ###
    field = $("#archetypes-fieldname-Methods #Methods")

    # create a copy of the methods array
    methods = $.extend [], methods

    # empty the field if the `flush` flag is set
    if flush then field.empty()

    if methods.length is 0
      @add_select_option field, null
    else
      me = this
      $.each methods, (index, method) ->
        # XXX only methods which allow manual entry
        #     -> workaround for missing catalog index
        if method.ManualEntryOfResults is no
          return
        title = method.title or method.Title
        uid = method.uid or method.UID
        me.add_select_option field, title, uid


  is_instrument_assignment_allowed: =>
    ###*
     * Get the value of the checkbox "Instrument assignment is allowed"
     *
     * @returns {boolean} True if instrument assignment is allowed
    ###
    field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults")
    return field.is ":checked"


  toggle_instrument_assignment_allowed: (toggle, silent=no) =>
    ###*
     * Toggle the "Instrument assignment is allowed" checkbox
     *
     * @param {boolean} toggle
     *    True to check the checkbox, False to uncheck the checkbox
    ###
    field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults")
    if toggle is undefined
      toggle = not field.is ":checked"
    field.prop "checked", toggle
    # trigger change event
    if not silent then field.trigger "change"


  get_instruments: =>
    ###*
     * Get all selected instrument UIDs from the multiselect
     *
     * @returns {array} of instrument objects
    ###
    field = $("#archetypes-fieldname-Instruments #Instruments")
    return $.extend [], field.val()


  set_instruments: (instruments, flush=yes) =>
    ###
     * Set the instruments to the field
     *
     * @param {array} instruments
     *    Array of instrument objects to set in the multi-select
    ###
    field = $("#archetypes-fieldname-Instruments #Instruments")

    # create a copy of the instruments array
    instruments = $.extend [], instruments

    # empty the field if the `flush` flag is set
    if flush then field.empty()

    if instruments.length is 0
      @add_select_option field, null
    else
      # set the instruments
      me = this
      $.each instruments, (index, instrument) ->
        uid = instrument.uid or instrument.UID
        title = instrument.title or instrument.Title
        me.add_select_option field, title, uid


  get_default_method: =>
    ###*
     * Get the UID of the selected default method
     *
     * @returns {string} UID of the default method
    ###
    field = $("#archetypes-fieldname-Method #Method")
    return field.val()


  set_default_method: (method, flush=yes) =>
    ###*
     * Set options for the default method select
    ###
    field = $("#archetypes-fieldname-Method #Method")

    # create a copy of the method
    method = $.extend {}, method

    # empty the field first
    if flush
      field.empty()

    title = method.title or method.Title
    uid = method.uid or method.UID

    if title and uid
      @add_select_option field, title, uid
    else
      @add_select_option field, null


  get_default_instrument: =>
    ###*
     * Get the UID of the selected default instrument
     *
     * @returns {string} UID of the default instrument
    ###
    field = $("#archetypes-fieldname-Instrument #Instrument")
    return field.val()


  set_default_instrument: (instrument, flush=yes) =>
    ###
     * Set options for the default instrument select
    ###
    field = $("#archetypes-fieldname-Instrument #Instrument")

    # create a copy of the instrument
    instrument = $.extend {}, instrument

    # empty the field first
    if flush
      field.empty()

    title = instrument.title
    uid = instrument.uid

    if title and uid
      @add_select_option field, title, uid
    else
      @add_select_option field, null


  use_default_calculation_of_method: =>
    ###*
     * Get the value of the checkbox "Use the Default Calculation of Method"
     *
     * @returns {boolean} True if the calculation of the method should be used
    ###
    field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation")
    return field.is ":checked"


  toggle_use_default_calculation_of_method: (toggle, silent=no) =>
    ###*
     * Toggle the "Use the Default Calculation of Method" checkbox
    ###
    field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation")
    if toggle is undefined
      toggle = not field.is ":checked"
    field.prop "checked", toggle
    # trigger change event
    if not silent then field.trigger "change"


  get_calculation: =>
    ###*
     * Get the UID of the selected default calculation
     *
     * @returns {string} UID of the calculation
    ###
    field = $("#archetypes-fieldname-Calculation #Calculation")
    return field.val()


  set_calculation: (calculation, flush=yes) =>
    ###*
     * Set the calculation field with the given calculation data
    ###
    field = $("#archetypes-fieldname-Calculation #Calculation")

    # create a copy of the calculation
    calculation = $.extend {}, calculation

    if flush
      field.empty()

    title = calculation.title or calculation.Title
    uid = calculation.uid or calculation.UID

    if title and uid
      @add_select_option field, title, uid
    else
      @add_select_option field, null


  get_interims: =>
    ###*
     * Extract the interim field values as a list of objects
     *
     * @returns {array} of interim record objects
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
    ###*
     * Set the interim field values
     *
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
          if value then value = yes else value = no
          input.checked = value
        else
          if not value then value = ""
          input.value = value


  flush_interims: =>
    ###*
     * Flush interim field
    ###
    field = $("#archetypes-fieldname-InterimFields")
    more_button = field.find("#InterimFields_more")
    more_button.click()
    rows = field.find("tr.records_row_InterimFields")
    rows.not(":last").remove()


  set_method_calculation: (method_uid) =>
    ###*
     * Loads the calculation of the method and set the interims of it
     *
     * @param {string} method_uid
     *    The UID of the method to set the calculations from
    ###

    if not @is_uid method_uid
      # remove all calculation interims
      @set_interims null
      # Set empty calculation
      @set_calculation null
    else
      # load the assigned calculation of the method
      @load_method_calculation method_uid
      .done (calculation) ->
        # set the default calculation
        @set_calculation calculation
        # set the interims of the default calculation
        @set_interims calculation.InterimFields


  set_instrument_methods: (instrument_uid, flush=yes) =>
    ###*
     * Loads the methods of the instrument
     *
     * @param {string} instrument_uid
     *    The UID of the instrument to set the method from
    ###
    me = this

    # Set empty default method if instrument UID is not set
    if not @is_uid instrument_uid
      return @set_default_method null

    @load_instrument_methods instrument_uid
    .done (methods) ->
      methods = $.extend [], methods
      $.each methods, (index, method) ->
        flush = if index is 0 then yes else no
        me.set_default_method method, flush=flush


  set_all_methods: =>
    ###*
     * Load and set all available methods
    ###
    cached = $.extend [], @_methods
    if cached.length
      @set_methods cached
    else
      @load_available_methods()
      .done (methods) ->
        @set_methods methods
        # cache
        @_methods = methods


  set_all_instruments: =>
    ###*
     * Load and set all available instruments
    ###

    if @_instruments
      instruments = $.extend [], @_instruments
      @set_instruments instruments
    else
      @load_available_instruments()
      .done (instruments) ->
        @set_instruments instruments
        # cache
        @_instruments = instruments


  set_all_calculations: =>
    ###
     * Load and set all available calculations
    ###
    @load_available_calculations()
    .done (calculations) ->
      me = this
      $.each calculations, (index, calculation) ->
        # flush only initially
        flush = if index is 0 then yes else no
        me.set_calculation calculation, flush
      # flush interims
      @set_interims null


  ### ASYNC DATA LOADERS ###

  load_available_calculations: =>
    ###*
     * Load all available calculations
     *
     * @returns {Deferred} Array of all available Calculation objects
    ###
    deferred = $.Deferred()

    options =
      url: @get_portal_url() + "/get_available_calculations"

    @ajax_submit options
    .done (data) ->
      if not data.objects
        # resolve with an empty array
        return deferred.resolveWith this, [[]]
      # resolve with data objects
      return deferred.resolveWith this, [data.objects]


  load_available_instruments: =>
    ###*
     * Load all available and valid instruments
     *
     * @returns {Deferred} Array of all available Instrument objects
    ###
    deferred = $.Deferred()

    options =
      url: @get_portal_url() + "/@@API/read"
      data:
        catalog_name: "bika_setup_catalog"
        page_size: 0
        portal_type: "Instrument"
        inactive_state: "active"
        sort_on: "sortable_title"

    @ajax_submit options
    .done (data) ->
      if not data.objects
        # resolve with an empty array
        return deferred.resolveWith this, [[]]
      # resolve with data objects
      return deferred.resolveWith this, [data.objects]

    return deferred.promise()


  load_available_methods: =>
    ###*
     * Load all available and valid instruments
     *
     * @returns {Deferred} Array of all available Method objects
    ###
    deferred = $.Deferred()

    options =
      url: @get_portal_url() + "/@@API/read"
      data:
        catalog_name: "bika_setup_catalog"
        page_size: 0
        portal_type: "Method"
        inactive_state: "active"
        sort_on: "sortable_title"

    @ajax_submit options
    .done (data) ->
      if not data.objects
        # resolve with an empty array
        return deferred.resolveWith this, [[]]
      return deferred.resolveWith this, [data.objects]

    return deferred.promise()


  load_instrument_methods: (instrument_uid) =>
    ###*
     * Load assigned methods of the instrument
     *
     * @param {string} instrument_uid
     *    The UID of the instrument
     * @returns {Deferred} Array of Method objects
    ###
    deferred = $.Deferred()

    # return immediately if we do not have a valid UID
    if not @is_uid instrument_uid
      deferred.resolveWith this, [[]]
      return deferred.promise()

    options =
      url: @get_portal_url() + "/get_instrument_methods"
      data:
        uid: instrument_uid
    @ajax_submit options
    .done (data) ->
      # {instrument: "51ebff9bf1314d00a7731b2f765dac37", methods: Array(3), title: "My Instrument"}
      # where `methods` is an array of {uid: "3a85b7bc0430496ba7d0a6bcb9cdc5d5", title: "My Method"}
      if not data.methods
        # resolve with an empty array
        deferred.resolveWith this, [[]]
      deferred.resolveWith this, [data.methods]

    return deferred.promise()


  load_method_calculation: (method_uid) =>
    ###*
     * Load assigned calculation of the given method UID
     *
     * @param {string} method_uid
     *    The UID of the method
     * @returns {Deferred} Calculation object
    ###
    deferred = $.Deferred()

    # return immediately if we do not have a valid UID
    if not @is_uid method_uid
      deferred.resolveWith this, [{}]
      return deferred.promise()

    options =
      url: @get_portal_url() + "/get_method_calculation"
      data:
        uid: method_uid

    @ajax_submit options
    .done (data) ->
      # /get_method_calculation returns just this structure:
      # {uid: "488400e9f5e24a4cbd214056e6b5e2aa", title: "My Calculation"}
      if not @is_uid data.uid
        return deferred.resolveWith this, [{}]
      # load the full calculation object
      @load_calculation data.uid
      .done (calculation) ->
        # resolve with the full calculation object
        return deferred.resolveWith this, [calculation]

    return deferred.promise()


  load_calculation: (calculation_uid) =>
    ###
     * Load calculation object from the JSON API for the given UID
     *
     * @param {string} calculation_uid
     *    The UID of the calculation
     * @returns {Deferred} Calculation object
    ###
    deferred = $.Deferred()

    # return immediately if we do not have a valid UID
    if not @is_uid calculation_uid
      deferred.resolveWith this, [{}]
      return deferred.promise()

    options =
      url: @get_portal_url() + "/@@API/read"
      data:
        catalog_name: "bika_setup_catalog"
        page_size: 0
        UID: calculation_uid
        inactive_state: "active"
        sort_on: "sortable_title"

    @ajax_submit options
    .done (data) ->
      calculation = {}
      # Parse the calculation object from the response data
      if data.objects.length is 1
        calculation = data.objects[0]
      else
        console.warn "Invalid data returned for calculation UID #{calculation_uid}: ", data
      # Resolve the deferred with the parsed calculation
      return deferred.resolveWith this, [calculation]

    return deferred.promise()


  ### HELPERS ###

  ajax_submit: (options) =>
    ###*
     * Ajax Submit with automatic event triggering and some sane defaults
     *
     * @param {object} options
     *    jQuery ajax options
     * @returns {Deferred} XHR request
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
    done = ->
      $(this).trigger "ajax:submit:end"
    return $.ajax(options).done done


  get_portal_url: =>
    ###*
     * Return the portal url
     *
     * @returns {string} portal url
    ###
    return window.portal_url


  is_uid: (str) =>
    ###*
     * Validate valid UID
     *
     * @returns {boolean} True if the argument is a UID
    ###
    if typeof str isnt "string"
      return no
    match = str.match /[a-z0-9]{32}/
    return match isnt null


  add_select_option: (select, name, value) =>
    ###*
     * Adds an option to the select
    ###

    # empty option
    if not value
      name = "None"
    option = "<option value='#{value}'>#{@_(name)}</option>"
    return $(select).append option

  select_first: (select) =>
    ###*
     * Select the first option of the select element
    ###
    $(select).children().first().prop "selected", yes


  ### EVENT HANDLER ###

  on_manual_entry_of_results_change: (event) =>
    ###*
     * Eventhandler when the "Instrument assignment is not required" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°"

    # Results can be set by "hand"
    if @is_manual_entry_of_results_allowed()
      console.debug "Manual entry of results is allowed"
      # load all methods to the methods multi-select
      @set_all_methods()
      # set the methods of the default instrument
      @set_instrument_methods @get_default_instrument()
    else
      # Results can be only set by an instrument
      console.debug "Manual entry of results is **not** allowed"
      # Flush all methods ()
      @set_methods null
      # Flush default method
      @set_default_method null
      # Flush default instrument
      @set_default_instrument null
      # Enable instrument assignment
      @toggle_instrument_assignment_allowed on
      # Disable "Use the Default Calculation of Method"
      @toggle_use_default_calculation_of_method off


  on_methods_change: (event) =>
    ###*
     * Eventhandler when the "Methods" multiselect changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_methods_change °°°"

    # selected method UIDs
    method_uids = @get_methods()

    # All methods deselected
    if method_uids.length is 0
      console.warn "All methods deselected"

    # Set selected methods to the list of the default methods
    me = this
    $.each method_uids, (index, uid) ->
      flush = index is 0 and yes or no
      # extract the title and uid from the option element
      $el = $(event.currentTarget)
      option = $el.find "option[value=#{uid}]"
      method =
        uid: option.val()
        title: option.text()
      me.set_default_method method, flush=flush

    # set the calculation of the default method
    @set_method_calculation @get_default_method()


  on_instrument_assignment_allowed_change: (event) =>
    ###*
     * Eventhandler when the "Instrument assignment is allowed" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°"

    if @is_instrument_assignment_allowed()
      console.debug "Instrument assignment is allowed"
      # load all instruments to the instruments multi-select
      # N.B. Methods with ManualEntryOfResults==false are filtered!
      @set_all_instruments()
    else
      console.debug "Instrument assignment is **not** allowed"
      @set_instruments null
      @set_default_instrument null
      # XXX Which instrument to load now?


  on_instruments_change: (event) =>
    ###*
     * Eventhandler when the "Instruments" multiselect changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instruments_change °°°"

    # selected instrument UIDs
    instrument_uids = @get_instruments()

    if instrument_uids.length is 0
      console.warn "All instruments deselected"

    # Set selected instruments to the list of the default instruments
    me = this
    $.each instrument_uids, (index, uid) ->
      flush = index is 0 and yes or no
      # extract the title and uid from the option element
      $el = $(event.currentTarget)
      option = $el.find "option[value=#{uid}]"
      instrument =
        uid: option.val()
        title: option.text()
      me.set_default_instrument instrument, flush=flush

    # set the instrument methods of the default instrument
    @set_instrument_methods @get_default_instrument()


  on_default_instrument_change: (event) =>
    ###*
     * Eventhandler when the "Default Instrument" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_instrument_change °°°"

    # set the instrument methods of the default instrument
    @set_instrument_methods @get_default_instrument()


  on_default_method_change: (event) =>
    ###*
     * Eventhandler when the "Default Method" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_method_change °°°"

    # Load the calculation of the method if the checkbox "Use the Default
    # Calculation of Method" is checked
    if @use_default_calculation_of_method()
      # Get the UID of the default Method
      method_uid = @get_default_method()
      # set the calculation of the method
      @set_method_calculation method_uid


  on_use_default_calculation_change: (event) =>
    ###*
     * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_use_default_calculation_change °°°"

    # "Use the Default Calculation of Method" checkbox checked
    if @use_default_calculation_of_method()
      # set the calculation of the method
      @set_method_calculation @get_default_method()
    else
      # load all available calculations
      @set_all_calculations()


  on_calculation_change: (event) =>
    ###*
     * Eventhandler when the "Calculation" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_calculation_change °°°"

    # load the calculation now, to set the interims
    @load_calculation @get_calculation()
    .done (calculation) ->
      @set_interims calculation.InterimFields


  on_display_detection_limit_selector_change: (event) =>
    ###*
     * Eventhandler when the "Display a Detection Limit selector" checkbox changed
     *
     * This checkbox is located on the "Analysis" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_display_detection_limit_selector_change °°°"
