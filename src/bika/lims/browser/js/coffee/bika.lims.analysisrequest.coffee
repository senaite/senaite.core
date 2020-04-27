### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.coffee
###

###*
# Controller class for Analysis Request View/s
###

window.AnalysisRequestView = ->
  that = this

  ###*
  # Entry-point method for AnalysisRequestView
  ###

  transition_with_publication_spec = (event) ->
    # Pass the Publication Spec UID (if present) into the WorkflowAction handler
    # Force the transition to use the "workflow_action" url instead of content_status_modify.
    # TODO This should be using content_status_modify!  modifying the href is silly.
    event.preventDefault()
    href = event.currentTarget.href.replace('content_status_modify', 'workflow_action')
    element = $('#PublicationSpecification_uid')
    if element.length > 0
      href = href + '&PublicationSpecification=' + $(element).val()
    window.location.href = href
    return

  transition_schedule_sampling = ->

    ### Force the transition to use the "workflow_action" url instead of
    content_status_modify.
    It is not possible to abort a transition using "workflow_script_*".
    The recommended way is to set a guard instead.

    The guard expression should be able to look up a view to facilitate more complex guard code, but when a guard returns False the transition isn't even listed as available. It is listed after saving the fields.

    TODO This should be using content_status_modify!  modifying the href
    is silly.
    ###

    url = $('#workflow-transition-schedule_sampling').attr('href')
    if url
      new_url = url.replace('content_status_modify', 'workflow_action')
      $('#workflow-transition-schedule_sampling').attr 'href', new_url
      # When user clicks on the transition
      $('#workflow-transition-schedule_sampling').click ->
        date = $('#SamplingDate').val()
        sampler = $('#ScheduledSamplingSampler').val()
        if date != '' and date != undefined and date != null and sampler != '' and sampler != undefined and sampler != null
          window.location.href = new_url
        else
          message = ''
          if date == '' or date == undefined or date == null
            message = message + PMF('${name} is required for this action, please correct.', 'name': _('Sampling Date'))
          if sampler == '' or sampler == undefined or sampler == null
            if message != ''
              message = message + '<br/>'
            message = message + PMF('${name} is required, please correct.', 'name': _('\'Define the Sampler for the shceduled\''))
          if message != ''
            window.bika.lims.portalMessage message
        return
    return

  workflow_transition_sample = ->
    $('#workflow-transition-sample').click (event) ->
      event.preventDefault()
      date = $('#DateSampled').val()
      sampler = $('#Sampler').val()
      if date and sampler
        form = $('form[name=\'header_form\']')
        # this 'transition' key is scanned for in header_table.py/__call__
        form.append '<input type=\'hidden\' name=\'transition\' value=\'sample\'/>'
        form.submit()
      else
        message = ''
        if date == '' or date == undefined or date == null
          message = message + PMF('${name} is required, please correct.', 'name': _('Date Sampled'))
        if sampler == '' or sampler == undefined or sampler == null
          if message != ''
            message = message + '<br/>'
          message = message + PMF('${name} is required, please correct.', 'name': _('Sampler'))
        if message != ''
          window.bika.lims.portalMessage message
      return
    return

  that.load = ->
    # fires for all AR workflow transitions fired using the plone contentmenu workflow actions
    $('a[id^=\'workflow-transition\']').not('#workflow-transition-schedule_sampling').not('#workflow-transition-sample').click transition_with_publication_spec
    # fires AR workflow transitions when using the schedule samplign transition
    transition_schedule_sampling()
    return

  return

###*
# Controller class for Analysis Request View View
###

