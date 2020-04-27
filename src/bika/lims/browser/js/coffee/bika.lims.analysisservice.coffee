### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisservice.coffee
###


class window.AnalysisServiceEditView

  load: =>
    console.debug "AnalysisServiceEditView::load"

    # load translations
    jarn.i18n.loadCatalog "bika"
    @_ = window.jarn.i18n.MessageFactory "bika"

    # All available instruments by UID
    @all_instruments = {}

    # All invalid instruments by UID
    @invalid_instruments = {}

    # Load available instruments
    d1 = @load_available_instruments()
    .done (instruments) ->
      me = this
      $.each instruments, (index, instrument) ->
        uid = instrument.UID
        # remember the instrument
        me.all_instruments[uid] = instrument
        if instrument.Valid isnt "1"
          # remember invalid instrument
          me.invalid_instruments[uid] = instrument

    # Interim values defined by the user (not part of the current calculation)
    @manual_interims = []

    # Calculate manual set interims
    d2 = @load_manual_interims()
    .done (manual_interims) ->
      @manual_interims = manual_interims

    # UIDs of the initial selected methods
    @selected_methods = @get_methods()

    # UIDs of the initial selected instruments
    @selected_instruments = @get_instruments()

    # UID of the initial selected calculation
    @selected_calculation = @get_calculation()

    # UID of the initial selected default instrument
    @selected_default_instrument = @get_default_instrument()

    # UID of the initial selected default method
    @selected_default_method = @get_default_method()

    # Array of UID/Title objects of the initial options from the methods field
    @methods = @parse_select_options $("#archetypes-fieldname-Methods #Methods")

    # Array of UID/Title objects of the initial options from the instrument field
    @instruments = @parse_select_options $("#archetypes-fieldname-Instruments #Instruments")

    # Array of UID/Title objects of the initial options from the calculations field
    @calculations = @parse_select_options $("#archetypes-fieldname-Calculation #Calculation")

    # bind the event handler to the elements
    @bind_eventhandler()

    # initialize the form when all data is loaded
    $.when(d1, d2).then @init

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


    ### CONTAINER AND PRESERVATION TAB ###

    # The "Separate Container" checkbox changed
    $("body").on "change", "#archetypes-fieldname-Separate #Separate", @on_separate_container_change

    # The "Default Preservation" select changed
    $("body").on "change", "#archetypes-fieldname-Preservation #Preservation", @on_default_preservation_change

    # The "Default Container" select changed
    $("body").on "selected", "#archetypes-fieldname-Container #Container", @on_default_container_change

    # The "Sample Type" select changed in the Partition setup
    $("body").on "change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.sampletype']", @on_partition_sampletype_change

    # The "Separate Container" checkbox changed in the Partition setup
    $("body").on "change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.separate']", @on_partition_separate_container_change

    # The "Container" checkbox changed in the Partition setup
    $("body").on "change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.container']", @on_partition_container_change

    # The "Required Volume" value changed in the Partition setup
    $("body").on "change", "#archetypes-fieldname-PartitionSetup [name^='PartitionSetup.vol']", @on_partition_required_volume_change


  init: =>
    ###*
     * Initialize Form
    ###

    # Set "Instrument assignment is not required" checkbox
    if @is_manual_entry_of_results_allowed()
      console.debug "--> Manual Entry of Results is allowed"
      # restore all initial set methods in the method multi-select
      @set_methods @methods
    else
      console.debug "--> Manual Entry of Results is **not** allowed"
      # flush all methods and add only the "None" option
      @set_methods null

    # Set "Instrument assignment is allowed" checkbox
    if @is_instrument_assignment_allowed()
      console.debug "--> Instrument assignment is allowed"
      # restore all initial set instruments
      @set_instruments @instruments
    else
      console.debug "--> Instrument assignment is **not** allowed"
      # flush all instruments and add only the "None" option
      @set_instruments null

    # Set "Use the Default Calculation of Method" checkbox
    if @use_default_calculation_of_method()
      console.debug "--> Use default calculation of method"
    else
      console.debug "--> Use default calculation of instrument"


  ### FIELD GETTERS/SETTERS/SELECTORS ###

  is_manual_entry_of_results_allowed: =>
    ###*
     * Get the value of the checkbox "Instrument assignment is not required"
     *
     * @returns {boolean} True if results can be entered without instrument
    ###
    field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults")
    return field.is ":checked"


  toggle_manual_entry_of_results_allowed: (toggle, silent=yes) =>
    ###*
     * Toggle the "Instrument assignment is not required" checkbox
    ###
    field = $("#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults")
    @toggle_checkbox field, toggle, silent


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
     *
     * @param {boolean} flush
     *    True to empty all instruments first
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
        # ensure only "methods with allow manual entry"
        if method.ManualEntryOfResults is no
          return
        title = method.title or method.Title
        uid = method.uid or method.UID
        me.add_select_option field, title, uid

    # restore initial selection
    @select_methods @selected_methods


  select_methods: (uids) =>
    ###*
     * Select methods by UID
     *
     * @param {Array} uids
     *    UIDs of Methods to select
    ###

    if not @is_manual_entry_of_results_allowed()
      console.debug "Manual entry of results is not allowed"
      return

    field = $("#archetypes-fieldname-Methods #Methods")
    # set selected attribute to the options
    @select_options field, uids

    # Set selected value to the default method select box
    me = this
    $.each uids, (index, uid) ->
      # flush the field for the first element
      flush = index is 0 and yes or no
      # extract the title and uid from the option element
      option = field.find "option[value=#{uid}]"
      method =
        uid: option.val()
        title: option.text()
      # append option to the default method select box
      me.set_default_method method, flush=flush

    # restore initial selected default method
    @select_default_method @selected_default_method

    if @use_default_calculation_of_method()
      # set the calculation of the default method
      @set_method_calculation @get_default_method()


  is_instrument_assignment_allowed: =>
    ###*
     * Get the value of the checkbox "Instrument assignment is allowed"
     *
     * @returns {boolean} True if instrument assignment is allowed
    ###
    field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults")
    return field.is ":checked"


  toggle_instrument_assignment_allowed: (toggle, silent=yes) =>
    ###*
     * Toggle the "Instrument assignment is allowed" checkbox
    ###
    field = $("#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults")
    @toggle_checkbox field, toggle, silent


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
     *
     * @param {boolean} flush
     *    True to empty all instruments first
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

    # restore initial selection
    @select_instruments @selected_instruments


  select_instruments: (uids) =>
    ###*
     * Select instruments by UID
     *
     * @param {Array} uids
     *    UIDs of Instruments to select
    ###

    if not @is_instrument_assignment_allowed()
      console.debug "Instrument assignment not allowed"
      @set_default_instrument null
      return

    field = $("#archetypes-fieldname-Instruments #Instruments")
    # set selected attribute to the options
    @select_options field, uids

    invalid_instruments = []

    # Set selected instruments to the list of the default instruments
    me = this
    $.each uids, (index, uid) ->
      flush = index is 0 and yes or no
      # get the instrument
      instrument = me.all_instruments[uid]
      if uid of me.invalid_instruments
        console.warn "Instrument '#{instrument.Title}' is invalid"
        invalid_instruments.push instrument
      me.set_default_instrument instrument, flush=flush

    # show invalid instruments
    if invalid_instruments.length > 0
      notification = $("<dl/>")
      $.each invalid_instruments, (index, instrument) ->
        notification.append "<dd>⚠ #{instrument.Title}</dd>"
      title = @_ "Some of the selected instruments are out-of-date, with failed calibration tests or under maintenance"
      @show_alert title: title, message: notification[0].outerHTML
    else
      @show_alert message: ""

    # restore initially selected default instrument
    @select_default_instrument @selected_default_instrument

    # set the instrument methods of the default instrument
    @set_instrument_methods @get_default_instrument()


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


  select_default_method: (uid) =>
    ###*
     * Select method by UID
     *
     * @param {string} uid
     *    UID of Method to select
    ###
    field = $("#archetypes-fieldname-Method #Method")
    @select_options field, [uid]


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

    title = instrument.title or instrument.Title
    uid = instrument.uid or instrument.UID

    if title and uid
      @add_select_option field, title, uid
    else
      @add_select_option field, null


  select_default_instrument: (uid) =>
    ###*
     * Select instrument by UID
     *
     * @param {string} uid
     *    UID of Instrument to select
    ###
    field = $("#archetypes-fieldname-Instrument #Instrument")
    @select_options field, [uid]


  use_default_calculation_of_method: =>
    ###*
     * Get the value of the checkbox "Use the Default Calculation of Method"
     *
     * @returns {boolean} True if the calculation of the method should be used
    ###
    field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation")
    return field.is ":checked"


  toggle_use_default_calculation_of_method: (toggle, silent=yes) =>
    ###*
     * Toggle the "Use the Default Calculation of Method" checkbox
    ###
    field = $("#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation")
    @toggle_checkbox field, toggle, silent


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


  select_calculation: (uid) =>
    ###*
     * Select calculation by UID
     *
     * @param {string} uid
     *    UID of Calculation to select
    ###
    field = $("#archetypes-fieldname-Calculation #Calculation")
    @select_options field, [uid]

    # load the calculation now, to set the interims
    @load_calculation uid
    .done (calculation) ->
      @set_interims calculation.InterimFields


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
      inputs = row.querySelectorAll "td input"
      $.each inputs, (index, input) ->
        # Extract the key from the element name
        # InterimFields.keyword:records:ignore_empty
        key = @name.split(":")[0].split(".")[1]
        value = input.value
        if input.type is "checkbox"
          value = input.checked
        values[key] = value
        # N.B. coffee-script always returns the last value if not explicitly returned
        #      and false values act as a break in $.each loops!
        return true

      # Only rows with Keyword set
      if values.keyword isnt ""
        interims.push values

      # N.B. coffee-script always returns the last value if not explicitly returned
      #      and false values act as a break in $.each loops!
      return true

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

    # extract the keys of the calculation interims
    interim_keys = interims.map (v) -> return v.keyword

    # always keep manual set interims
    $.each @manual_interims, (index, interim) ->
      # the keyword of the manual interim is in the keys of the calculation
      # interims -> overwrite calculation interim with the manual interim
      i = interim_keys.indexOf interim.keyword
      if i >= 0
        interims[i] = interim
      else
        # append the manual interim at the end
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
          input.checked = value
          # N.B. if we omit the value, the field won't be set on save
          input.value = "on"
        else
          if not value then value = ""
          input.value = value

        # N.B. coffee-script always returns the last value if not explicitly returned
        #      and false values act as a break in $.each loops!
        return true


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

    # Leave default method if the "None" instrument was selected
    if not @is_uid instrument_uid
      return

    @load_instrument_methods instrument_uid
    .done (methods) ->
      methods = $.extend [], methods
      # Extend the default methods with the instrument methods
      $.each methods, (index, method) ->
        flush = if index is 0 then yes else no
        me.set_default_method method, flush=flush

      # restore the initially selected method
      @select_default_method @selected_default_method

      # set the calculation of the method
      if @use_default_calculation_of_method()
        @set_method_calculation @get_default_method()


  show_alert: (options) =>
    ###
     * Display a notification box above the content
    ###
    title = options.title or ""
    message = options.message or ""
    level = options.level or "warning"
    flush = options.flush or yes

    alerts = $("#viewlet-above-content #alerts")
    if alerts.length is 0
       $("#viewlet-above-content").append "<div id='alerts'></div>"
      alerts = $("#viewlet-above-content #alerts")
    if flush then alerts.empty()
    if message is "" then alerts.remove()
    html = """
    <div class="alert alert-#{level} errorbox" role="alert">
      <h3>#{title}</h3>
      <div>#{message}</div>
    </div>
    """
    alerts.append html


  ### ASYNC DATA LOADERS ###


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

    @ajax_submit options
    .done (data) ->
      if not data.objects
        # resolve with an empty array
        return deferred.resolveWith this, [[]]
      # resolve with data objects
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
        is_active: true
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


  load_manual_interims: =>
    ###*
     * 1. Load the default calculation
     * 2. Subtract calculation interims from the current active interims
     *
     * XXX: This should be better done by the server!
     *
     * @returns {Deferred} Array of manual interims
    ###
    deferred = $.Deferred()

    @load_calculation @get_calculation()
    .done (calculation) ->

      # interims of this calculation
      calculation_interims = $.extend [], calculation.InterimFields

      # extract the keys of the calculation interims
      calculation_interim_keys = calculation_interims.map (v) -> return v.keyword

      # separate manual interims from calculation interims
      manual_interims = []
      $.each @get_interims(), (index, value) ->
        # manual interim is not part of the calculation interims
        if value.keyword not in calculation_interim_keys
          manual_interims.push value
        else
          # manual interim is also located in the calculaiton interims
          # -> check for interim override, e.g. different value, unit etc.

          # get the calculation interim
          i = calculation_interim_keys.indexOf value.keyword
          calculation_interim = calculation_interims[i]

          # check for different values
          $.each calculation_interim, (k, v) ->
            if v isnt value[k]
              manual_interims.push value
              # stop iteration
              return false
      deferred.resolveWith this, [manual_interims]

    return deferred.promise()


  load_object_by_uid: (uid) =>
    ###
     * Load object by UID
     *
     * @returns {Deferred}
    ###
    deferred = $.Deferred()

    options =
      url: @get_portal_url() + "/@@API/read"
      data:
        catalog_name: "uid_catalog"
        page_size: 0
        UID: uid

    @ajax_submit options
    .done (data) ->
      object = {}
      if data.objects.length is 1
        object = data.objects[0]
      # Resolve the deferred with the parsed calculation
      return deferred.resolveWith this, [object]

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


  get_url: =>
    ###*
     * Return the current absolute url
     *
     * @returns {string} current absolute url
    ###
    location = window.location
    protocol = location.protocol
    host = location.host
    pathname = location.pathname
    return "#{protocol}//#{host}#{pathname}"


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

    if value
      option = "<option value='#{value}'>#{@_(name)}</option>"
    else
      # empty option (selected by default)
      option = "<option selected='selected' value=''>#{@_("None")}</option>"
    return $(select).append option


  parse_select_options: (select) =>
    ###*
     * Parse UID/Title from the select field
     *
     * @returns {Array} of UID/Title objects
    ###
    options = []
    $.each $(select).children(), (index, option) ->
      uid = option.value
      title = option.innerText
      return unless uid
      options.push
        uid: uid
        title: title
    return options


  parse_select_option: (select, value) =>
    ###*
     * Return the option by value
    ###
    option = field.find "option[value=#{uid}]"
    data =
      uid: option.val() or ""
      title: option.text() or ""
    return data


  select_options: (select, values) =>
    ###*
     * Select the options of the given select field where the value is in values
    ###
    $.each $(select).children(), (index, option) ->
      value = option.value
      return unless value in values
      option.selected = "selected"


  toggle_checkbox: (checkbox, toggle, silent=yes) =>
    ###*
     * Toggle the checkbox
     *
     * @param {element} checkbox
     *    The checkbox to toggle
     *
     * @param {boolean} toggle
     *    True to check the checkbox
     *
     * @param {boolean} silent
     *    True to trigger a "change" event after set
    ###
    field = $(checkbox)
    if toggle is undefined
      toggle = not field.is ":checked"
    field.prop "checked", toggle
    # trigger change event
    if not silent then field.trigger "change"


  ### EVENT HANDLER ###

  on_manual_entry_of_results_change: (event) =>
    ###*
     * Eventhandler when the "Instrument assignment is not required" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_manual_entry_of_results_change °°°"

    # Results can be set by "hand"
    if @is_manual_entry_of_results_allowed()
      console.debug "Manual entry of results is allowed"
      # restore all initial set methods
      @set_methods @methods
    else
      # Results can be only set by an instrument
      console.debug "Manual entry of results is **not** allowed"
      # flush all methods and add only the "None" option
      @set_methods null


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

    # Select the methods
    @select_methods method_uids


  on_instrument_assignment_allowed_change: (event) =>
    ###*
     * Eventhandler when the "Instrument assignment is allowed" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instrument_assignment_allowed_change °°°"

    if @is_instrument_assignment_allowed()
      console.debug "Instrument assignment is allowed"
      # restore the instruments multi-select to the initial value
      @set_instruments @instruments
    else
      console.debug "Instrument assignment is **not** allowed"
      @set_instruments null


  on_instruments_change: (event) =>
    ###*
     * Eventhandler when the "Instruments" multiselect changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_instruments_change °°°"

    # selected instrument UIDs
    instrument_uids = @get_instruments()

    if instrument_uids.length is 0
      console.warn "All instruments deselected"

    # Select the instruments
    @select_instruments instrument_uids


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
      # set the calculation of the method
      @set_method_calculation @get_default_method()


  on_use_default_calculation_change: (event) =>
    ###*
     * Eventhandler when the "Use the Default Calculation of Method" checkbox changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_use_default_calculation_change °°°"

    # "Use the Default Calculation of Method" checkbox checked
    if @use_default_calculation_of_method()
      console.debug "Use default calculation"
      # set the calculation of the method
      @set_method_calculation @get_default_method()
    else
      # restore all initial set calculations
      me = this
      $.each @calculations, (index, calculation) ->
        flush = if index is 0 then yes else no
        me.set_calculation calculation, flush=flush
      # select initial set calculation
      if @selected_calculation
        @select_calculation @selected_calculation
      # select first calculation in list
      else
        @select_calculation @get_calculation()


  on_calculation_change: (event) =>
    ###*
     * Eventhandler when the "Calculation" selector changed
    ###
    console.debug "°°° AnalysisServiceEditView::on_calculation_change °°°"
    @select_calculation @get_calculation()


  on_separate_container_change: (event) =>
    ###*
     * Eventhandler when the "Separate Container" checkbox changed
     *
     * This checkbox is located on the "Container and Preservation" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_separate_container_change °°°"

    value = event.currentTarget.checked


  on_default_preservation_change: (event) =>
    ###*
     * Eventhandler when the "Default Preservation" selection changed
     *
     * This field is located on the "Container and Preservation" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_preservation_change °°°"


  on_default_container_change: (event) =>
    ###*
     * Eventhandler when the "Default Container" selection changed
     *
     * This field is located on the "Container and Preservation" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_default_container_change °°°"

    el = event.currentTarget
    uid = el.getAttribute "uid"

    field = $("#archetypes-fieldname-Preservation #Preservation")

    @load_object_by_uid uid
    .done (data) ->
      if data
        field.val data.Preservation
        field.prop "disabled", yes
      else
        field.val ""
        field.prop "disabled", no


  on_partition_sampletype_change: (event) =>
    ###*
     * Eventhandler when the "Sample Type" selection changed
     *
     * This field is located on the "Container and Preservation" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_partition_sampletype_change °°°"

    el = event.currentTarget
    uid = el.value

    @load_object_by_uid uid
    .done (sampletype) ->
      minvol = sampletype.MinimumVolume or ""
      # set the minimum volume to the partition
      $(el).parents("tr").find("[name^='PartitionSetup.vol']").val minvol


  on_partition_separate_container_change: (event) =>
    ###*
     * Eventhandler when the "Separate Container" checkbox changed
     *
     * This checkbox is located on the "Container and Preservation" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_partition_separate_container_change °°°"


  on_partition_container_change: (event) =>
    ###*
     * Eventhandler when the "Container" multi-select changed
     *
     * This multi select is located on the "Container and Preservation" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_partition_container_change °°°"
    el = event.currentTarget
    uid = el.value

    field = $(el).parents("tr").find("[name^='PartitionSetup.preservation']")

    @load_object_by_uid uid
    .done (data) ->
      if not $.isEmptyObject data
        $(el).val data.UID
        $(field).val data.Preservation
        $(field).prop "disabled", yes
      else
        $(field).prop "disabled", no


  on_partition_required_volume_change: (event) =>
    ###*
     * Eventhandler when the "Required Volume" value changed
     *
     * This field is located on the "Container and Preservation" Tab
    ###
    console.debug "°°° AnalysisServiceEditView::on_partition_required_volume_change °°°"
