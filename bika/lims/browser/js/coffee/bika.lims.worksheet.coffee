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
    instrument_uid = template_instruments[template_uid]

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



class window.WorksheetAddAnalysesView
  ###
   * Controller class for Worksheet's add analyses view
  ###

  load: =>
    console.debug "WorksheetAddanalysesview::load"

    # bind the event handler to the elements
    @bind_eventhandler()


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


  get_listing_form_id: () =>
    ###
     * Returns the CSS ID of the analyses listing
    ###
    return "list"


  get_listing_form: () =>
    ###
     * Returns the analyses listing form element
    ###
    form_id = @get_listing_form_id()
    return $("form[id='#{form_id}']")


  filter_service_selector_by_category_uid: (category_uid) =>
    ###
     * Filters the service selector by category
    ###
    console.debug "WorksheetAddanalysesview::filter_service_selector_by_category_uid:#{category_uid}"

    form_id = @get_listing_form_id()
    select_name = "#{form_id}_FilterByService"
    $select = $("[name='#{select_name}']")

    base_url = @get_base_url()
    url = base_url.replace "/add_analyses", "/getServices"

    data =
      _authenticator: @get_authenticator()

    if category_uid isnt "any"
      data["getCategoryUID"] = category_uid

    @ajax_submit
      url: url
      data: data
      dataType: "json"
    .done (data) ->
      $select.empty()
      any_option = "<option value='any'>#{_('Any')}</option>"
      $select.append any_option
      $.each data, (index, item) ->
        uid = item[0]
        name = item[1]
        option = "<option value='#{uid}'>#{name}</option>"
        $select.append option


  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "WorksheetAddanalysesview::bind_eventhandler"

    # Category filter changed
    $("body").on "change", "[name='list_FilterByCategory']", @on_category_change

    # Search button clicked
    $("body").on "click", ".ws-analyses-search-button", @on_search_click


  ### EVENT HANDLER ###

  on_category_change: (event) =>
    ###
     * Eventhandler for category change
    ###
    console.debug "°°° WorksheetAddanalysesview::on_category_change °°°"

    # The select element for WS Template
    $el = $(event.currentTarget)

    # extract the category UID and filter the services box
    category_uid = $el.val()
    @filter_service_selector_by_category_uid category_uid


  on_search_click: (event) =>
    ###
     * Eventhandler for the search button
    ###
    console.debug "°°° WorksheetAddanalysesview::on_search_click °°°"

    # Prevent form submit
    event.preventDefault()

    form = @get_listing_form()
    form_id = @get_listing_form_id()

    filter_indexes = [
      "FilterByCategory"
      "FilterByService"
      "FilterByClient"
    ]

    # The filter elements (Category/Service/Client) belong to another form.
    # Therefore, we need to inject these values into the listing form as hidden
    # input fields.
    $.each filter_indexes, (index, filter) ->
      name = "#{form_id}_#{filter}"
      $el = $("select[name='#{name}']")
      value = $el.val()

      # get the corresponding input element of the listing form
      input = $("input[name='#{name}']", form)
      if input.length == 0
        form.append "<input name='#{name}' value='#{value}' type='hidden'/>"
        input = $("input[name='#{name}']", form)
      input.val value

      # omit the field if the value is set to any
      if value == "any"
         input.remove()

    # extract the data of the listing form and post it to the AddAnalysesView
    form_data = new FormData form[0]
    form_data.set "table_only", form_id

    @ajax_submit
      data: form_data
      processData: no  # do not transform to a query string
      contentType: no # do not set any content type header
    .done (data) ->
      $container = $("div.bika-listing-table-container", form)
      $data = $(data)
      if $data.find("tbody").length == 0
        $container.html "<div class='discreet info'>0 #{_('Results')}</div>"
      else
        $container.html data



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


################ REFACTOR FROM HERE ##############################


###*
# Controller class for Worksheet's manage results view
###

