### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.site.coffee
###


class window.SiteView

  load: =>
    console.debug "SiteView::load"

    # load translations
    jarn.i18n.loadCatalog 'bika'
    @_ = window.jarn.i18n.MessageFactory('bika')

    # initialze the loading spinner
    @init_spinner()

    # initialze the client add overlay
    @init_client_add_overlay()

    # initialze the client combogrid
    @init_client_combogrid()

    # initialze datepickers
    @init_datepickers()

    # initialze reference definition selection
    @init_referencedefinition()

    # initialze department filtering
    @init_department_filtering()

    # bind the event handler to the elements
    @bind_eventhandler()

    # allowed keys for numeric fields
    @allowed_keys = [
      8,    # backspace
      9,    # tab
      13,   # enter
      35,   # end
      36,   # home
      37,   # left arrow
      39,   # right arrow
      46,   # delete - We don't support the del key in Opera because del == . == 46.
      44,   # ,
      60,   # <
      62,   # >
      45,   # -
      69,   # E
      101,  # e,
      61    # =
    ]

    # The name of the department filter cookies
    @department_filter_cookie = "filter_by_department_info"
    @department_filter_disabled_cookie = "dep_filter_disabled"


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
    ###
    console.debug "SiteView::bind_eventhandler"

    # Analysis service popup
    $('.service_title span:not(.before)').on 'click', @on_analysis_service_title_click

    # ReferenceSample selection changed
    $("#ReferenceDefinition\\:list").on "change", @on_reference_definition_list_change

    # Numeric field events
    $('.numeric').on 'keypress', @on_numeric_field_keypress
    $('.numeric').on 'paste', @on_numeric_field_paste

    # AT field events
    $("input[name*='\\:int\'], .ArchetypesIntegerWidget input").on "keyup", @on_at_integer_field_keyup
    $("input[name*='\\:float\'], .ArchetypesDecimalWidget input").on "keyup", @on_at_float_field_keyup

    # Autocomplete events
    # XXX Where is this used?
    $("input.autocomplete").on "keydown", @on_autocomplete_keydown

    # Department filtering events
    $("#department_filter_submit").on "click", @on_department_filter_submit
    $("#admin_dep_filter_enabled").on "change", @on_admin_dep_filter_change
    $("select[name='Departments:list']").on "change", @on_department_list_change

    # Date Range Filtering
    $(".date_range_start").on "change", @on_date_range_start_change
    $(".date_range_end").on "change", @on_date_range_end_change

    # handle Ajax events
    $(document).on "ajaxStart", @on_ajax_start
    $(document).on "ajaxStop", @on_ajax_end
    $(document).on "ajaxError", @on_ajax_error


  init_client_add_overlay: =>
    ###
     * Initialize Client Overlay
    ###
    console.debug "SiteView::init_client_add_overlay"

    $('a.add_client').prepOverlay
      subtype: 'ajax'
      filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info'
      formselector: '#client-base-edit'
      closeselector: '[name="form.button.cancel"]'
      width: '70%'
      noform: 'close'
      config:
        closeOnEsc: false
        onLoad: ->
          # manually remove remarks
          @getOverlay().find('#archetypes-fieldname-Remarks').remove()
          return
        onClose: ->
          # here is where we'd populate the form controls, if we cared to.
          return


  init_spinner: =>
    ###
     * Initialize Spinner Overlay
    ###
    console.debug "SiteView::init_spinner"

    # unbind default Plone loader
    $(document).unbind 'ajaxStart'
    $(document).unbind 'ajaxStop'
    $('#ajax-spinner').remove()

    # counter of active spinners
    @counter = 0

    # crate a spinner and append it to the body
    @spinner = $("<div id='bika-spinner'><img src='#{@get_portal_url()}/spinner.gif' alt=''/></div>")
    @spinner.appendTo('body').hide()


  init_client_combogrid: =>
    ###
     * Initialize client combogrid, e.g. on the Client Add View
    ###
    console.debug "SiteView::init_client_combogrid"

    $("input[id*='ClientID']").combogrid
      colModel: [
        'columnName': 'ClientUID'
        'hidden': true
      ,
        'columnName': 'ClientID'
        'width': '20'
        'label': _('Client ID')
      ,
        'columnName': 'Title'
        'width': '80'
        'label': _('Title')
      ]
      showOn: true
      width: '450px'
      url: "#{@get_portal_url()}/getClients?_authenticator=#{@get_authenticator()}"
      select: (event, ui) ->
        $(this).val ui.item.ClientID
        $(this).change()
        false


  init_datepickers: =>
    ###
     * Initialize date pickers
     *
     * XXX Where are these event handlers used?
    ###
    console.debug "SiteView::init_datepickers"

    curDate = new Date
    y = curDate.getFullYear()
    limitString = '1900:' + y
    dateFormat = @_('date_format_short_datepicker')

    if dateFormat == 'date_format_short_datepicker'
      dateFormat = 'yy-mm-dd'

    $('input.datepicker_range').datepicker
      ###*
      This function defines a datepicker for a date range. Both input
      elements should be siblings and have the class 'date_range_start' and
      'date_range_end'.
      ###
      showOn: 'focus'
      showAnim: ''
      changeMonth: true
      changeYear: true
      dateFormat: dateFormat
      yearRange: limitString

    $('input.datepicker').on 'click', ->
      console.warn "SiteView::datepicker.click: Refactor this event handler!"

      $(this).datepicker(
        showOn: 'focus'
        showAnim: ''
        changeMonth: true
        changeYear: true
        dateFormat: dateFormat
        yearRange: limitString).click(->
        $(this).attr 'value', ''
        return
      ).focus()
      return

    $('input.datepicker_nofuture').on 'click', ->
      console.warn "SiteView::datetimepicker_nofuture.click: Refactor this event handler!"

      $(this).datepicker(
        showOn: 'focus'
        showAnim: ''
        changeMonth: true
        changeYear: true
        maxDate: curDate
        dateFormat: dateFormat
        yearRange: limitString).click(->
        $(this).attr 'value', ''
        return
      ).focus()
      return

    $('input.datepicker_2months').on 'click', ->
      console.warn "SiteView::datetimepicker_2months.click: Refactor this event handler!"

      $(this).datepicker(
        showOn: 'focus'
        showAnim: ''
        changeMonth: true
        changeYear: true
        maxDate: '+0d'
        numberOfMonths: 2
        dateFormat: dateFormat
        yearRange: limitString).click(->
        $(this).attr 'value', ''
        return
      ).focus()
      return

    $('input.datetimepicker_nofuture').on 'click', ->
      console.warn "SiteView::datetimepicker_nofuture.click: Refactor this event handler!"

      $(this).datetimepicker(
        showOn: 'focus'
        showAnim: ''
        changeMonth: true
        changeYear: true
        maxDate: curDate
        dateFormat: dateFormat
        yearRange: limitString
        timeFormat: 'HH:mm'
        beforeShow: ->
          setTimeout (->
            $('.ui-datepicker').css 'z-index', 99999999999999
            return
          ), 0
          return
      ).click(->
        $(this).attr 'value', ''
        return
      ).focus()
      return


  init_referencedefinition: =>
    ###
     * Initialize reference definition selection
     * XXX: When is this used?
    ###
    console.debug "SiteView::init_referencedefinition"

    if $('#ReferenceDefinition:list').val() != ''
      console.warn "SiteView::init_referencedefinition: Refactor this method!"
      $('#ReferenceDefinition:list').change()


  init_department_filtering: =>
    ###
     * Initialize department filtering (when enabled in Setup)
     *
     * This function checks if the cookie 'filter_by_department_info' is
     * available. If the cookie exists, do nothing, if the cookie has not been
     * created yet, checks the selected department in the checkbox group and
     * creates the cookie with the UID of the first department. If cookie value
     * "dep_filter_disabled" is true, it means the user is admin and filtering
     * is disabled.
    ###
    console.debug "SiteView::init_department_filtering"

    cookie_val = @read_cookie(@department_filter_cookie)
    if cookie_val == null or cookie_val == ''
      dep_uid = $('input[name^=chb_deps_]:checkbox:visible:first').val()
      @set_cookie @department_filter_cookie, dep_uid

    dep_filter_disabled = @read_cookie @department_filter_disabled_cookie
    if dep_filter_disabled == 'true' or dep_filter_disabled == '"true"'
      $('#admin_dep_filter_enabled').prop 'checked', true

    return


  ### METHODS ###

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


  portalAlert: (html) =>
    ###
     * BBB: Use portal_alert
    ###
    console.warn "SiteView::portalAlert: Please use portal_alert method instead."
    @portal_alert html


  portal_alert: (html) =>
    ###
     * Display a portal alert box
    ###
    console.debug "SiteView::portal_alert"

    alerts = $('#portal-alert')

    if alerts.length == 0
      $('#portal-header').append "<div id='portal-alert' style='display:none'><div class='portal-alert-item'>#{html}</div></div>"
    else
      alerts.append "<div class='portal-alert-item'>#{html}</div>"
    alerts.fadeIn()
    return


  log: (message) =>
    ###
     * Log message via bika.lims.log
    ###
    console.debug "SiteView::log: message=#{message}"

    # XXX: This should actually log via XHR to the server, but seem to not work.
    window.bika.lims.log message


  readCookie: (cname) =>
    ###
     * BBB: Use read_cookie
    ###
    console.warn "SiteView::readCookie: Please use read_cookie method instead."
    @read_cookie cname


  read_cookie: (cname) =>
    ###
     * Read cookie value
    ###
    console.debug "SiteView::read_cookie:#{cname}"
    name = cname + '='
    ca = document.cookie.split ';'
    i = 0
    while i < ca.length
      c = ca[i]
      while c.charAt(0) == ' '
        c = c.substring(1)
      if c.indexOf(name) == 0
        return c.substring(name.length, c.length)
      i++
    return null


  setCookie: (cname, cvalue) =>
    ###
     * BBB: Use set_cookie
    ###
    console.warn "SiteView::setCookie: Please use set_cookie method instead."
    @set_cookie cname, cvalue


  set_cookie: (cname, cvalue) =>
    ###
     * Read cookie value
    ###
    console.debug "SiteView::set_cookie:cname=#{cname}, cvalue=#{cvalue}"
    d = new Date
    d.setTime d.getTime() + 1 * 24 * 60 * 60 * 1000
    expires = 'expires=' + d.toUTCString()
    document.cookie = cname + '=' + cvalue + ';' + expires + ';path=/'
    return


  notificationPanel: (data, mode) =>
    ###
     * BBB: Use notify_in_panel
    ###
    console.warn "SiteView::notificationPanel: Please use notfiy_in_panel method instead."
    @notify_in_panel data, mode


  notify_in_panel: (data, mode) =>
    ###
     * Render an alert inside the content panel, e.g.in autosave of ARView
    ###
    console.debug "SiteView::notify_in_panel:data=#{data}, mode=#{mode}"

    $('#panel-notification').remove()
    html = "<div id='panel-notification' style='display:none'><div class='#{mode}-notification-item'>#{data}</div></div>"

    $('div#viewlet-above-content-title').append html
    $('#panel-notification').fadeIn 'slow', 'linear', ->
      setTimeout (->
        $('#panel-notification').fadeOut 'slow', 'linear'
        return
      ), 3000
      return
    return


  start_spinner: =>
    ###
     * Start Spinner Overlay
    ###
    console.debug "SiteView::start_spinner"

    # increase the counter
    @counter++

    @timer = setTimeout (=>
      if @counter > 0
        @spinner.show 'fast'
      return
    ), 500

    return


  stop_spinner: =>
    ###
     * Stop Spinner Overlay
    ###
    console.debug "SiteView::stop_spinner"

    # decrease the counter
    @counter--

    if @counter < 0
      @counter = 0
    if @counter == 0
      clearTimeout @timer
      @spinner.stop()
      @spinner.hide()
    return


  load_analysis_service_popup: (title, uid) =>
    ###
     * Load the analysis service popup
    ###
    console.debug "SiteView::show_analysis_service_popup:title=#{title}, uid=#{uid}"

    if !title or !uid
      console.warn "SiteView::load_analysis_service_popup: title and uid are mandatory"
      return

    dialog = $('<div></div>')
    dialog.load "#{@get_portal_url()}/analysisservice_popup",
      'service_title': title
      'analysis_uid': uid
      '_authenticator': @get_authenticator()
    .dialog
      width: 450
      height: 450
      closeText: @_('Close')
      resizable: true
      title: $(this).text()
    return


  filter_default_departments: (deps_element) =>
    ###
     * Keep the list of default departments in sync with the selected departments
     *
     * 1. Go to a labcontact and select departments
     * 2. The list of default departments is kept in sync with the selection
    ###
    console.debug "SiteView::filter_default_departments"

    def_deps = $("select[name='DefaultDepartment']")[0]
    def_deps.options.length = 0
    null_opt = document.createElement('option')
    null_opt.text = ''
    null_opt.value = ''
    null_opt.selected = 'selected'
    def_deps.add null_opt

    #Adding selected deps
    $('option:selected', deps_element).each ->
      option = document.createElement('option')
      option.text = $(this).text()
      option.value = $(this).val()
      option.selected = 'selected'
      def_deps.add option
      return
    return


  ### EVENT HANDLER ###

  on_date_range_start_change: (event) =>
    ###
     * Eventhandler for Date Range Filtering
     *
     * 1. Go to Setup and enable advanced filter bar
     * 2. Set the start date of adv. filter bar, e.g. in AR listing
    ###
    console.debug "°°° SiteView::on_date_range_start_change °°°"

    el = event.currentTarget
    $el = $(el)

    # Set the min selectable end date to the start date
    date_element = $el.datepicker('getDate')
    brother = $el.siblings('.date_range_end')
    $(brother).datepicker 'option', 'minDate', date_element


  on_date_range_end_change: (event) =>
    ###
     * Eventhandler for Date Range Filtering
     *
     * 1. Go to Setup and enable advanced filter bar
     * 2. Set the start date of adv. filter bar, e.g. in AR listing
    ###
    console.debug "°°° SiteView::on_date_range_end_change °°°"

    el = event.currentTarget
    $el = $(el)

    # Set the max selectable start date to the end date
    date_element = $el.datepicker('getDate')
    brother = $el.siblings('.date_range_start')
    $(brother).datepicker 'option', 'maxDate', date_element


  on_department_list_change: (event) =>
    ###
     * Eventhandler for Department list on LabContacts
    ###
    console.debug "°°° SiteView::on_department_list_change °°°"

    el = event.currentTarget
    $el = $(el)

    # filter the list of default departments
    @filter_default_departments el


  on_department_filter_submit: (event) =>
    ###
     * Eventhandler for Department filter Portlet
     *
     * 1. Go to Setup and activate "Enable filtering by department"
     * 2. The portlet contains the id="department_filter_submit"
    ###
    console.debug "°°° SiteView::on_department_filter_submit °°°"

    el = event.currentTarget
    $el = $(el)

    if !$('#admin_dep_filter_enabled').is(':checked')
      deps = []
      $.each $('input[name^=chb_deps_]:checked'), ->
        deps.push $(this).val()
        return

      if deps.length == 0
        deps.push $('input[name^=chb_deps_]:checkbox:not(:checked):visible:first').val()

      @set_cookie @department_filter_cookie, deps.toString()

    window.location.reload true
    return


  on_admin_dep_filter_change: (event) =>
    ###
     * Eventhandler for Department filter Portlet
     *
     * 1. Go to Setup and activate "Enable filtering by department"
     * 2. The portlet contains the id="admin_dep_filter_enabled"
    ###
    console.debug "°°° SiteView::on_admin_dep_filter_change °°°"

    el = event.currentTarget
    $el = $(el)

    if $el.is(':checked')
      deps = []
      $.each $('input[name^=chb_deps_]:checkbox'), ->
        deps.push $(this).val()

      @set_cookie @department_filter_cookie, deps
      @set_cookie @department_filter_disabled_cookie, 'true'

      window.location.reload true
    else
      @set_cookie @department_filter_disabled_cookie, 'false'
      window.location.reload true
    return


  on_autocomplete_keydown: (event) =>
    ###
     * Eventhandler for Autocomplete fields
     *
     * XXX: Refactor if it is clear where this code is used!
    ###
    console.debug "°°° SiteView::on_autocomplete_keydown °°°"

    el = event.currentTarget
    $el = $(el)

    availableTags = $.parseJSON($('input.autocomplete').attr('voc'))

    split = (val) ->
      val.split /,\s*/

    extractLast = (term) ->
      split(term).pop()

    if event.keyCode == $.ui.keyCode.TAB and $el.autocomplete('instance').menu.active
      event.preventDefault()
    return

    $el.autocomplete
      minLength: 0
      source: (request, response) ->
        # delegate back to autocomplete, but extract the last term
        response $.ui.autocomplete.filter(availableTags, extractLast(request.term))
        return
      focus: ->
        # prevent value inserted on focus
        return false
      select: (event, ui) ->
        terms = split($el.val())
        # remove the current input
        terms.pop()
        # add the selected item
        terms.push ui.item.value
        # add placeholder to get the comma-and-space at the end
        terms.push ''
        @el.val terms.join(', ')
        return false


  on_at_integer_field_keyup: (event) =>
    ###
     * Eventhandler for AT integer fields
    ###
    console.debug "°°° SiteView::on_at_integer_field_keyup °°°"

    el = event.currentTarget
    $el = $(el)

    if /\D/g.test($el.val())
      $el.val $el.val().replace(/\D/g, '')
    return


  on_at_float_field_keyup: (event) =>
    ###
     * Eventhandler for AT float fields
    ###
    console.debug "°°° SiteView::on_at_float_field_keyup °°°"

    el = event.currentTarget
    $el = $(el)

    if /[^-.\d]/g.test($el.val())
      $el.val $el.val().replace(/[^.\d]/g, '')
    return


  on_numeric_field_paste: (event) =>
    ###
     * Eventhandler when the user pasted a value inside a numeric field.
    ###
    console.debug "°°° SiteView::on_numeric_field_paste °°°"

    el = event.currentTarget
    $el = $(el)

    # Wait (next cycle) for value popluation and replace commas.
    window.setTimeout (->
      $el.val $el.val().replace(',', '.')
      return
    ), 0
    return


  on_numeric_field_keypress: (event) =>
    ###
     * Eventhandler when the user pressed a key inside a numeric field.
    ###
    console.debug "°°° SiteView::on_numeric_field_keypress °°°"

    el = event.currentTarget
    $el = $(el)

    key = event.which
    isAllowedKey = @allowed_keys.join(',').match(new RegExp(key))

    # IE doesn't support indexOf
    # Some browsers just don't raise events for control keys. Easy. e.g. Safari backspace.
    if !key or 48 <= key and key <= 57 or isAllowedKey
      # Opera assigns values for control keys.
      # Wait (next cycle) for value popluation and replace commas.
      window.setTimeout (->
        $el.val $el.val().replace(',', '.')
        return
      ), 0
      return
    else
      event.preventDefault()
    return


  on_reference_definition_list_change: (event) =>
    ###
     * Eventhandler when the user clicked on the reference defintion dropdown.
     *
     * 1. Add a ReferenceDefintion at /bika_setup/bika_referencedefinitions
     * 2. Add a Supplier in /bika_setup/bika_suppliers
     * 3. Add a ReferenceSample in /bika_setup/bika_suppliers/supplier-1/portal_factory/ReferenceSample
     *
     * The dropdown with the id="ReferenceDefinition:list" is rendered there.
    ###
    console.debug "°°° SiteView::on_reference_definition_list_change °°°"

    el = event.currentTarget
    $el = $(el)

    authenticator = @get_authenticator()
    uid = $el.val()
    option = $el.children(':selected').html()

    if uid == ''
      # No reference definition selected;
      # render empty widget.
      $('#Blank').prop 'checked', false
      $('#Hazardous').prop 'checked', false
      $('.bika-listing-table').load 'referenceresults', '_authenticator': authenticator
      return

    if option.search(@_('(Blank)')) > -1 or option.search("(Blank)") > -1
      $('#Blank').prop 'checked', true
    else
      $('#Blank').prop 'checked', false

    if option.search(@_('(Hazardous)')) > -1 or option.search("(Hazardous)") > -1
      $('#Hazardous').prop 'checked', true
    else
      $('#Hazardous').prop 'checked', false

    $('.bika-listing-table').load 'referenceresults',
      '_authenticator': authenticator
      'uid': uid

    return


  on_analysis_service_title_click: (event) =>
    ###
     * Eventhandler when the user clicked on an Analysis Service Title
    ###
    console.debug "°°° SiteView::on_analysis_service_title_click °°°"

    el = event.currentTarget
    $el = $(el)

    title = $el.closest('td').find("span[class^='state']").html()
    uid = $el.parents('tr').attr('uid')

    @load_analysis_service_popup title, uid


  on_ajax_start: (event) =>
    ###
     * Eventhandler if an global Ajax Request started
    ###
    console.debug "°°° SiteView::on_ajax_start °°°"

    # start the loading spinner
    @start_spinner()


  on_ajax_end: (event) =>
    ###
     * Eventhandler if an global Ajax Request ended
    ###
    console.debug "°°° SiteView::on_ajax_end °°°"

    # stop the loading spinner
    @stop_spinner()


  on_ajax_error: (event, jqxhr, settings, thrownError) =>
    ###
     * Eventhandler if an global Ajax Request error
    ###
    console.debug "°°° SiteView::on_ajax_error °°°"

    # stop the loading spinner
    @stop_spinner()

    @log "Error at #{settings.url}: #{thrownError}"