window.AnalysisRequestViewView = ->
  that = this

  ###*
  # Entry-point method for AnalysisRequestView
  ###

  resultsinterpretation_move_below = ->
    # By default show only the Results Interpretation for the whole AR, not Dept specific
    $('a.department-tab').click (e) ->
      e.preventDefault()
      uid = $(this).attr('data-uid')
      $('.department-area').not('[id="' + uid + '"]').hide()
      $('.department-area[id="' + uid + '"]').show()
      $('a.department-tab.selected').removeClass 'selected'
      $(this).addClass 'selected'
      return

    $('a.department-tab[data-uid="ResultsInterpretationDepts-general"]').click()
    #Remove buttons from TinyMCE
    setTimeout (->
      $('div.arresultsinterpretation-container .fieldTextFormat').remove()
      $('table.mceToolbar a.mce_image').remove()
      $('table.mceToolbar a.mce_code').remove()
      $('table.mceToolbar a.mce_save').hide()
      return
    ), 1500
    return

  parse_CCClist = ->

    ###*
    # It parses the CCContact-listing, where are located the CCContacts, and build the fieldvalue list.
    # @return: the builed field value -> "uid:TheValueOfuid1|uid:TheValueOfuid2..."
    ###

    fieldvalue = ''
    $('#CCContact-listing').children('.reference_multi_item').each (ii) ->
      if fieldvalue.length < 1
        fieldvalue = 'uid:' + $(this).attr('uid')
      else
        fieldvalue = fieldvalue + '|uid:' + $(this).attr('uid')
      return
    fieldvalue

  that.load = ->
    resultsinterpretation_move_below()
    return

  return

###*
# Controller class for Analysis Request Manage Results view
###

window.AnalysisRequestManageResultsView = ->
  that = this

  ###*
  # Entry-point method for AnalysisRequestManageResultsView
  ###

  that.load = ->
    # Set the analyst automatically when selected in the picklist
    $('.portaltype-analysisrequest .bika-listing-table td.Analyst select').change ->
      analyst = $(this).val()
      key = $(this).closest('tr').attr('keyword')
      obj_path = window.location.href.replace(window.portal_url, '')
      obj_path_split = obj_path.split('/')
      if obj_path_split.length > 4
        obj_path_split[obj_path_split.length - 1] = key
      else
        obj_path_split.push key
      obj_path = obj_path_split.join('/')
      $.ajax
        type: 'POST'
        url: window.portal_url + '/@@API/update'
        data:
          'obj_path': obj_path
          'Analyst': analyst
      return
    return

  return

###*
# Controller class for Analysis Request Analyses view
###

