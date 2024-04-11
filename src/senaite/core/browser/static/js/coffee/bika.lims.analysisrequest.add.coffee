### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add.coffee
###


class window.AnalysisRequestAdd

  load: =>
    console.debug "AnalysisRequestAdd::load"

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

    # manually deselected references
    # => keep track to avoid setting these fields with the default values
    @deselected_uids = {}

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

    # initialize service conditions (needed for AR copies)
    @init_service_conditions()

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
    # Composite Checkbox clicked
    $("body").on "click", "tr[fieldname=Composite] input[type='checkbox']", @recalculate_records
    # InvoiceExclude Checkbox clicked
    $("body").on "click", "tr[fieldname=InvoiceExclude] input[type='checkbox']", @recalculate_records
    # Analysis Checkbox clicked
    $("body").on "click", "tr[fieldname=Analyses] input[type='checkbox'].analysisservice-cb", @on_analysis_checkbox_click

    # Analysis lock button clicked
    $("body").on "click", ".service-lockbtn", @on_analysis_lock_button_click
    # Analysis info button clicked
    $("body").on "click", ".service-infobtn", @on_analysis_details_click
    # Copy button clicked
    $("body").on "click", "img.copybutton", @on_copy_button_click

    # Generic select/deselect event handler for reference fields
    $("body").on "select deselect" , "div.uidreferencefield textarea", @on_referencefield_value_changed

    # Analysis Template selected
    $("body").on "select", "tr[fieldname=Template] textarea", @on_analysis_template_selected
    # Analysis Template removed
    $("body").on "deselect", "tr[fieldname=Template] textarea", @on_analysis_template_removed

    # Analysis Profile selected
    $("body").on "select", "tr[fieldname=Profiles] textarea", @on_analysis_profile_selected
    # Analysis Profile deselected
    $("body").on "deselect", "tr[fieldname=Profiles] textarea", @on_analysis_profile_removed

    # Save button clicked
    $("body").on "click", "[name='save_button']", @on_form_submit
    # Save and copy button clicked
    $("body").on "click", "[name='save_and_copy_button']", @on_form_submit
    # Cancel button clicked
    $("body").on "click", "[name='cancel_button']", @on_cancel

    ### internal events ###

    # handle value changes in the form
    $(this).on "form:changed", @debounce @recalculate_records, 1000
    # recalculate prices after services changed
    $(this).on "services:changed", @debounce @recalculate_prices, 2000
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
      buttons[_t("Yes")] = ->
        # trigger 'yes' event
        $(@).trigger "yes"
        $(@).dialog "close"
      buttons[_t("No")] = ->
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
     * Fetch global settings from the setup, e.g. show_prices
    ###
    @ajax_post_form("get_global_settings").done (settings) ->
      console.debug "Global Settings:", settings
      # remember the global settings
      @global_settings = settings
      # trigger event for whom it might concern
      $(@).trigger "settings:updated", settings


  get_flush_settings: =>
    ###
     * Retrieve the flush settings mapping (field name -> list of other fields to flush)
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
     *
     * Records provided from the server (see ajax_recalculate_records)
    ###
    console.debug "*** update_form ***"

    me = this

    # initially hide all lock icons
    $(".service-lockbtn").hide()

    # set all values for one record (a single column in the AR Add form)
    $.each records, (arnum, record) ->

      # Apply the values generically, but those to be handled differently
      discard = ["service_metadata", "template_metadata"]
      $.each record, (name, metadata) ->
        # Discard those fields that will be handled differently and those that
        # do not contain explicit object metadata
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

        # select the service
        me.set_service arnum, uid, yes

      # set template
      $.each record.template_metadata, (uid, template) ->
        me.set_template arnum, template

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
     * Set default field values to dependents
    ###
    me = this
    $.each record.field_values, (field_name, values) ->
      me.apply_dependent_value arnum, field_name, values


  apply_dependent_value: (arnum, field_name, values) ->
    ###
     * Set values on field
    ###

    # always handle values as array internally
    if not Array.isArray values
      values = [values]

    me = this
    values_json = JSON.stringify values
    field = $("#" + field_name + "-#{arnum}")
    console.debug "apply_dependent_value: field_name=#{field_name} field_values=#{values_json}"

    # (multi-) reference fields, e.g. CC Contacts of selected Contact
    if @is_reference_field field
      manually_deselected = @deselected_uids[field_name] or []
      # filter out values that were manually deselected
      values = values.filter (value) ->
        return value.uid not in manually_deselected

      # get a list of uids
      uids = values.map (value) ->
        return value.uid

      # update reference field data records
      values.forEach (value) =>
        @set_reference_field_records field, value

      if field.data("multi_valued") is 1
        @set_multi_reference_field field, uids
      else
        uid = if uids.length > 0 then uids[0] else ""
        @set_reference_field field, uid

    # other fields, e.g. default CC Emails of Client
    else
      values.forEach (value, index) ->
        # do not override if the `if_empty` flag is set
        if value.if_empty? and value.if_empty is true
          if field.val()
            return

        # set the value
        if value.value?
          if typeof value.value == "boolean"
            field.prop "checked", value.value
          else
            field.val value.value


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


  is_reference_field: (field) ->
    ###
     * Checks if the given field is a reference field
    ###
    field = $(field)
    if field.hasClass("senaite-uidreference-widget-input")
      return yes
    if field.hasClass("ArchetypesReferenceWidget")
      return yes
    return no


  flush_reference_field: (field) ->
    ###
     * Empty the reference field and restore the search query
    ###
    return unless field.length > 0

    # restore the original search query
    @reset_reference_field_query field
    # set emtpy value
    @set_reference_field field, ""


  reset_reference_field_query: (field) =>
    ###
     * Restores the catalog search query for the given reference field
    ###
    return unless field.length > 0
    this.set_reference_field_query(field, {})


  set_reference_field_query: (field, query) =>
    ###
     * Set the catalog search query for the given reference field
    ###
    return unless field.length > 0
    # set the new query
    search_query = JSON.stringify(query)
    field.attr("data-search_query", search_query)
    console.info("----------> Set search query for field #{field.selector} -> #{search_query}")


  set_reference_field_records: (field, records) =>
    ###
     * Set data-records to display the UID of a reference field
    ###
    records ?= {}
    $field = $(field)

    existing_records = JSON.parse($field.attr("data-records") or '{}')
    new_records = Object.assign(existing_records, records)
    $field.attr("data-records", JSON.stringify(new_records))


  set_reference_field: (field, uid) ->
    ###
     * Set the UID of a reference field
     * NOTE: This method overrides any existing value!
    ###
    return unless field.length > 0

    fieldname = JSON.parse field.data("name")
    console.debug "set_reference_field:: field=#{fieldname} uid=#{uid}"
    textarea = field.find("textarea")
    this.native_set_value(textarea[0], uid)


  set_multi_reference_field: (field, uids, append=true) ->
    ###
     * Set multiple UIDs of a reference field
    ###
    return unless field.length > 0

    uids ?= []
    fieldname = JSON.parse field.data("name")
    console.debug "set_multi_reference_field:: field=#{fieldname} uids=#{uids}"
    textarea = field.find("textarea")

    if not append
      this.native_set_value(textarea[0], uids.join("\n"))
    else
      existing = textarea.val().split("\n")
      uids.forEach (uid) ->
        if uid not in existing
          existing = existing.concat(uid)
      this.native_set_value(textarea[0], existing.join("\n"))


  get_reference_field_value: (field) =>
    ###
     * Return the value of a single/multi reference field
    ###
    $field = $(field)
    if $field.type is "textarea"
      $textarea = $field
    else
      $textarea = $field.find("textarea")
    return $textarea.val()


  set_template: (arnum, template) =>
    ###
     * Apply the template data to all fields of arnum
    ###
    me = this

    # apply template only once
    template_field = $("#Template-#{arnum}")
    template_uid = @get_reference_field_value(template_field)

    if arnum of @applied_templates
      # Allow to remove fields set by the template
      if @applied_templates[arnum] == template_uid
        console.debug "Skipping already applied template"
        return

    # remember the template for this ar
    @applied_templates[arnum] = template_uid

    # set the sample type
    field = $("#SampleType-#{arnum}")
    value = @get_reference_field_value(field)
    if not value
      uid = template.sample_type_uid
      @set_reference_field field, uid

    # set the sample point
    field = $("#SamplePoint-#{arnum}")
    value = @get_reference_field_value(field)
    if not value
      uid = template.sample_point_uid
      @set_reference_field field, uid

    # set the composite checkbox
    field = $("#Composite-#{arnum}")
    field.prop "checked", template.composite

    # set the services
    $.each template.service_uids, (index, uid) ->
      # select the service
      me.set_service arnum, uid, yes

    # set the template field again
    # XXX how to avoid that setting the sample types flushes the template field?
    @set_reference_field template_field, template_uid


  set_service: (arnum, uid, checked) =>
    ###
     * Select the checkbox of a service by UID
    ###
    console.debug "*** set_service::AR=#{arnum} UID=#{uid} checked=#{checked}"
    me = this
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
    # show/hide the service conditions for this analysis
    me.set_service_conditions el
    # trigger event for price recalculation
    $(@).trigger "services:changed"


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
     * Generic event handler for when a reference field value changed
    ###
    me = this
    el = event.currentTarget
    $el = $(el)
    field_name = $el.closest("tr[fieldname]").attr "fieldname"
    arnum = $el.closest("[arnum]").attr "arnum"

    # handle manually selected/deselected UIDs
    value = event.detail.value
    if value
      manually_deselected = @deselected_uids[field_name] or []
      select = if event.type is "select" then yes else no
      if select
        # remove UID from the manually deselected list again
        manually_deselected = manually_deselected.filter (item) -> item isnt value
        console.debug "Reference with UID #{value} was manually selected"
      else
        # remember UID as manually deselected
        manually_deselected = if manually_deselected.indexOf value > -1 then manually_deselected.concat value
        console.debug "Reference with UID #{value} was manually deselected"
      @deselected_uids[field_name] = manually_deselected

    if field_name in ["Template", "Profiles"]
      # These fields have it's own event handler
      return

    console.debug "°°° on_referencefield_value_changed: field_name=#{field_name} arnum=#{arnum} °°°"

    # Flush depending fields
    me.flush_fields_for field_name, arnum

    # trigger custom event <field_name>:after_change
    event_data = { bubbles: true, detail: { value: el.value } }
    after_change = new CustomEvent("#{ field_name }:after_change", event_data)
    el.dispatchEvent(after_change)

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


  on_analysis_template_selected: (event) =>
    ###
     * Eventhandler when an Analysis Template was selected.
    ###
    console.debug "°°° on_analysis_template_selected °°°"
    # trigger form:changed event
    $(this).trigger "form:changed"


  on_analysis_template_removed: (event) =>
    ###
     * Eventhandler when an Analysis Template was removed.
    ###
    console.debug "°°° on_analysis_template_removed °°°"

    el = event.currentTarget
    $el = $(el)
    arnum = $el.closest("[arnum]").attr "arnum"
    @applied_templates[arnum] = null

    # trigger form:changed event
    $(this).trigger "form:changed"


  on_analysis_profile_selected: (event) =>
    ###
     * Eventhandler when an Analysis Profile was selected.
    ###
    console.debug "°°° on_analysis_profile_selected °°°"
    # trigger form:changed event
    $(this).trigger "form:changed"


  # Note: Context of callback bound to this object
  on_analysis_profile_removed: (event) =>
    ###
     * Eventhandler when an Analysis Profile was removed.
    ###
    console.debug "°°° on_analysis_profile_removed °°°"

    me = this
    el = event.currentTarget
    $el = $(el)
    arnum = $el.closest("[arnum]").attr "arnum"

    # The event detail tells us which profile UID has been deselected
    profile_uid = event.detail.value

    record = @records_snapshot[arnum]
    profile_metadata = record.profiles_metadata[profile_uid]
    profile_services = []

    # prepare a list of services used by the profile with the given UID
    $.each record.profile_to_services[profile_uid], (index, uid) ->
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

    # show/hide the service conditions for this analysis
    me.set_service_conditions $el
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

    # reference widget
    if $(td1).find('.ArchetypesReferenceWidget').length > 0
      console.debug "-> Copy reference field"

      el = $(td1).find(".ArchetypesReferenceWidget")
      records = JSON.parse(el.attr("data-records")) or {}
      value = me.get_reference_field_value(el)

      $.each [1..ar_count], (arnum) ->
        # skip the first (source) column
        return unless arnum > 0

        # find the reference widget of the next column
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find(".ArchetypesReferenceWidget")

        # XXX: Needed?
        _field_name = _el.closest("tr[fieldname]").attr "fieldname"
        me.flush_fields_for _field_name, arnum

        # RectJS queryselect widget provides the JSON data of the selected
        # records in the `data-records` attribute.
        # This is needed because otherwise we would only see the raw UID value
        # (or another Ajax call would be needed.)
        me.set_reference_field_records(_el, records)

        # set the textarea (this triggers a select event on the field)
        me.set_reference_field(_el, value)

      # trigger form:changed event
      $(me).trigger "form:changed"
      return

    # Copy <input type="checkbox"> fields
    $td1.find("input[type=checkbox]").each (index, el) ->
      console.debug "-> Copy checkbox field"
      $el = $(el)
      checked = $el.prop "checked"
      is_service = $el.hasClass "analysisservice-cb"
      # iterate over columns, starting from column 2
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type=checkbox]")[index]
        $(_el).prop "checked", checked
        if is_service
          # show/hide the service conditions for this analysis
          uid = $el.closest("[uid]").attr "uid"
          me.set_service_conditions $(_el)
          # copy the conditions for this analysis
          me.copy_service_conditions 0, arnum, uid

      # trigger event for price recalculation
      if is_service
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

    # Copy <input type="number"> fields
    $td1.find("input[type=number]").each (index, el) ->
      console.debug "-> Copy text field"
      $el = $(el)
      value = $el.val()
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type=number]")[index]
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
        me.native_set_value(_el, value)

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

    # Copy <input type="date"> fields
    $td1.find("input[type='date']").each (index, el) ->
      console.debug "-> Copy date field"
      $el = $(el)
      value = $el.val()
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type='date']")[index]
        $(_el).val value

    # Copy <input type="time"> fields
    $td1.find("input[type='time']").each (index, el) ->
      console.debug "-> Copy time field"
      $el = $(el)
      value = $el.val()
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type='time']")[index]
        $(_el).val value

    # Copy <input type="hidden"> fields
    $td1.find("input[type='hidden']").each (index, el) ->
      console.debug "-> Copy hidden field"
      $el = $(el)
      value = $el.val()
      $.each [1..ar_count], (arnum) ->
        # skip the first column
        return unless arnum > 0
        _td = $tr.find("td[arnum=#{arnum}]")
        _el = $(_td).find("input[type='hidden']")[index]
        $(_el).val value

    # trigger form:changed event
    $(me).trigger "form:changed"


  ###*
    * Set input value with native setter to support ReactJS components
  ###
  native_set_value: (input, value) =>
    # https://stackoverflow.com/questions/23892547/what-is-the-best-way-to-trigger-onchange-event-in-react-js
    # TL;DR: React library overrides input value setter

    setter = null
    if input.tagName == "TEXTAREA"
      setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value").set
    else if input.tagName == "SELECT"
      setter = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype, "value").set
    else if input.tagName == "INPUT"
      setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set
    else
      input.value = value

    if setter
      setter.call(input, value)

    event = new Event("input", {bubbles: true})
    input.dispatchEvent(event)


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
      msg = _t("Sorry, an error occured: #{status}")
      window.bika.lims.portalMessage msg
      window.scroll 0, 0


  on_ajax_start: =>
    ###
     * Ajax request started
    ###
    console.debug "°°° on_ajax_start °°°"

    # deactivate the save button
    save_button = $("input[name=save_button]")
    save_button.prop "disabled": yes
    save_button[0].value = _t("Loading ...")

    # deactivate the save and copy button
    save_and_copy_button = $("input[name=save_and_copy_button]")
    save_and_copy_button.prop "disabled": yes


  on_ajax_end: =>
    ###
     * Ajax request finished
    ###
    console.debug "°°° on_ajax_end °°°"

    # reactivate the save button
    save_button = $("input[name=save_button]")
    save_button.prop "disabled": no
    save_button[0].value = _t("Save")

    # reactivate the save and copy button
    save_and_copy_button = $("input[name=save_and_copy_button]")
    save_and_copy_button.prop "disabled": no


  on_cancel: (event, callback) =>
    console.debug "°°° on_cancel °°°"
    event.preventDefault()
    base_url = this.get_base_url()

    @ajax_post_form("cancel").done (data) ->
      if data["redirect_to"]
        window.location.replace data["redirect_to"]
      else
        window.location.replace base_url


  # Note: Context of callback bound to this object
  on_form_submit: (event, callback) =>
    ###
     * Eventhandler for the form submit button.
     * Extracts and submits all form data asynchronous.
    ###
    console.debug "°°° on_form_submit °°°"
    event.preventDefault()
    me = this

    # The clicked submit button is not part of the form data, therefore,
    # we pass the name of the button through a hidden field
    btn = event.currentTarget
    action = "save"
    if btn.name == "save_and_copy_button"
        action = "save_and_copy"
    action_input = document.querySelector("input[name='submit_action']")
    action_input.value = action

    # get the right base url
    base_url = me.get_base_url()

    # the poral url
    portal_url = me.get_portal_url()

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
          msg = _t("Sorry, an error occured 🙈<p class='code'>#{msg}</p>")

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

      else if data['confirmation']
        dialog = me.template_dialog "confirm-template", data.confirmation
        dialog.on "yes", ->
            # Re-submit
            $("input[name=confirmed]").val "1"
            $("input[name=save_button]").trigger "click"

        dialog.on "no", ->
          # Don't submit and redirect user if required
          destination = data.confirmation["destination"]
          if destination
            window.location.replace portal_url + '/' + destination
      else if data['redirect_to']
        window.location.replace data['redirect_to']
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
      add_btn_src = "#{window.portal_url}/senaite_theme/icon/plus"
      add_btn = $("<img class='addbtn' width='16' style='cursor:pointer;' src='#{add_btn_src}' />")

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
    del_btn_src = "#{window.portal_url}/senaite_theme/icon/delete"
    del_btn = $("<img class='delbtn' width='16' style='cursor:pointer;' src='#{del_btn_src}' />")

    # Bind an DELETE event handler
    del_btn.on "click", element, (event) ->
      $(this).parent().remove()

    # Attach the Button into the same div container
    file_field_div.append del_btn

    # Attach the new field to the outer div of the passed file field
    $(element).parent().parent().append file_field_div


  set_service_conditions: (el) =>
    ###
     * Shows or hides the service conditions input elements for the service
     * bound to the checkbox element passed in
    ###

    # Check whether the checkbox is selected or not
    checked = el.prop "checked"

    # Get the uid of the analysis and the column number
    parent = el.closest("td[uid][arnum]")
    uid = parent.attr "uid"
    arnum = parent.attr "arnum"

    # Get the div where service conditions are rendered
    conditions = $("div.service-conditions", parent)
    conditions.empty()

    # If the service is unchecked, remove the conditions form
    if not checked
      conditions.hide()
      return

    # Check if this service requires conditions
    data = conditions.data "data"
    base_info =
      arnum: arnum

    if not data
      @get_service(uid).done (data) ->
        context = $.extend({}, data, base_info)
        if context.conditions and context.conditions.length > 0
          template = @render_template "service-conditions", context
          conditions.append template
          conditions.data "data", context
          conditions.show()
    else
      context = $.extend({}, data, base_info)
      if context.conditions and context.conditions.length > 0
        template = @render_template "service-conditions", context
        conditions.append template
        conditions.show()


  copy_service_conditions: (from, to, uid) =>
    ###
     * Copies the service conditions values from those set for the service with
     * the specified uid and arnum_from column to the same analysis from the
     * arnum_to column
    ###
    console.debug "*** copy_service_conditions::from=#{from} to=#{to} UID=#{uid}"

    me = this

    # Copy the values from all input fields to destination by name
    source = "td[fieldname='Analyses-#{from}'] div[id='#{uid}-conditions'] input[name='ServiceConditions-#{from}.value:records']"
    $(source).each (idx, el) ->
      # Extract the information from the field to look for
      $el = $(el)
      name = $el.attr "name"
      subfield = $el.closest("[data-subfield]").attr "data-subfield"
      console.debug "-> Copy service condition: #{subfield}"

      # Set the value
      dest = $("td[fieldname='Analyses-#{to}'] tr[data-subfield='#{subfield}'] input[name='ServiceConditions-#{to}.value:records']")
      dest.val($el.val())


  init_service_conditions: =>
    ###
     * Updates the visibility of the conditions for the selected services
    ###
    console.debug "init_service_conditions"

    me = this

    # Find out all selected services checkboxes
    services = $("input[type=checkbox].analysisservice-cb:checked")
    $(services).each (idx, el) ->
      $el = $(el)
      me.set_service_conditions $el