window.WorksheetManageResultsView = ->
  that = this

  portalMessage = (message) ->
    window.jarn.i18n.loadCatalog 'bika'
    _ = jarn.i18n.MessageFactory('bika')
    str = '<dl class=\'portalMessage info\'>' + '<dt>' + _('Info') + '</dt>' + '<dd><ul>' + message + '</ul></dd></dl>'
    $('.portalMessage').remove()
    $(str).appendTo '#viewlet-above-content'
    return

  loadRemarksEventHandlers = ->
    # On click, toggle the remarks field
    $('a.add-remark').click (e) ->
      e.preventDefault()
      rmks = $(this).closest('tr').next('tr').find('td.remarks')
      $(rmks).find('div.remarks-placeholder').toggle()
      return
    return

  loadDetectionLimitsEventHandlers = ->
    $('select[name^="DetectionLimit."]').change ->
      defdls = $(this).closest('td').find('input[id^="DefaultDLS."]').first().val()
      resfld = $(this).closest('tr').find('input[name^="Result."]')[0]
      uncfld = $(this).closest('tr').find('input[name^="Uncertainty."]')
      defdls = $.parseJSON(defdls)
      $(resfld).prop 'readonly', !defdls.manual
      if $(this).val() == '<'
        $(resfld).val defdls['min']
        # Inactivate uncertainty?
        if uncfld.length > 0
          $(uncfld).val ''
          $(uncfld).prop 'readonly', true
          $(uncfld).closest('td').children().hide()
      else if $(this).val() == '>'
        $(resfld).val defdls['max']
        # Inactivate uncertainty?
        if uncfld.length > 0
          $(uncfld).val ''
          $(uncfld).prop 'readonly', true
          $(uncfld).closest('td').children().hide()
      else
        $(resfld).val ''
        $(resfld).prop 'readonly', false
        # Activate uncertainty?
        if uncfld.length > 0
          $(uncfld).val ''
          $(uncfld).prop 'readonly', false
          $(uncfld).closest('td').children().show()
      # Maybe the result is used in calculations...
      $(resfld).change()
      return
    $('select[name^="DetectionLimit."]').change()
    return

  loadWideInterimsEventHandlers = ->
    $('#wideinterims_analyses').change ->
      $('#wideinterims_interims').html ''
      $('input[id^="wideinterim_' + $(this).val() + '"]').each (i, obj) ->
        itemval = '<option value="' + $(obj).attr('keyword') + '">' + $(obj).attr('name') + '</option>'
        $('#wideinterims_interims').append itemval
        return
      return
    $('#wideinterims_interims').change ->
      analysis = $('#wideinterims_analyses').val()
      interim = $(this).val()
      idinter = '#wideinterim_' + analysis + '_' + interim
      $('#wideinterims_value').val $(idinter).val()
      return
    $('#wideinterims_apply').click (event) ->
      event.preventDefault()
      analysis = $('#wideinterims_analyses').val()
      interim = $('#wideinterims_interims').val()
      $('tr[keyword="' + analysis + '"] input[field="' + interim + '"]').each (i, obj) ->
        if $('#wideinterims_empty').is(':checked')
          if $(this).val() == '' or $(this).val().match(/\d+/) == '0'
            $(this).val $('#wideinterims_value').val()
            $(this).change()
        else
          $(this).val $('#wideinterims_value').val()
          $(this).change()
        return
      return
    return

  ###*
  # Applies the rules and constraints to each analysis displayed in the
  # manage results view regarding to methods, instruments and results.
  # For example, this service is responsible of disabling the results field
  # if the analysis has no valid instrument available for the selected
  # method if the service don't allow manual entry of results. Another
  # example is that this service is responsible of populating the list of
  # instruments avialable for an analysis service when the user changes the
  # method to be used.
  # See docs/imm_results_entry_behavior.png for detailed information.
  ###

  initializeInstrumentsAndMethods = ->
    auids = []
    #/ Get all the analysis UIDs from this manage results table, cause
    # we'll need them to retrieve all the IMM constraints/rules to be
    # applied later.
    dictuids = $.parseJSON($('#item_data').val())
    $.each dictuids, (key, value) ->
      auids.push key
      return
    # Retrieve all the rules/constraints to be applied for each analysis
    # by using an ajax call. The json dictionary returned is assigned to
    # the variable mi_constraints for further use.
    # FUTURE: instead of an ajax call to retrieve the dictionary, embed
    #  the dictionary in a div when the bika_listing template is rendered.
    $.ajax(
      url: window.portal_url + '/get_method_instrument_constraints'
      type: 'POST'
      data:
        '_authenticator': $('input[name="_authenticator"]').val()
        'uids': $.toJSON(auids)
      dataType: 'json').done((data) ->
      # Save the constraints in the m_constraints variable
      mi_constraints = data
      $.each auids, (index, value) ->
        # Apply the constraints/rules to each analysis.
        load_analysis_method_constraint value, null
        return
      return
    ).fail ->
      window.bika.lims.log 'bika.lims.worksheet: Something went wrong while retrieving analysis-method-instrument constraints'
      return
    return

  ###*
  # Applies the constraints and rules to the specified analysis regarding to
  # the method specified. If method is null, the function assumes the rules
  # must apply for the currently selected method.
  # The function uses the variable mi_constraints to find out which is the
  # rule to be applied to the analysis and method specified.
  # See initializeInstrumentsAndMethods() function for further information
  # about the constraints and rules retrieval and assignment.
  # @param {string} analysis_uid - The Analysis UID
  # @param {string} method_uid - The Method UID. If null, uses the method
  #  that is currently selected for the specified analysis.
  ###

  load_analysis_method_constraint = (analysis_uid, method_uid) ->
    if method_uid == null
      # Assume to load the constraints for the currently selected method
      muid = $('select.listing_select_entry[field="Method"][uid="' + analysis_uid + '"]').val()
      muid = if muid then muid else ''
      load_analysis_method_constraint analysis_uid, muid
      return
    andict = mi_constraints[analysis_uid]
    if !andict
      return
    constraints = andict[method_uid]
    if !constraints or constraints.length < 7
      return
    m_selector = $('select.listing_select_entry[field="Method"][uid="' + analysis_uid + '"]')
    i_selector = $('select.listing_select_entry[field="Instrument"][uid="' + analysis_uid + '"]')
    # None option in method selector?
    $(m_selector).find('option[value=""]').remove()
    if constraints[1] == 1
      $(m_selector).prepend '<option value="">' + _('Not defined') + '</option>'
    # Select the method
    $(m_selector).val method_uid
    # Method selector visible?
    # 0: no, 1: yes, 2: label, 3: readonly
    $(m_selector).prop 'disabled', false
    $('.method-label[uid="' + analysis_uid + '"]').remove()
    if constraints[0] == 0
      $(m_selector).hide()
    else if constraints[0] == 1
      $(m_selector).show()
    else if constraints[0] == 2
      if andict.length > 1
        $(m_selector).hide()
        method_name = $(m_selector).find('option[value="' + method_uid + '"]').innerHtml()
        $(m_selector).after '<span class="method-label" uid="' + analysis_uid + '" href="#">' + method_name + '</span>'
    else if constraints[0] == 3
      #$(m_selector).prop('disabled', true);
      $(m_selector).show()
    # We are going to reload Instrument list.. Enable all disabled options from other Instrument lists which has the
    # same value as old value of this Instrument Selectbox.
    ins_old_val = $(i_selector).val()
    if ins_old_val and ins_old_val != ''
      $('table.bika-listing-table select.listing_select_entry[field="Instrument"][value!="' + ins_old_val + '"] option[value="' + ins_old_val + '"]').prop 'disabled', false
    # Populate instruments list
    $(i_selector).find('option').remove()
    if constraints[7]
      $.each constraints[7], (key, value) ->
        if is_ins_allowed(key)
          $(i_selector).append '<option value="' + key + '">' + value + '</option>'
        else
          $(i_selector).append '<option value="' + key + '" disabled="true">' + value + '</option>'
        return
    # None option in instrument selector?
    if constraints[3] == 1
      $(i_selector).prepend '<option selected="selected" value="">' + _('None') + '</option>'
    # Select the default instrument
    if is_ins_allowed(constraints[4])
      $(i_selector).val constraints[4]
      # Disable this Instrument in the other Instrument SelectBoxes
      $('table.bika-listing-table select.listing_select_entry[field="Instrument"][value!="' + constraints[4] + '"] option[value="' + constraints[4] + '"]').prop 'disabled', true
    # Instrument selector visible?
    if constraints[2] == 0
      $(i_selector).hide()
    else if constraints[2] == 1
      $(i_selector).show()
    # Allow to edit results?
    if constraints[5] == 0
      $('.interim input[uid="' + analysis_uid + '"]').val ''
      $('input[field="Result"][uid="' + analysis_uid + '"]').val ''
      $('.interim input[uid="' + analysis_uid + '"]').prop 'disabled', true
      $('input[field="Result"][uid="' + analysis_uid + '"]').prop 'disabled', true
    else if constraints[5] == 1
      $('.interim input[uid="' + analysis_uid + '"]').prop 'disabled', false
      $('input[field="Result"][uid="' + analysis_uid + '"]').prop 'disabled', false
    # Info/Warn message?
    $('.alert-instruments-invalid[uid="' + analysis_uid + '"]').remove()
    if constraints[6] and constraints[6] != ''
      $(i_selector).after '<img uid="' + analysis_uid + '" class="alert-instruments-invalid" src="' + window.portal_url + '/++resource++bika.lims.images/warning.png" title="' + constraints[6] + '")">'
    $('.amconstr[uid="' + analysis_uid + '"]').remove()
    #$(m_selector).before("<span style='font-weight:bold;font-family:courier;font-size:1.4em;' class='amconstr' uid='"+analysis_uid+"'>"+constraints[10]+"&nbsp;&nbsp;</span>");
    return

  loadHeaderEventsHandlers = ->
    $('.manage_results_header .analyst').change ->
      if $(this).val() == ''
        return false
      $.ajax
        type: 'POST'
        url: window.location.href.replace('/manage_results', '') + '/set_analyst'
        data:
          'value': $(this).val()
          '_authenticator': $('input[name="_authenticator"]').val()
        success: (data, textStatus, jqXHR) ->
          window.jarn.i18n.loadCatalog 'plone'
          _p = jarn.i18n.MessageFactory('plone')
          portalMessage _p('Changes saved.')
          return
      return
    # Change the results layout
    $('#resultslayout_form #resultslayout_button').hide()
    $('#resultslayout_form #resultslayout').change ->
      $('#resultslayout_form #resultslayout_button').click()
      return
    $('.manage_results_header .instrument').change ->
      $('#content-core .instrument-error').remove()
      instruid = $(this).val()
      if instruid == ''
        return false
      $.ajax
        type: 'POST'
        url: window.location.href.replace('/manage_results', '') + '/set_instrument'
        data:
          'value': instruid
          '_authenticator': $('input[name="_authenticator"]').val()
        success: (data, textStatus, jqXHR) ->
          window.jarn.i18n.loadCatalog 'plone'
          _p = jarn.i18n.MessageFactory('plone')
          portalMessage _p('Changes saved.')
          # Set the selected instrument to all the analyses which
          # that can be done using that instrument. The rest of
          # of the instrument picklist will not be changed
          $('select.listing_select_entry[field="Instrument"] option[value="' + instruid + '"]').parent().find('option[value="' + instruid + '"]').prop 'selected', false
          $('select.listing_select_entry[field="Instrument"] option[value="' + instruid + '"]').prop 'selected', true
          return
        error: (data, jqXHR, textStatus, errorThrown) ->
          $('.manage_results_header .instrument').closest('table').after '<div class=\'alert instrument-error\'>' + _('Unable to apply the selected instrument') + '</div>'
          false
      return
    return

  ###*
  # Change the instruments to be shown for an analysis when the method selected changes
  ###

  loadMethodEventHandlers = ->
    $('table.bika-listing-table select.listing_select_entry[field="Method"]').change ->
      auid = $(this).attr('uid')
      muid = $(this).val()
      load_analysis_method_constraint auid, muid
      return
    return

  ###*
  # If a new instrument is chosen for the analysis, disable this Instrument for the other analyses. Also, remove
  # the restriction of previous Instrument of this analysis to be chosen in the other analyses.
  ###

  loadInstrumentEventHandlers = ->
    $('table.bika-listing-table select.listing_select_entry[field="Instrument"]').on('focus', ->
      # First, getting the previous value
      previous = @value
      return
    ).change ->
      auid = $(this).attr('uid')
      iuid = $(this).val()
      # Disable New Instrument for rest of the analyses
      $('table.bika-listing-table select.listing_select_entry[field="Instrument"][value!="' + iuid + '"] option[value="' + iuid + '"]').prop 'disabled', true
      # Enable previous Instrument everywhere
      $('table.bika-listing-table select.listing_select_entry[field="Instrument"] option[value="' + previous + '"]').prop 'disabled', false
      # Enable 'None' option as well.
      $('table.bika-listing-table select.listing_select_entry[field="Instrument"] option[value=""]').prop 'disabled', false
      return
    return

  ###*
  # Check if the Instrument is allowed to appear in Instrument list of Analysis.
  # Returns true if multiple use of an Instrument is enabled for assigned Worksheet Template or UID is not in selected Instruments
  # @param {uid} ins_uid - UID of Instrument.
  ###

  is_ins_allowed = (uid) ->
    multiple_enabled = $('#instrument_multiple_use').attr('value')
    if multiple_enabled == 'True'
      return true
    else
      i_selectors = $('select.listing_select_entry[field="Instrument"]')
      i = 0
      while i < i_selectors.length
        if i_selectors[i].value == uid
          return false
        i++
    true

  that.load = ->
    # Remove empty options
    initializeInstrumentsAndMethods()
    loadHeaderEventsHandlers()
    loadMethodEventHandlers()
    # Manage the upper selection form for spread wide interim results values
    loadWideInterimsEventHandlers()
    loadRemarksEventHandlers()
    loadDetectionLimitsEventHandlers()
    loadInstrumentEventHandlers()
    return

  ###*
  # Stores the constraints regarding to methods and instrument assignments to
  # each analysis. The variable is filled in initializeInstrumentsAndMethods
  # and is used inside loadMethodEventHandlers.
  ###

  mi_constraints = null
  return
