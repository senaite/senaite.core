### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add.coffee
###


class window.AnalysisRequestAdd

  load: =>
    console.debug "AnalysisRequestAdd::load"

    # load translations
    jarn.i18n.loadCatalog 'senaite.core'
    @_ = window.jarn.i18n.MessageFactory("senaite.core")

    # disable browser autocomplete
    $('input[type=text]').prop 'autocomplete', 'off'

    # storage for global Bika settings
    @global_settings = {}

    # storage for mapping of fields to flush on_change
    @flush_settings = {}

    # services data snapshot from recalculate_records
    # returns a mapping of arnum -> services data
    @records_snapshot = {}

    # brain for already applied templates
    @applied_templates = {}

    # Remove the '.blurrable' class to avoid inline field validation
    $(".blurrable").removeClass("blurrable")

    # bind the event handler to the elements
    @bind_eventhandler()

    # N.B.: The new AR Add form handles File fields like this:
    # - File fields can carry more than one field (see init_file_fields)
    # - All uploaded files are extracted and added as attachments to the new created AR
    # - The file field itself (Plone) will stay empty therefore
    @init_file_fields()

    # get the global settings on load
    @get_global_settings()

    # get the flush settings
    @get_flush_settings()

    # recalculate records on load (needed for AR copies)
    @recalculate_records()

    # always recalculate prices in the first run
    @recalculate_prices()

    # return a reference to the instance
    return @


  ### METHODS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the body and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "AnalysisRequestAdd::bind_eventhandler"
    # Categories header clicked
    $("body").on "click", ".service-listing-header", @on_service_listing_header_click
    # Category toggle button clicked
    $("body").on "click", "tr.category", @on_service_category_click
    # Save button clicked
    $("body").on "click", "[name='save_button']", @on_form_submit
    # Composite Checkbox clicked
    $("body").on "click", "tr[fieldname=Composite] input[type='checkbox']", @recalculate_records
    # InvoiceExclude Checkbox clicked
    $("body").on "click", "tr[fieldname=InvoiceExclude] input[type='checkbox']", @recalculate_records
    # Analysis Checkbox clicked
    $("body").on "click", "tr[fieldname=Analyses] input[type='checkbox']", @on_analysis_checkbox_click
    # Generic onchange event handler for reference fields
    $("body").on "selected change" , "input[type='text'].referencewidget", @on_referencefield_value_changed

    # Analysis Specification changed
    $("body").on "change", "input.min", @on_analysis_specification_changed
    $("body").on "change", "input.max", @on_analysis_specification_changed
    $("body").on "change", "input.warn_min", @on_analysis_specification_changed
    $("body").on "change", "input.warn_max", @on_analysis_specification_changed
    # Analysis lock button clicked
    $("body").on "click", ".service-lockbtn", @on_analysis_lock_button_click
    # Analysis info button clicked
    $("body").on "click", ".service-infobtn", @on_analysis_details_click
    # Analysis Template changed
    $("body").on "selected change", "tr[fieldname=Template] input[type='text']", @on_analysis_template_changed
    # Analysis Profile selected
    $("body").on "selected", "tr[fieldname=Profiles] input[type='text']", @on_analysis_profile_selected
    # Analysis Profile deselected
    $("body").on "click", "tr[fieldname=Profiles] img.deletebtn", @on_analysis_profile_removed
    # Copy button clicked
    $("body").on "click", "img.copybutton", @on_copy_button_click

    ### internal events ###

    # handle value changes in the form
    $(this).on "form:changed", @debounce @recalculate_records, 1500
    # recalculate prices after services changed
    $(this).on "services:changed", @debounce @recalculate_prices, 3000
    # update form from records after the data changed
    $(this).on "data:updated", @debounce @update_form
    # hide open service info after data changed
    $(this).on "data:updated", @debounce @hide_all_service_info
    # handle Ajax events
    $(this).on "ajax:start", @on_ajax_start
    $(this).on "ajax:end", @on_ajax_end


  debounce: (func, threshold, execAsap) =>
    ###
     * Debounce a function call
     * See: https://coffeescript-cookbook.github.io/chapters/functions/debounce
    ###
    timeout = null

    return (args...) ->
      obj = this
      delayed = ->
        func.apply(obj, args) unless execAsap
        timeout = null
      if timeout
        clearTimeout(timeout)
      else if (execAsap)
        func.apply(obj, args)
      timeout = setTimeout(delayed, threshold || 300)


  template_dialog: (template_id, context, buttons) =>
    ###
     * Render the content of a Handlebars template in a jQuery UID dialog
       [1] http://handlebarsjs.com/
       [2] https://jqueryui.com/dialog/
    ###

    # prepare the buttons
    if not buttons?
      buttons = {}
      buttons[@_("Yes")] = ->
        # trigger 'yes' event
        $(@).trigger "yes"
        $(@).dialog "close"
      buttons[@_("No")] = ->
        # trigger 'no' event
        $(@).trigger "no"
        $(@).dialog "close"

    # render the Handlebars template
    content = @render_template template_id, context

    # render the dialog box
    $(content).dialog
      width: 450
      resizable: no
      closeOnEscape: no
      buttons: buttons
      open: (event, ui) ->
        # Hide the X button on the top right border
        $(".ui-dialog-titlebar-close").hide()


  render_template: (template_id, context) =>
    ###
     * Render Handlebars JS template
    ###

    # get the template by ID
    source = $("##{template_id}").html()
    return unless source
    # Compile the handlebars template
    template = Handlebars.compile(source)
    # Render the template with the given context
    content = template(context)
    return content


  get_global_settings: =>
    ###
     * Submit all form values to the server to recalculate the records
    ###
    @ajax_post_form("get_global_settings").done (settings) ->
      console.debug "Global Settings:", settings
      # remember the global settings
      @global_settings = settings
      # trigger event for whom it might concern
      $(@).trigger "settings:updated", settings


  get_flush_settings: =>
    ###
     * Retrieve the flush settings
    ###
    @ajax_post_form("get_flush_settings").done (settings) ->
      console.debug "Flush settings:", settings
      @flush_settings = settings
      $(@).trigger "flush_settings:updated", settings


  recalculate_records: =>
    ###
     * Submit all form values to the server to recalculate the records
    ###
    @ajax_post_form("recalculate_records").done (records) ->
      console.debug "Recalculate Analyses: Records=", records
      # remember a services snapshot
      @records_snapshot = records
      # trigger event for whom it might concern
      $(@).trigger "data:updated", records


  recalculate_prices: =>
    ###
     * Submit all form values to the server to recalculate the prices of all columns
    ###

    if @global_settings.show_prices is false
      console.debug "*** Skipping Price calculation ***"
      return

    @ajax_post_form("recalculate_prices").done (data) ->
      console.debug "Recalculate Prices Data=", data
      for own arnum, prices of data
        $("#discount-#{arnum}").text prices.discount
        $("#subtotal-#{arnum}").text prices.subtotal
        $("#vat-#{arnum}").text prices.vat
        $("#total-#{arnum}").text prices.total
      # trigger event for whom it might concern
      $(@).trigger "prices:updated", data


  update_form: (event, records) =>
    ###
     * Update form according to the server data
    ###
    console.debug "*** update_form ***"

    me = this

    # initially hide all lock icons
    $(".service-lockbtn").hide()

    # set all values for one record (a single column in the AR Add form)
    $.each records, (arnum, record) ->

      # Apply the values generically, but those to be handled differently
      discard = ["service_metadata", "specification_metadata", "template_metadata"]
      $.each record, (name, metadata) ->
        # Discard those fields that will be handled differently and those that
        # do not contain explicit object metadata (e.g service_to_specification)
        if name in discard or !name.endsWith("_metadata")
          return
        $.each metadata, (uid, obj_info) ->
          me.apply_field_value arnum, obj_info

      # set services
      $.each record.service_metadata, (uid, metadata) ->
        # lock icon (to be displayed when the service cannot be deselected)
        lock = $("##{uid}-#{arnum}-lockbtn")
        # service is included in a profile
        if uid of record.service_to_profiles
          lock.show()
        # service is part of the template
        # if uid of record.service_to_templates
        #   lock.show()

        # select the service
        me.set_service arnum, uid, yes

      # set template
      $.each record.template_metadata, (uid, template) ->
        me.set_template arnum, template

      # set specification
      $.each record.specification_metadata, (uid, spec) ->
        $.each spec.specifications, (uid, service_spec) ->
          me.set_service_spec arnum, uid, service_spec

      # handle unmet dependencies, one at a time
      $.each record.unmet_dependencies, (uid, dependencies) ->
        service = record.service_metadata[uid]

        context =
          "service": service
          "dependencies": dependencies

        dialog = me.template_dialog "dependency-add-template", context

        dialog.on "yes", ->
          # select the services
          $.each dependencies, (index, service) ->
            me.set_service arnum, service.uid, yes
          # trigger form:changed event
          $(me).trigger "form:changed"
        dialog.on "no", ->
          # deselect the dependant service
          me.set_service arnum, uid, no
          # trigger form:changed event
          $(me).trigger "form:changed"

        # break the iteration after the first loop to avoid multiple dialogs.
        return false


  get_portal_url: =>
    ###
     * Return the portal url (calculated in code)
    ###
    url = $("input[name=portal_url]").val()
    return url


  get_base_url: =>
    ###
     * Return the current (relative) base url
    ###
    base_url = window.location.href
    if base_url.search("/portal_factory") >= 0
      return base_url.split("/portal_factory")[0]
    return base_url.split("/ar_add")[0]


  get_authenticator: =>
    ###
     * Get the authenticator value
    ###
    return $("input[name='_authenticator']").val()


  get_form: =>
    ###
     * Return the form element
    ###
    return $("#analysisrequest_add_form")


  get_fields: (arnum) =>
    ###
     * Get all fields of the form
    ###
    form = @get_form()

    fields_selector = "tr[fieldname] td[arnum] input"
    if arnum?
      fields_selector = "tr[fieldname] td[arnum=#{arnum}] input"
    fields = $(fields_selector, form)
    return fields


  get_field_by_id: (id, arnum) =>
    ###
     * Query the field by id
    ###

    # split the fieldname from the suffix
    [name, suffix] = id.split "_"

    # append the arnum
    field_id = "#{name}-#{arnum}"

    # append the suffix if it is there
    if suffix?
      field_id = "#{field_id}_#{suffix}"

    # prepend a hash if it is not there
    if not id.startsWith "#"
      field_id = "##{field_id}"

    console.debug "get_field_by_id: $(#{field_id})"
    # query the field
    return $(field_id)


  typeIsArray = Array.isArray || (value) ->
    ###
     * Returns if the given value is an array
     * Taken from: https://coffeescript-cookbook.github.io/chapters/arrays/check-type-is-array
    ###
    return {}.toString.call( value ) is '[object Array]'


  apply_field_value: (arnum, record) ->
    ###
     * Applies the value for the given record, by setting values and applying
     * search filters to dependents
    ###
    me = this
    title = record.title
    console.debug "apply_field_value: arnum=#{arnum} record=#{title}"

    # Set default values to dependents
    me.apply_dependent_values arnum, record

    # Apply search filters to other fields
    me.apply_dependent_filter_queries record, arnum


  apply_dependent_values: (arnum, record) ->
    ###
     * Sets default field values to dependents
    ###
    me = this
    $.each record.field_values, (field_name, values) ->
      me.apply_dependent_value arnum, field_name, values


  apply_dependent_value: (arnum, field_name, values) ->
    ###
     * Apply search filters to dependendents
    ###
    me = this
    values_json = $.toJSON values
    field = $("#" + field_name + "-#{arnum}")

    if values.if_empty? and values.if_empty is true
      # Set the value if the field is empty only
      if field.val()
        return

    console.debug "apply_dependent_value: field_name=#{field_name} field_values=#{values_json}"

    if values.uid? and values.title?
      # This is a reference field
      me.set_reference_field field, values.uid, values.title

    else if values.value?
      # This is a normal input field
      if typeof values.value == "boolean"
        field.prop "checked", values.value
      else
        field.val values.value

    else if typeIsArray values
      # This is a multi field (e.g. CCContact)
      $.each values, (index, item) ->
        me.apply_dependent_value arnum, field_name, item


  apply_dependent_filter_queries: (record, arnum) ->
    ###
     * Apply search filters to dependents
    ###
    me = this
    $.each record.filter_queries, (field_name, query) ->
      field = $("#" + field_name + "-#{arnum}")
      me.set_reference_field_query field, query


  flush_fields_for: (field_name, arnum) ->
    ###
     * Flush dependant fields
    ###
    me = this
    field_ids = @flush_settings[field_name]
    $.each @flush_settings[field_name], (index, id) ->
      console.debug "flushing: id=#{id}"
      field = $("##{id}-#{arnum}")
      me.flush_reference_field field


  flush_reference_field: (field) ->
    ###
     * Empty the reference field and restore the search query
    ###

    catalog_name = field.attr "catalog_name"
    return unless catalog_name

    # flush values
    field.val("")
    $("input[type=hidden]", field.parent()).val("")
    $(".multiValued-listing", field.parent()).empty()

    # restore the original search query
    @reset_reference_field_query field

  reset_reference_field_query: (field) =>
    ###
     * Restores the catalog search query for the given reference field
    ###
    catalog_name = field.attr "catalog_name"
    return unless catalog_name
    query = $.parseJSON field.attr "base_query"
    @set_reference_field_query field, query

  set_reference_field_query: (field, query, type="base_query") =>
    ###
     * Set the catalog search query for the given reference field
     * XXX This is lame! The field should provide a proper API.
    ###

    catalog_name = field.attr "catalog_name"
    return unless catalog_name

    # get the combogrid options
    options = $.parseJSON field.attr "combogrid_options"

    # prepare the new query url
    url = @get_base_url()
    url += "/#{options.url}"
    url += "?_authenticator=#{@get_authenticator()}"
    url += "&catalog_name=#{catalog_name}"
    url += "&colModel=#{$.toJSON options.colModel}"
    url += "&search_fields=#{$.toJSON options.search_fields}"
    url += "&discard_empty=#{$.toJSON options.discard_empty}"
    url += "&minLength=#{$.toJSON options.minLength}"

    # get the current query (either "base_query" or "search_query" attribute)
    catalog_query = $.parseJSON field.attr type
    # update this query with the passed in query
    $.extend catalog_query, query

    new_query = $.toJSON catalog_query
    console.debug "set_reference_field_query: query=#{new_query}"

    if type is 'base_query'
      url += "&base_query=#{new_query}"
      url += "&search_query=#{field.attr('search_query')}"
    else
      url += "&base_query=#{field.attr('base_query')}"
      url += "&search_query=#{new_query}"

    options.url = url
    options.force_all = "false"


    field.combogrid options
    field.attr "search_query", "{}"


  set_reference_field: (field, uid, title) =>
    ###
     * Set the value and the uid of a reference field
     * XXX This is lame! The field should handle this on data change.
    ###

    me = this
    $field = $(field)

    # If the field doesn't exist in the form, avoid trying to set it's values
    if ! $field.length
      console.debug "field #{field} does not exist, skip set_reference_field"
      return
    $parent = field.closest("div.field")
    fieldname = field.attr "name"

    console.debug "set_reference_field:: field=#{fieldname} uid=#{uid} title=#{title}"

    uids_field = $("input[type=hidden]", $parent)
    existing_uids = uids_field.val()

    # uid is already selected
    if existing_uids.indexOf(uid) >= 0
      return

    # nothing in the field -> uid is the first entry
    if existing_uids.length == 0
      uids_field.val uid
    else
      # append to the list
      uids = uids_field.val().split(",")
      uids.push uid
      uids_field.val uids.join ","

    # set the title as the value
    $field.val title

    # handle multivalued reference fields
    mvl = $(".multiValued-listing", $parent)
    if mvl.length > 0
      portal_url = @get_portal_url()
      src = "#{portal_url}/++resource++bika.lims.images/delete.png"
      img = $("<img class='deletebtn'/>")
      img.attr "src", src
      img.attr "data-contact-title", title
      img.attr "fieldname", fieldname
      img.attr "uid", uid
      div = $("<div class='reference_multi_item'/>")
      div.attr "uid", uid
      div.append img
      div.append title
      mvl.append div
      $field.val("")


  get_reference_field_value: (field) =>
    ###
     * Return the value of a single/multi reference field
    ###
    $field = $(field)
    if $field.attr("multivalued") is undefined
      return []

    multivalued = $field.attr("multivalued") == "1"

    if not multivalued
      return [$field.val()]

    $parent = field.closest("div.field")
    uids = $("input[type=hidden]", $parent)?.val()
    if not uids
      return []

    return uids.split(",")


  set_template: (arnum, template) =>
    ###
     * Apply the template data to all fields of arnum
    ###

    me = this

    # apply template only once
    field = $("#Template-#{arnum}")
    uid = field.attr "uid"
    template_uid = template.uid

    if arnum of @applied_templates
      if @applied_templates[arnum] == template_uid
        console.debug "Skipping already applied template"
        return

    # remember the template for this ar
    @applied_templates[arnum] = template_uid

    # set the sample type
    field = $("#SampleType-#{arnum}")
    if not field.val()
      uid = template.sample_type_uid
      title = template.sample_type_title
      @flush_reference_field field
      @set_reference_field field, uid, title

    # set the sample point
    field = $("#SamplePoint-#{arnum}")
    if not field.val()
      uid = template.sample_point_uid
      title = template.sample_point_title
      @flush_reference_field field
      @set_reference_field field, uid, title

    # set the analysis profile
    field = $("#Profiles-#{arnum}")
    if not field.val()
      uid = template.analysis_profile_uid
      title = template.analysis_profile_title
      @flush_reference_field field
      @set_reference_field field, uid, title

    # set the remarks
    field = $("#Remarks-#{arnum}")
    if not field.val()
      field.text template.remarks

    # set the composite checkbox
    field = $("#Composite-#{arnum}")
    field.prop "checked", template.composite

    # set the services
    $.each template.service_uids, (index, uid) ->
      # select the service
      me.set_service arnum, uid, yes


  set_service: (arnum, uid, checked) =>
    ###
     * Select the checkbox of a service by UID
    ###
    console.debug "*** set_service::AR=#{arnum} UID=#{uid} checked=#{checked}"
    # get the service checkbox element
    el = $("td[fieldname='Analyses-#{arnum}'] #cb_#{arnum}_#{uid}")
    # avoid unneccessary event triggers if the checkbox status is unchanged
    if el.is(":checked") == checked
      return
    # select the checkbox
    el.prop "checked", checked
    # get the point of capture of this element
    poc = el.closest("tr[poc]").attr "poc"
    # make the element visible if the categories are visible
    if @is_poc_expanded poc
      el.closest("tr").addClass "visible"
    # trigger event for price recalculation
    $(@).trigger "services:changed"


  set_service_spec: (arnum, uid, spec) =>
    ###
     * Set the specification of the service
    ###
    console.debug "*** set_service_spec::AR=#{arnum} UID=#{uid} spec=", spec

    # get the service specifications
    el = $("div##{uid}-#{arnum}-specifications")

    min = $(".min", el)
    max = $(".max", el)
    warn_min = $(".warn_min", el)
    warn_max = $(".warn_max", el)

    min.val spec.min
    max.val spec.max
    warn_min.val spec.warn_min
    warn_max.val spec.warn_max


  get_service: (uid) =>
    ###
     * Fetch the service data from server by UID
    ###

    options =
      data:
        uid: uid
      processData: yes
      contentType: 'application/x-www-form-urlencoded; charset=UTF-8'

    @ajax_post_form("get_service", options).done (data) ->
      console.debug "get_service::data=", data


  hide_all_service_info: =>
    ###
     * hide all open service info boxes
    ###
    info = $("div.service-info")
    info.hide()


  is_poc_expanded: (poc) ->
    ###
     * Checks if the point of captures are visible
    ###
    el = $("tr.service-listing-header[poc=#{poc}]")
    return el.hasClass "visible"


  toggle_poc_categories: (poc, toggle) ->
    ###
     * Toggle all categories within a point of capture (lab/service)
     * :param poc: the point of capture (lab/field)
     * :param toggle: services visible if true
    ###

    if not toggle?
      toggle = not @is_poc_expanded(poc)

    # get the element
    el = $("tr[data-poc=#{poc}]")
    # all categories of this poc
    categories = $("tr.category.#{poc}")
    # all services of this poc
    services = $("tr.service.#{poc}")
    # all checked services
    services_checked = $("input[type=checkbox]:checked", services)
    toggle_buttons = $(".service-category-toggle")

    if toggle
      el.addClass "visible"
      categories.addClass "visible"
      services_checked.closest("tr").addClass "visible"
    else
      el.removeClass "visible"
      categories.removeClass "visible"
      categories.removeClass "expanded"
      services.removeClass "visible"
      services.removeClass "expanded"
      toggle_buttons.text("+")


  ### EVENT HANDLER ###

  on_referencefield_value_changed: (event) =>
    ###
     * Generic event handler for when a field value changes
    ###
    me = this
    el = event.currentTarget
    $el = $(el)
    has_value = @get_reference_field_value $el
    uid = $el.attr "uid"
    field_name = $el.closest("tr[fieldname]").attr "fieldname"
    arnum = $el.closest("[arnum]").attr "arnum"
    if field_name in ["Template", "Profiles"]
      # These fields have it's own event handler
      return

    console.debug "°°° on_referencefield_value_changed: field_name=#{field_name} arnum=#{arnum} °°°"

    # Flush depending fields
    me.flush_fields_for field_name, arnum

    # Manually flush UID field if the field does not have a selected value
    if not has_value
      $("input[type=hidden]", $el.parent()).val("")

    # trigger form:changed event
    $(me).trigger "form:changed"


  on_analysis_specification_changed: (event) =>
    ###
     * Eventhandler when the specification of an analysis service changed
    ###
    console.debug "°°° on_analysis_specification_changed °°°"

    me = this

    # trigger form:changed event
    $(me).trigger "form:changed"


  on_analysis_details_click: (event) =>
    ###
     * Eventhandler when the user clicked on the info icon of a service.
    ###

    el = event.currentTarget
    $el = $(el)
    uid = $el.attr "uid"
    arnum = $el.closest("[arnum]").attr "arnum"
    console.debug "°°° on_analysis_column::UID=#{uid}°°°"

    info = $("div.service-info", $el.parent())
    info.empty()

    data = info.data "data"

    # extra data to extend to the template context
    extra =
      profiles: []
      templates: []
      specifications: []

    # get the current snapshot record for this column
    record = @records_snapshot[arnum]

    # inject profile info
    if uid of record.service_to_profiles
      profiles = record.service_to_profiles[uid]
      $.each profiles, (index, uid) ->
        extra["profiles"].push record.profiles_metadata[uid]

    # inject template info
    if uid of record.service_to_templates
      templates = record.service_to_templates[uid]
      $.each templates, (index, uid) ->
        extra["templates"].push record.template_metadata[uid]

    # inject specification info
    if uid of record.service_to_specifications
      specifications = record.service_to_specifications[uid]
      $.each specifications, (index, uid) ->
        extra["specifications"].push record.specification_metadata[uid]

    if not data
      @get_service(uid).done (data) ->
        context = $.extend({}, data, extra)
        template = @render_template "service-info", context
        info.append template
        info.data "data", context
        info.fadeIn()
    else
      context = $.extend({}, data, extra)
      template = @render_template "service-info", context
      info.append template
      info.fadeToggle()


  on_analysis_lock_button_click: (event) =>
    ###
     * Eventhandler when an Analysis Profile was removed.
    ###
    console.debug "°°° on_analysis_lock_button_click °°°"

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $el.attr "uid"
    arnum = $el.closest("[arnum]").attr "arnum"

    record = me.records_snapshot[arnum]

    context = {}
    context["service"] = record.service_metadata[uid]
    context["profiles"] = []
    context["templates"] = []

    # collect profiles
    if uid of record.service_to_profiles
      profile_uid = record.service_to_profiles[uid]
      context["profiles"].push record.profiles_metadata[profile_uid]

    # collect templates
    if uid of record.service_to_templates
      template_uid = record.service_to_templates[uid]
      context["templates"].push record.template_metadata[template_uid]

    buttons =
      OK: ->
        $(@).dialog "close"

    dialog = @template_dialog "service-dependant-template", context, buttons


  on_analysis_template_changed: (event) =>
    ###
     * Eventhandler when an Analysis Template was changed.
    ###

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $(el).attr "uid"
    val = $el.val()
    arnum = $el.closest("[arnum]").attr "arnum"
    has_template_selected = $el.val()
    console.debug "°°° on_analysis_template_change::UID=#{uid} Template=#{val}°°°"

    # remember the set uid to handle later removal
    if uid
      $el.attr "previous_uid", uid
    else
      uid = $el.attr "previous_uid"

    # deselect the template if the field is empty
    if not has_template_selected and uid
      # forget the applied template
      @applied_templates[arnum] = null

      # XXX manually flush UID field
      $("input[type=hidden]", $el.parent()).val("")

      record = @records_snapshot[arnum]
      template_metadata = record.template_metadata[uid]
      template_services = []

      # prepare a list of services used by the template with the given UID
      $.each record.template_to_services[uid], (index, uid) ->
        # service might be deselected before and thus, absent
        if uid of record.service_metadata
          template_services.push record.service_metadata[uid]

      if template_services.length
        context = {}
        context["template"] = template_metadata
        context["services"] = template_services

        dialog = @template_dialog "template-remove-template", context
        dialog.on "yes", ->
          # deselect the services
          $.each template_services, (index, service) ->
            me.set_service arnum, service.uid, no
          # trigger form:changed event
          $(me).trigger "form:changed"
        dialog.on "no", ->
          # trigger form:changed event
          $(me).trigger "form:changed"

      # deselect the profile coming from the template
      # XXX: This is crazy and need to get refactored!
      if template_metadata.analysis_profile_uid
        field = $("#Profiles-#{arnum}")

        # uid and title of the selected profile
        uid = template_metadata.analysis_profile_uid
        title = template_metadata.analysis_profile_title

        # get the parent field wrapper (field is only the input)
        $parent = field.closest("div.field")

        # search for the multi item and remove it
        item = $(".reference_multi_item[uid=#{uid}]", $parent)
        if item.length
          item.remove()
          # remove the uid from the hidden field
          uids_field = $("input[type=hidden]", $parent)
          existing_uids = uids_field.val().split(",")
          remove_index = existing_uids.indexOf(uid)
          if remove_index > -1
            existing_uids.splice remove_index, 1
          uids_field.val existing_uids.join ","

      # deselect the samplepoint
      if template_metadata.sample_point_uid
        field = $("#SamplePoint-#{arnum}")
        @flush_reference_field(field)

      # deselect the sampletype
      if template_metadata.sample_type_uid
        field = $("#SampleType-#{arnum}")
        @flush_reference_field(field)

      # flush the remarks field
      if template_metadata.remarks
        field = $("#Remarks-#{arnum}")
        field.text ""

      # reset the composite checkbox
      if template_metadata.composite
        field = $("#Composite-#{arnum}")
        field.prop "checked", no

    # trigger form:changed event
    $(me).trigger "form:changed"


  on_analysis_profile_selected: (event) =>
    ###
     * Eventhandler when an Analysis Profile was selected.
    ###
    console.debug "°°° on_analysis_profile_selected °°°"

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $(el).attr "uid"

    # trigger form:changed event
    $(me).trigger "form:changed"


  # Note: Context of callback bound to this object
  on_analysis_profile_removed: (event) =>
    ###
     * Eventhandler when an Analysis Profile was removed.
    ###
    console.debug "°°° on_analysis_profile_removed °°°"

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $el.attr "uid"
    arnum = $el.closest("[arnum]").attr "arnum"

    record = @records_snapshot[arnum]
    profile_metadata = record.profiles_metadata[uid]
    profile_services = []

    # prepare a list of services used by the profile with the given UID
    $.each record.profile_to_services[uid], (index, uid) ->
      profile_services.push record.service_metadata[uid]

    context = {}
    context["profile"] = profile_metadata
    context["services"] = profile_services

    me = this
    dialog = @template_dialog "profile-remove-template", context
    dialog.on "yes", ->
      # deselect the services
      $.each profile_services, (index, service) ->
        me.set_service arnum, service.uid, no
      # trigger form:changed event
      $(me).trigger "form:changed"
    dialog.on "no", ->
      # trigger form:changed event
      $(me).trigger "form:changed"


  on_analysis_checkbox_click: (event) =>
    ###
     * Eventhandler for Analysis Service Checkboxes.
    ###

    me = this
    el = event.currentTarget
    checked = el.checked
    $el = $(el)
    uid = $el.val()

    console.debug "°°° on_analysis_click::UID=#{uid} checked=#{checked}°°°"

    # trigger form:changed event
    $(me).trigger "form:changed"
    # trigger event for price recalculation
    $(me).trigger "services:changed"


  on_service_listing_header_click: (event) =>
    ###
     * Eventhandler for analysis service category header rows.
     * Toggles the visibility of all categories within this poc.
    ###
    $el = $(event.currentTarget)
    poc = $el.data("poc")
    visible = $el.hasClass("visible")
    toggle = not visible
    @toggle_poc_categories poc, toggle


  on_service_category_click: (event) =>
    ###
     * Eventhandler for analysis service category rows.
     * Toggles the visibility of all services within this category.
     * Selected services always stay visible.
    ###
    event.preventDefault()
    $el = $(event.currentTarget)
    poc = $el.attr("poc")
    $btn = $(".service-category-toggle", $el)

    expanded = $el.hasClass("expanded")
    category = $el.data "category"
    services = $("tr.#{poc}.#{category}")
    services_checked = $("input[type=checkbox]:checked", services)

    console.debug "°°° on_service_category_click: category=#{category} °°°"

    if expanded
      $btn.text("+")
      $el.removeClass "expanded"
      services.removeClass "visible"
      services.removeClass "expanded"
      services_checked.closest("tr").addClass("visible")
    else
      $btn.text("-")
      $el.addClass "expanded"
      services.addClass "visible"
      services.addClass "expanded"


  on_copy_button_click: (event) =>
    ###
     * Eventhandler for the field copy button per row.
     * Copies the value of the first field in this row to the remaining.
     * XXX Refactor
    ###
    console.debug "°°° on_copy_button_click °°°"

    me = this

    el = event.target
    $el = $(el)

    tr = $el.closest('tr')[0]
    $tr = $(tr)

    td1 = $(tr).find('td[arnum="0"]').first()
    $td1 = $(td1)

    ar_count = parseInt($('input[id="ar_count"]').val(), 10)
    return unless ar_count > 1

    # the record data of the first AR
    record_one = @records_snapshot[0]

    # ReferenceWidget cannot be simply copied, the combogrid dropdown widgets
    # don't cooperate and the multiValued div must be copied.
    if $(td1).find('.ArchetypesReferenceWidget').length > 0
      console.debug "-> Copy reference field"

      el = $(td1).find(".ArchetypesReferenceWidget")
      field = el.find("input[type=text]")
      uid = field.attr("uid")
      value = field.val()
      mvl = el.find(".multiValued-listing")

      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0

        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find(".ArchetypesReferenceWidget")
        _field = _el.find("input[type=text]")

        # flush the field completely
        me.flush_reference_field _field

        if mvl.length > 0
          # multi valued reference field
          $.each mvl.children(), (idx, item) ->
            uid = $(item).attr "uid"
            value = $(item).text()
            me.set_reference_field _field, uid, value
        else
          # single reference field
          me.set_reference_field _field, uid, value

        # notify that the field changed
        $(_field).trigger "change"

      # trigger form:changed event
      $(me).trigger "form:changed"
      return

    # Copy <input type="checkbox"> fields
    $td1.find("input[type=checkbox]").each (index, el) ->
      console.debug "-> Copy checkbox field"
      $el = $(el)
      checked = $el.prop "checked"
      # iterate over columns, starting from column 2
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type=checkbox]")[index]
        $(_el).prop "checked", checked
      # trigger event for price recalculation
      if $el.hasClass "analysisservice-cb"
        $(me).trigger "services:changed"

    # Copy <select> fields
    $td1.find("select").each (index, el) ->
      console.debug "-> Copy select field"
      $el = $(el)
      value = $el.val()
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("select")[index]
        $(_el).val value

    # Copy <input type="text"> fields
    $td1.find("input[type=text]").each (index, el) ->
      console.debug "-> Copy text field"
      $el = $(el)
      value = $el.val()
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type=text]")[index]
        $(_el).val value

    # Copy <textarea> fields
    $td1.find("textarea").each (index, el) ->
      console.debug "-> Copy textarea field"
      $el = $(el)
      value = $el.val()
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("textarea")[index]
        $(_el).val value

    # Copy <input type="radio"> fields
    $td1.find("input[type=radio]").each (index, el) ->
      console.debug "-> Copy radio field"
      $el = $(el)
      checked = $(el).is ":checked"
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type=radio]")[index]
        $(_el).prop "checked", checked

    # trigger form:changed event
    $(me).trigger "form:changed"


  # Note: Context of callback bound to this object
  ajax_post_form: (endpoint, options={}) =>
    ###
     * Ajax POST the form data to the given endpoint
    ###
    console.debug "°°° ajax_post_form::Endpoint=#{endpoint} °°°"
    # calculate the right form URL
    base_url = @get_base_url()
    url = "#{base_url}/ajax_ar_add/#{endpoint}"
    console.debug "Ajax POST to url #{url}"

    # extract the form data
    form = $("#analysisrequest_add_form")
    # form.serialize does not include file attachments
    # form_data = form.serialize()
    form_data = new FormData(form[0])

    # jQuery Ajax options
    ajax_options =
      url: url
      type: 'POST'
      data: form_data
      context: @
      cache: false
      dataType: 'json'  # data type we expect from the server
      processData: false
      contentType: false
      # contentType: 'application/x-www-form-urlencoded; charset=UTF-8'
      timeout: 600000  # 10 minutes timeout

    # Update Options
    $.extend(ajax_options, options)

    ### Execute the request ###

    # Notify Ajax start
    me = this
    $(me).trigger "ajax:start"
    $.ajax(ajax_options).always (data) ->
      # Always notify Ajax end
      $(me).trigger "ajax:end"
    .fail (request, status, error) ->
      msg = _("Sorry, an error occured: #{status}")
      window.bika.lims.portalMessage msg
      window.scroll 0, 0


  on_ajax_start: =>
    ###
     * Ajax request started
    ###
    console.debug "°°° on_ajax_start °°°"

    # deactivate the button
    button = $("input[name=save_button]")
    button.prop "disabled": yes
    button[0].value = _("Loading ...")


  on_ajax_end: =>
    ###
     * Ajax request finished
    ###
    console.debug "°°° on_ajax_end °°°"

    # reactivate the button
    button = $("input[name=save_button]")
    button.prop "disabled": no
    button[0].value = _("Save")


  # Note: Context of callback bound to this object
  on_form_submit: (event, callback) =>
    ###
     * Eventhandler for the form submit button.
     * Extracts and submits all form data asynchronous.
    ###
    console.debug "°°° on_form_submit °°°"
    event.preventDefault()
    me = this

    # get the right base url
    base_url = me.get_base_url()

    # remove all errors
    $("div.error").removeClass("error")
    $("div.fieldErrorBox").text("")

    # Ajax POST to the submit endpoint
    @ajax_post_form("submit").done (data) ->
      ###
      # data contains the following useful keys:
      # - errors: any errors which prevented the AR from being created
      #   these are displayed immediately and no further ation is taken
      # - destination: the URL to which we should redirect on success.
      #   This includes GET params for printing labels, so that we do not
      #   have to care about this here.
      ###

      if data['errors']
        msg = data.errors.message
        if msg isnt ""
          msg = "#{msg}<br/>"

        for fieldname of data.errors.fielderrors
          field = $("##{fieldname}")
          parent = field.parent "div.field"
          if field and parent
            parent.toggleClass "error"
            errorbox = parent.children("div.fieldErrorBox")
            message = data.errors.fielderrors[fieldname]
            errorbox.text message
            msg += "#{message}<br/>"

        window.bika.lims.portalMessage msg
        window.scroll 0, 0

      else if data['stickers']
        destination = base_url
        ars = data['stickers']
        stickertemplate = data['stickertemplate']
        q = '/sticker?autoprint=1&template=' + stickertemplate + '&items=' + ars.join(',')
        window.location.replace destination + q
      else
        window.location.replace base_url


  init_file_fields: =>
    me = this
    $('tr[fieldname] input[type="file"]').each (index, element) ->
      # Wrap the initial field into a div
      file_field = $(element)
      file_field.wrap "<div class='field'/>"
      file_field_div = file_field.parent()
      # Create and add an ADD Button on the fly
      add_btn_src = "#{window.portal_url}/++resource++bika.lims.images/add.png"
      add_btn = $("<img class='addbtn' style='cursor:pointer;' src='#{add_btn_src}' />")

      # bind ADD event handler
      add_btn.on "click", element, (event) ->
        me.file_addbtn_click event, element

      # Attach the Button into the same div container
      file_field_div.append add_btn

  file_addbtn_click: (event, element) ->
    # Clone the file field and wrap it into a div
    file_field = $(element).clone()
    file_field.val("")
    file_field.wrap "<div class='field'/>"
    file_field_div = file_field.parent()
    [name, arnum] = $(element).attr("name").split("-")

    # Get all existing input fields and their names
    holding_div = $(element).parent().parent()
    existing_file_fields = holding_div.find("input[type='file']")
    existing_file_field_names = existing_file_fields.map (index, element) ->
      $(element).attr("name")

    # Generate a new name for the field and ensure it is not taken by another field already
    counter = 0
    newfieldname = $(element).attr("name")
    while newfieldname in existing_file_field_names
      newfieldname = "#{name}_#{counter}-#{arnum}"
      counter++

    # set the new id, name
    file_field.attr("name", newfieldname)
    file_field.attr("id", newfieldname)

    # Create and add an DELETE Button on the fly
    del_btn_src = "#{window.portal_url}/++resource++bika.lims.images/delete.png"
    del_btn = $("<img class='delbtn' style='cursor:pointer;' src='#{del_btn_src}' />")

    # Bind an DELETE event handler
    del_btn.on "click", element, (event) ->
      $(this).parent().remove()

    # Attach the Button into the same div container
    file_field_div.append del_btn

    # Attach the new field to the outer div of the passed file field
    $(element).parent().parent().append file_field_div
