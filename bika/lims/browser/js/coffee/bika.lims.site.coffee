### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.site.coffee
###


class window.SiteView

  load: =>
    console.debug "SiteView::load"

    # load translations
    jarn.i18n.loadCatalog 'senaite.core'
    @_ = window.jarn.i18n.MessageFactory("senaite.core")

    # initialize datepickers
    @init_datepickers()

    # initialze reference definition selection
    @init_referencedefinition()

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

  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
    ###
    console.debug "SiteView::bind_eventhandler"

    # ReferenceSample selection changed
    $("body").on "change", "#ReferenceDefinition\\:list", @on_reference_definition_list_change

    # Numeric field events
    $("body").on "keypress", ".numeric", @on_numeric_field_keypress
    $("body").on "paste", ".numeric", @on_numeric_field_paste

    # AT field events
    $("body").on "keyup", "input[name*='\\:int\'], .ArchetypesIntegerWidget input", @on_at_integer_field_keyup
    $("body").on "keyup","input[name*='\\:float\'], .ArchetypesDecimalWidget input", @on_at_float_field_keyup

    # Autocomplete events
    # XXX Where is this used?
    $("body").on "keydown", "input.autocomplete", @on_autocomplete_keydown

    $("body").on "click", "a.service_info", @on_service_info_click

    # Show loader on Ajax events
    $(document).on
      ajaxStart: ->
        $("body").addClass "loading"
        return
      ajaxStop: ->
        $("body").removeClass "loading"
        return
      ajaxError: ->
        $("body").removeClass "loading"
        return


  init_datepickers: =>
    ###
     * Initialize date pickers
     *
     * This is used for date pickers not bound to a DateTime widget
    ###
    console.debug "SiteView::init_datepickers"

    curDate = new Date
    y = curDate.getFullYear()
    limitString = '1900:' + y
    dateFormat = @_('date_format_short_datepicker')

    if dateFormat == 'date_format_short_datepicker'
      dateFormat = 'yy-mm-dd'

    # Initialize default settings for datepicker
    # See https://github.com/senaite/senaite.core/pull/1634
    lang = jarn.i18n.currentLanguage
    config = $.datepicker.regional[lang] or $.datepicker.regional['']
    $("input[class*='datepicker']").datepicker(
      Object.assign(config, {
        showOn: 'focus',
        showAnim: '',
        changeMonth: true,
        changeYear: true,
        dateFormat: dateFormat,
        numberOfMonths: 1,
        yearRange: limitString
        }
      )
    )

    # Date picker that displays two months
    $('input.datepicker_2months').datepicker("option", "numberOfMonths", 2)
    $('input.datepicker_2months').datepicker("option", "maxDate", "+0d")

    # Date picker with no future date selection available
    $('input.datepicker_nofuture').datepicker("option", "maxDate", curDate)

    # Date time picker with no future date time selection available
    $('input.datetimepicker_nofuture').datepicker("option", "maxDate", curDate)
    $('input.datetimepicker_nofuture').datepicker("option", "timeFormat", "HH:mm")


  init_referencedefinition: =>
    ###
     * Initialize reference definition selection
     * XXX: When is this used?
    ###
    console.debug "SiteView::init_referencedefinition"

    if $('#ReferenceDefinition:list').val() != ''
      console.warn "SiteView::init_referencedefinition: Refactor this method!"
      $('#ReferenceDefinition:list').change()


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


  ### EVENT HANDLER ###

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


  on_service_info_click: (event) =>
    ###
     * Eventhandler when the service info icon was clicked
    ###
    console.debug "°°° SiteView::on_service_info_click °°°"
    event.preventDefault()
    el = event.currentTarget

    # https://jquerytools.github.io/documentation/overlay
    # https://github.com/plone/plone.app.jquerytools/blob/master/plone/app/jquerytools/browser/overlayhelpers.js
    $(el).prepOverlay
      subtype: "ajax"
      width: '70%'
      filter: '#content>*:not(div#portal-column-content)'
      config:
        closeOnClick: yes
        closeOnEsc: yes
        onBeforeLoad: (event) ->
          overlay = this.getOverlay()
          overlay.draggable()
        onLoad: (event) ->
          # manually dispatch the DOMContentLoaded event, so that the ReactJS
          # component loads
          event = new Event "DOMContentLoaded", {}
          window.document.dispatchEvent(event)

    # workaround un-understandable overlay api
    $(el).click()