window.AnalysisRequestAnalysesView = ->
  that = this

  ###*
  # Entry-point method for AnalysisRequestAnalysesView
  ###

  ###*
  * This function validates specification inputs
  * @param {element} The input field from specifications (min, max, err)
  ###

  validate_spec_field_entry = (element) ->
    uid = $(element).attr('uid')
    min_element = $('[name=\'min\\.' + uid + '\\:records\']')
    max_element = $('[name=\'max\\.' + uid + '\\:records\']')
    error_element = $('[name=\'error\\.' + uid + '\\:records\']')
    min = parseFloat($(min_element).val(), 10)
    max = parseFloat($(max_element).val(), 10)
    error = parseFloat($(error_element).val(), 10)
    if $(element).attr('name') == $(min_element).attr('name')
      if isNaN(min)
        $(min_element).val ''
      else if !isNaN(max) and min > max
        $(max_element).val ''
    else if $(element).attr('name') == $(max_element).attr('name')
      if isNaN(max)
        $(max_element).val ''
      else if !isNaN(min) and max < min
        $(min_element).val ''
    else if $(element).attr('name') == $(error_element).attr('name')
      if isNaN(error) or error < 0 or error > 100
        $(error_element).val ''
    return

  ###*
  * This functions runs the logic needed after setting the checkbox of a
  * service.
  * @param {service_uid} the service uid checked.
  ###

  check_service = (service_uid) ->
    new_element = undefined
    element = undefined

    ### Check if this row is disabled. row_data has the attribute "disabled"
    as true if the analysis service has been submitted. So, in this case
    no further action will take place.

    "allow_edit" attribute in bika_listing displays the editable fields.
    Since the object keeps this attr even if the row is disabled; price,
    partition, min,max and error will be displayed (but disabled).
    ###

    row_data = $.parseJSON($('#' + service_uid + '_row_data').val())
    if row_data != '' and row_data != undefined and row_data != null
      if 'disabled' of row_data and row_data.disabled == true
        return
    # Add partition dropdown
    element = $('[name=\'Partition.' + service_uid + ':records\']')
    new_element = '' + '<select class=\'listing_select_entry\' ' + 'name=\'Partition.' + service_uid + ':records\' ' + 'field=\'Partition\' uid=\'' + service_uid + '\' ' + 'style=\'font-size: 100%\'>'
    $.each $('td.PartTitle'), (i, v) ->
      partid = $($(v).children()[1]).text()
      new_element = new_element + '<option value=\'' + partid + '\'>' + partid + '</option>'
      return
    new_element = new_element + '</select>'
    $(element).replaceWith new_element
    # Add price field
    logged_in_client = $('input[name=\'logged_in_client\']').val()
    if logged_in_client != '1'
      element = $('[name=\'Price.' + service_uid + ':records\']')
      new_element = '' + '<input class=\'listing_string_entry numeric\' ' + 'name=\'Price.' + service_uid + ':records\' ' + 'field=\'Price\' type=\'text\' uid=\'' + service_uid + '\' ' + 'autocomplete=\'off\' style=\'font-size: 100%\' size=\'5\' ' + 'value=\'' + $(element).val() + '\'>'
      $($(element).siblings()[1]).remove()
      $(element).replaceWith new_element
    # spec fields
    specfields = [
      'min'
      'max'
      'error'
    ]
    for i of specfields
      element = $('[name=\'' + specfields[i] + '.' + service_uid + ':records\']')
      new_element = '' + '<input class=\'listing_string_entry numeric\' type=\'text\' size=\'5\' ' + 'field=\'' + specfields[i] + '\' value=\'' + $(element).val() + '\' ' + 'name=\'' + specfields[i] + '.' + service_uid + ':records\' ' + 'uid=\'' + service_uid + '\' autocomplete=\'off\' style=\'font-size: 100%\'>'
      $(element).replaceWith new_element
    return

  ###*
  * This functions runs the logic needed after unsetting the checkbox of a
  * service.
  * @param {service_uid} the service uid unchecked.
  ###

  uncheck_service = (service_uid) ->
    new_element = undefined
    element = undefined
    element = $('[name=\'Partition.' + service_uid + ':records\']')
    new_element = '' + '<input type=\'hidden\' name=\'Partition.' + service_uid + ':records\' value=\'\'/>'
    $(element).replaceWith new_element
    logged_in_client = $('input[name=\'logged_in_client\']').val()
    if logged_in_client != '1'
      element = $('[name=\'Price.' + service_uid + ':records\']')
      $($(element).siblings()[0]).after '<span class=\'state-active state-active \'>' + $(element).val() + '</span>'
      new_element = '' + '<input type=\'hidden\' name=\'Price.' + service_uid + ':records\' value=\'' + $(element).val() + '\'/>'
      $(element).replaceWith new_element
    specfields = [
      'min'
      'max'
      'error'
    ]
    for i of specfields
      element = $('[name=\'' + specfields[i] + '.' + service_uid + ':records\']')
      new_element = '' + '<input type=\'hidden\' field=\'' + specfields[i] + '\' value=\'' + element.val() + '\' ' + 'name=\'' + specfields[i] + '.' + service_uid + ':records\' uid=\'' + service_uid + '\'>'
      $(element).replaceWith new_element
    return

  ###*
  * Given a selected service, this function selects the dependencies for
  * the selected service.
  * @param {String} dlg: The dialog to display (Not working!)
  * @param {DOM object} element: The checkbox object.
  * @param {Object} dep_services: A list of UIDs.
  * @return {None} nothing.
  ###

  add_Yes = (dlg, element, dep_services) ->
    service_uid = undefined
    dep_cb = undefined
    i = 0
    while i < dep_services.length
      service_uid = dep_services[i]
      dep_cb = $('#list_cb_' + service_uid)
      if dep_cb.length > 0
        if !$(dep_cb).prop('checked')
          check_service service_uid
          $('#list_cb_' + service_uid).prop 'checked', true
      else
        expand_category_for_service service_uid
      i++
    if dlg != false
      $(dlg).dialog 'close'
      $('#messagebox').remove()
    return

  add_No = (dlg, element) ->
    if $(element).prop('checked')
      uncheck_service $(element).attr('value')
      $(element).prop 'checked', false
    if dlg != false
      $(dlg).dialog 'close'
      $('#messagebox').remove()
    return

  ###*
  * Once a checkbox has been selected, this functions finds out which are
  * the dependencies and dependants related to it.
  * @param {elements} The selected element, a checkbox.
  * @param {auto_yes} A boolean. If 'true', the dependants and dependencies
  * will be automatically selected/unselected.
  ###

  calcdependencies = (elements, auto_yes) ->

    ###jshint validthis:true ###

    auto_yes = auto_yes or false
    jarn.i18n.loadCatalog 'senaite.core'
    _ = window.jarn.i18n.MessageFactory("senaite.core")
    dep = undefined
    i = undefined
    cb = undefined
    lims = window.bika.lims
    elements_i = 0
    while elements_i < elements.length
      dep_services = []
      # actionable services
      dep_titles = []
      element = elements[elements_i]
      service_uid = $(element).attr('value')
      # selecting a service; discover dependencies
      if $(element).prop('checked')
        Dependencies = lims.AnalysisService.Dependencies(service_uid)
        i = 0
        while i < Dependencies.length
          dep = Dependencies[i]
          if $('#list_cb_' + dep.Service_uid).prop('checked')
            i++
            continue
            # skip if checked already
          dep_services.push dep
          dep_titles.push dep.Service
          i++
        if dep_services.length > 0
          if auto_yes
            add_Yes false, element, dep_services
          else
            html = '<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>'
            html = html + _('<p>${service} requires the following services to be selected:</p>' + '<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>',
              service: $(element).attr('title')
              deps: dep_titles.join('<br/>'))
            html = html + '</div>'
            $('body').append html
            $('#messagebox').dialog
              width: 450
              resizable: false
              closeOnEscape: false
              buttons:
                yes: ->
                  add_Yes this, element, dep_services
                  return
                no: ->
                  add_No this, element
                  return
      else
        Dependants = lims.AnalysisService.Dependants(service_uid)
        i = 0
        while i < Dependants.length
          dep = Dependants[i]
          cb = $('#list_cb_' + dep)
          if cb.prop('checked')
            dep_titles.push dep.Service
            dep_services.push dep
          i++
        if dep_services.length > 0
          if auto_yes
            i = 0
            while i < dep_services.length
              dep = dep_services[i]
              service_uid = dep
              cb = $('#list_cb_' + service_uid)
              uncheck_service service_uid
              $(cb).prop 'checked', false
              i += 1
          else
            $('body').append '<div id=\'messagebox\' style=\'display:none\' title=\'' + _('Service dependencies') + '\'>' + _('<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>',
              service: $(element).attr('title')
              deps: dep_titles.join('<br/>')) + '</div>'
            $('#messagebox').dialog
              width: 450
              resizable: false
              closeOnEscape: false
              buttons:
                yes: ->
                  i = 0
                  while i < dep_services.length
                    dep = dep_services[i]
                    service_uid = dep
                    cb = $('#list_cb_' + dep)
                    $(cb).prop 'checked', false
                    uncheck_service dep
                    i += 1
                  $(this).dialog 'close'
                  $('#messagebox').remove()
                  return
                no: ->
                  service_uid = $(element).attr('value')
                  check_service service_uid
                  $(element).prop 'checked', true
                  $('#messagebox').remove()
                  $(this).dialog 'close'
                  return
      elements_i++
    return

  ###*
  * Given an analysis service UID, this function expands the category for
  * that service and selects it.
  * @param {String} serv_uid: uid of the analysis service.
  * @return {None} nothing.
  ###

  expand_category_for_service = (serv_uid) ->
    # Ajax getting the category from uid
    request_data = 
      catalog_name: 'uid_catalog'
      UID: serv_uid
      include_methods: 'getCategoryTitle'
    window.bika.lims.jsonapi_read request_data, (data) ->
      if data.objects.length < 1
        msg = '[bika.lims.analysisrequest.add_by_col.js] No data returned ' + 'while running "expand_category_for_service" for ' + serv_uid
        console.warn msg
        window.bika.lims.warning msg
      else
        cat_title = data.objects[0].getCategoryTitle
        # Expand category by uid and select the service
        element = $('th[cat=\'' + cat_title + '\']')
        #category_header_expand_handler(element, arnum, serv_uid);
        window.bika.lims.BikaListingTableView.category_header_expand_handler(element).done ->
          check_service serv_uid
          $('#list_cb_' + serv_uid).prop 'checked', true
          return
      return
    return

  that.load = ->
    return

  return
