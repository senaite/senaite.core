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


  ####################
  ### AJAX FETCHER ###
  ####################

  ###*
   * Fetch global settings from the setup, e.g. show_prices
   *
  ###
  get_global_settings: =>
    @ajax_post_form("get_global_settings").done (settings) ->
      console.debug "Global Settings:", settings
      # remember the global settings
      @global_settings = settings
      # trigger event for whom it might concern
      $(@).trigger "settings:updated", settings


  ###*
   * Retrieve the flush settings mapping (field name -> list of other fields to flush)
   *
  ###
  get_flush_settings: =>
    @ajax_post_form("get_flush_settings").done (settings) ->
      console.debug "Flush settings:", settings
      @flush_settings = settings
      $(@).trigger "flush_settings:updated", settings


  ###*
   * Fetch the service data from server by UID
   *
  ###
  get_service: (uid) =>
    options =
      data:
        uid: uid
      processData: yes
      contentType: 'application/x-www-form-urlencoded; charset=UTF-8'

    @ajax_post_form("get_service", options).done (data) ->
      console.debug "get_service::data=", data


  ###*
   * Submit all form values to the server to recalculate the records
   *
  ###
  recalculate_records: =>
    @ajax_post_form("recalculate_records").done (records) ->
      console.debug "Recalculate Analyses: Records=", records
      # remember a services snapshot
      @records_snapshot = records
      # trigger event for whom it might concern
      $(@).trigger "data:updated", records


  ###*
   * Submit all form values to the server to recalculate the prices of all columns
   *
  ###
  recalculate_prices: =>
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


  ###*
   * Ajax POST the form data to the given endpoint
   *
   * NOTE: Context of callback is bound to this object
   *
   * @param endpoint {String} Ajax endpoint to call
   * @param options {Object} Additional ajax options
  ###
  ajax_post_form: (endpoint, options={}) =>
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


  ###*
   * Fetch Ajax API resource from the server
   *
   * @param endpoint {String} API endpoint
   * @param options {Object} Fetch options and data payload
   * @returns {Promise}
  ###
  get_json: (endpoint, options) ->
    options ?= {}

    method = options.method or "POST"
    data = JSON.stringify(options.data) or "{}"

    base_url = @get_base_url()
    url = "#{base_url}/ajax_ar_add/#{endpoint}"

    # Always notify Ajax end
    me = this
    $(me).trigger "ajax:start"

    init =
      method: method
      headers:
        "Content-Type": "application/json"
        "X-CSRF-TOKEN": @get_csrf_token()
      body: if method is "POST" then data else null
      credentials: "include"
    console.info "get_json:endpoint=#{endpoint} init=",init
    request = new Request(url, init)
    fetch(request)
    .then (response) ->
      $(me).trigger "ajax:end"
      if not response.ok
        return Promise.reject response
      return response
    .then (response) ->
      return response.json()
    .catch (response) ->
      return response


  ###############
  ### METHODS ###
  ###############

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

    # Date sampled changed
    $("body").on "change", "tr[fieldname=DateSampled] input", @recalculate_records

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


  ###*
   * Init file fields to allow multiple attachments
   *
  ###
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


  ###*
   * Updates the visibility of the conditions for the selected services
   *
  ###
  init_service_conditions: =>
    console.debug "init_service_conditions"

    me = this

    # Find out all selected services checkboxes
    services = $("input[type=checkbox].analysisservice-cb:checked")
    $(services).each (idx, el) ->
      $el = $(el)
      me.set_service_conditions $el


  ###*
   * Debounce a function call
   *
   * See: https://coffeescript-cookbook.github.io/chapters/functions/debounce
   *
   * @param func {Object} Function to debounce
   * @param threshold {Integer} Debounce time in milliseconds
   * @param execAsap {Boolean} True/False to execute the function immediately
  ###
  debounce: (func, threshold, execAsap) =>
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


  ###*
   * Update form according to the server data
   *
   * Records provided from the server (see recalculate_records)
   *
   * @param event {Object} Event object
   * @param records {Object} Updated records
  ###
  update_form: (event, records) =>
    console.debug "*** update_form ***"

    me = this

    # initially hide all service-related icons
    $(".service-lockbtn").hide()

    # hide all holding time related icons and set checks enabled by default
    $(".analysisservice").show()
    $(".service-beyondholdingtime").hide()
    $(".analysisservice-cb").prop "disabled": no

    # set all values for one record (a single column in the AR Add form)
    $.each records, (arnum, record) ->

      # Apply the values generically
      $.each record, (name, metadata) ->
        # Discard those fields that do not contain explicit object metadata
        if !name.endsWith("_metadata")
          return
        $.each metadata, (uid, obj_info) ->
          me.apply_field_value arnum, obj_info

      # set services
      $.each record.service_metadata, (uid, metadata) ->
        # lock icon (to be displayed when the service cannot be deselected)
        lock = $("##{uid}-#{arnum}-lockbtn")
        # service is included in a profile
        if uid of record.service_to_profiles
          # do not display the lock button if beyond holding time
          if uid not in record.beyond_holding_time
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

      # disable (and uncheck) services that are beyond sample holding time
      $.each record.beyond_holding_time, (index, uid) ->
        # display the alert
        beyond_holding_time = $("##{uid}-#{arnum}-beyondholdingtime")
        beyond_holding_time.show()

        # disable the service's checkbox to prevent value submit
        service_cb = $("#cb_#{arnum}_#{uid}")
        service_cb.prop "disabled": yes

        # hide checkbox container
        parent = service_cb.parent "div.analysisservice"
        parent.hide()

  ###*
   * Return the portal url (calculated in code)
   *
   * @returns {String} Portal URL
  ###
  get_portal_url: =>
    ###
     * Return the portal url (calculated in code)
    ###
    url = $("input[name=portal_url]").val()
    return url


  ###*
   * Return the current (relative) base url
   *
   * @returns {String} Base URL for Ajax Request
  ###
  get_base_url: =>
    base_url = window.location.href
    if base_url.search("/portal_factory") >= 0
      return base_url.split("/portal_factory")[0]
    return base_url.split("/ar_add")[0]


  ###*
   * Return the CSRF token
   *
   * NOTE: The fields won't save w/o that token set
   *
   * @returns {String} CSRF token
  ###
  get_csrf_token: ->
    ###
     * Get the plone.protect CSRF token
     * Note: The fields won't save w/o that token set
    ###
    return document.querySelector("#protect-script").dataset.token


  ###*
   * Returns the ReactJS widget controller for the given field
   *
   * @param field {Object} jQuery field
   * @returns {Object} ReactJS widget controller
  ###
  get_widget_controller: (field) ->
    id = $(field).prop("id")
    ns = window?.senaite?.core?.widgets or {}
    return ns[id]


  ###*
   * Checks if a given field is a reference field
   *
   * TODO: This check is very naive.
   *       Maybe we can do this better with the widget controller!
   *
   * @param field {Object} jQuery field
   * @returns {Boolean} True if the field is a reference field
  ###
  is_reference_field: (field) ->
    field = $(field)
    if field.hasClass("senaite-uidreference-widget-input")
      return yes
    if field.hasClass("ArchetypesReferenceWidget")
      return yes
    return no


  ###*
   * Checks if the given value is an Array
   *
   * @param thing {Object} value to check
   * @returns {Boolean} True if the value is an Array
  ###
  is_array: (value) ->
    return Array.isArray(value)


  ###*
   * Checks if the given value is a plain Object
   *
   * @param thing {Object} value to check
   * @returns {Boolean} True if the value is a plain Object, i.e. `{}`
  ###
  is_object: (value) ->
    return Object.prototype.toString.call(value) is "[object Object]"


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


  ###*
   * Apply the field value to set dependent fields and set dependent filter queries
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param record {Object} The data record object containing the value and metadata
  ###
  apply_field_value: (arnum, record) ->
    # Set default values to dependents
    @apply_dependent_values arnum, record
    # Apply search filters to other fields
    @apply_dependent_filter_queries arnum, record


  ###*
   * Apply dependent field values
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param record {Object} The data record object containing the value and metadata
  ###
  apply_dependent_values: (arnum, record) ->
    me = this
    $.each record.field_values, (field_name, values) ->
      me.apply_dependent_value arnum, field_name, values


  ###*
   * Apply the actual value on the dependent field
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param field_name {String} Name of the dependent field, e.g. 'CCContact'
   * @param values {Object, Array} The value to be set
  ###
  apply_dependent_value: (arnum, field_name, values) ->
    # always handle values as array internally
    if not @is_array(values)
      values = [values]

    # avoid flushing the field with empty values
    return unless values.length > 0

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

      # update reference field values
      @set_reference_field field, uids

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


  ###*
   * Apply filter queries of dependent reference fields to restrict the allowed searches
   *
   * NOTE: This method is chained to set dependent filter queries sequentially,
   *       because a new Ajax request is done for each field to check if the
   *       current value is allowed or must be flushed.
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param record {Object} The data record object containing the filter_queries
  ###
  apply_dependent_filter_queries: (arnum, record) ->
    me = this
    chain = Promise.resolve()
    $.each record.filter_queries, (field_name, query) ->
      field = $("#" + field_name + "-#{arnum}")
      chain = chain.then () ->
        me.set_reference_field_query field, query


  ###*
   * Set a custom filter query of a reference field
   *
   * This method also checks if the current value is allowed by the new search query.
   *
   * @param field {Object} jQuery field
   * @param query {Object} The catalog query to apply to the base query
  ###
  set_reference_field_query: (field, query) =>
    controller = @get_widget_controller(field)
    # No controller found, return immediately
    # -> happens when the field is hidden or absent
    return unless controller

    # set the new query
    controller.set_search_query(query)
    console.debug("Set custom search query for field #{field.selector}: #{JSON.stringify(query)}")

    # check if the target field needs to be flushed
    target_field_name = field.closest("tr[fieldname]").attr "fieldname"
    target_field_label = field.closest("tr[fieldlabel]").attr "fieldlabel"
    target_value = controller.get_values()
    target_base_query = controller.get_query()
    target_query = Object.assign({}, target_base_query, query)
    target_catalog = controller.get_catalog()

    # no flushing required if the field is already empty
    if target_value.length == 0
      return

    me = this
    data =
      query: target_query
      uids: target_value
      catalog: target_catalog
      label: target_field_label
      name: target_field_name

    # Ask the server if the value is allowed by the new query
    @get_json("is_reference_value_allowed", {data: data}).then (response) ->
      if not response.allowed
        console.info("Reference value #{target_value} of field #{target_field_name} " +
                     "is *not* allowed by the new query ", target_query)
        me.flush_reference_field field
        message = response.message
        if message
          site.add_notification(message.title, message.text)


  ###*
   * Reset the custom filter query of a reference field
   *
   * @param field {Object} jQuery field
  ###
  reset_reference_field_query: (field) =>
    this.set_reference_field_query(field, {})


  ###*
   * Get the current value of the reference field
   *
   * NOTE: This method returns the values for backwards compatibility as if they
   *       were read from the textfield (lines of UIDs)
   *       This will be removed when all methods rely on `controller.get_values()`
   *
   * @param field {Object} jQuery field
   * @returns {String} UIDs joined with \n
  ###
  get_reference_field_value: (field) =>
    controller = @get_widget_controller(field)
    # No controller found, return immediately
    # -> happens when the field is hidden or absent
    return unless controller

    values = controller.get_values()
    # BBB: provide the values in the same way as the textarea
    return values.join("\n")


  ###*
   * Set UID(s) of a single/multi reference field
   *
   * NOTE: This method overrides the value of single reference fields or
   *       removes/adds the omitted/added values from multi-reference fields
   *
   * @param field {Object} jQuery field
   * @param values {String,Array} UID(s) to set. A falsy value flushes the field.
  ###
  set_reference_field: (field, values) ->
    if not @is_array(values)
      values = [values]

    # filter out invalid UIDs
    # NOTE: UIDs have always a length of 32
    values = values.filter((item) -> item and item.length == 32)

    controller = @get_widget_controller(field)
    # No controller found, return immediately
    # -> happens when the field is hidden or absent
    return unless controller

    fieldname = controller.get_name()
    console.debug "set_reference_field:: field=#{fieldname} values=#{values}"
    controller.set_values(values)


  ###*
   * Flush reference fields that are statically provided in the flush_settings
   *
   * NOTE: Since https://github.com/senaite/senaite.core/pull/2564 this makes
   *       only sense for non-reference fields, e.g. `EnvironmentalConditions`
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param field_name {String} The name of the field where dependent fields need to be flushed
  ###
  flush_fields_for: (arnum, field_name) ->
    me = this
    field_ids = @flush_settings[field_name]
    $.each @flush_settings[field_name], (index, id) ->
      console.debug "flushing: id=#{id}"
      field = $("##{id}-#{arnum}")
      me.flush_reference_field field


  ###*
   * Empty the reference field and restore the search query
   *
   * @param field {Object} jQuery field
  ###
  flush_reference_field: (field) ->
    # set emtpy value
    @set_reference_field field, null
    # restore the original search query
    @reset_reference_field_query field


  ###*
   * Set data-records to display the UID of a reference field
   *
   * NOTE: This method if for performance reasons only.
   *       It avoids an additional lookup of the reference widget to fetch the
   *       required data to render the display template for the actual UID.
   *
   * @param field {Object} jQuery field
   * @param records {Object} Records to set
  ###
  set_reference_field_records: (field, records) =>
    return unless records and @is_object(records)

    controller = @get_widget_controller(field)
    # No controller found, return immediately
    # -> happens when the field is hidden or absent
    return unless controller

    existing_records = controller.get_data_records()
    new_records = Object.assign(existing_records, records)
    controller.set_data_records(new_records)


  ###*
   * Return the record metadata from the `records_snapshot` for the given field
   *
   * NOTE: The `records_snapshot` get updated each time `recalculate_records`
   *       is called. It is provided by the server and contains information
   *       about dependencies, dependent fields/queries etc.
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param records {Object} Records to set
  ###
  get_metadata_for: (arnum, field_name) =>
    record = @records_snapshot[arnum] or {}
    metadata_key = "#{field_name}_metadata".toLowerCase()
    return record[metadata_key] or {}


  ###*
   * Apply the template values to the sample in the specified column
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param template {Object} Template record
  ###
  set_template: (arnum, template) =>
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


  ###*
   * Select service checkbox by UID
   *
   * @param arnum {String} Sample column number, e.g. '0' for a field of the first column
   * @param uid {String} UID of the service to select
   * @param checked {Boolean} True/False to toggle select/delselect
  ###
  set_service: (arnum, uid, checked) =>
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


  ###*
   * Show/hide  service conditions input elements for the service
   *
   * @param el {Object} jQuery service checkbox
  ###
  set_service_conditions: (el) =>
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


  ###*
   * Copies the service conditions values from those set for the service with
   * the specified uid and arnum_from column to the same analysis from the
   * arnum_to column
  ###
  copy_service_conditions: (from, to, uid) =>
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


  ###*
   * Hide all open service info boxes
   *
  ###
  hide_all_service_info: =>
    info = $("div.service-info")
    info.hide()


  ###*
   * Checks if the point of capture is visible
   *
   * @param poc {String} Point of Capture, i.e. 'lab' or 'field'
  ###
  is_poc_expanded: (poc) ->
    el = $("tr.service-listing-header[poc=#{poc}]")
    return el.hasClass "visible"


  ###*
   * Toggle all categories within a point of capture (lab/service)
   *
   * @param poc {String} Point of Capture, i.e. 'lab' or 'field'
   * @param toggle {Boolean} True/False to show/hide categories
  ###
  toggle_poc_categories: (poc, toggle) ->
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


  ###*
   * Render a confirmation dialog popup
   *
   * [1] http://handlebarsjs.com/
   * [2] https://jqueryui.com/dialog/
   *
   * @param template_id {String} ID of the Handlebars template
   * @param context {Object} Data to fill into the template
   * @param buttons {Object} Buttons to render
  ###
  template_dialog: (template_id, context, buttons) =>
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


  ###*
   * Render template with Handlebars
   *
   * @returns {String} Rendered content
  ###
  render_template: (template_id, context) =>
    # get the template by ID
    source = $("##{template_id}").html()
    return unless source
    # Compile the handlebars template
    template = Handlebars.compile(source)
    # Render the template with the given context
    content = template(context)
    return content


  ######################
  ### EVENT HANDLERS ###
  ######################

  ###*
   * Generic event handler for when a reference field value changed
   *
   * @param event {Object} The event object
  ###
  on_referencefield_value_changed: (event) =>
    me = this
    el = event.currentTarget
    $el = $(el)
    field_name = $el.closest("tr[fieldname]").attr "fieldname"
    arnum = $el.closest("[arnum]").attr "arnum"
    value = event.detail.value
    selected = if event.type is "select" then yes else no
    deselected = not selected
    manually_deselected = @deselected_uids[field_name] or []
    record = @records_snapshot[arnum] or {}
    metadata = @get_metadata_for(arnum, field_name)

    # reset all dependent filter queries
    if deselected and metadata
      # get the applied filter queries of the current UID
      filter_queries = metadata[value]?.filter_queries or []
      $.each filter_queries, (target_field_name, target_field_query) ->
        target_field = $("##{target_field_name}-#{arnum}")
        me.reset_reference_field_query target_field

    # handle manually selected/deselected UIDs
    if value
      if selected
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
    me.flush_fields_for arnum, field_name

    # trigger custom event <field_name>:after_change
    event_data = { bubbles: true, detail: { value: el.value } }
    after_change = new CustomEvent("#{ field_name }:after_change", event_data)
    el.dispatchEvent(after_change)

    # trigger form:changed event
    $(me).trigger "form:changed"


  ###*
   * Event handler when the user clicked on the info icon of a service.
   *
   * @param event {Object} The event object
  ###
  on_analysis_details_click: (event) =>
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


  ###*
   * Event handler when an Analysis Profile was removed.
   *
   * @param event {Object} The event object
  ###
  on_analysis_lock_button_click: (event) =>
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


  ###*
   * Event handler when an Analysis Template was selected.
   *
   * @param event {Object} The event object
  ###
  on_analysis_template_selected: (event) =>
    console.debug "°°° on_analysis_template_selected °°°"
    # trigger form:changed event
    $(this).trigger "form:changed"


  ###*
   * Eventhandler when an Analysis Template was removed.
   *
   * @param event {Object} The event object
  ###
  on_analysis_template_removed: (event) =>
    console.debug "°°° on_analysis_template_removed °°°"

    el = event.currentTarget
    $el = $(el)
    arnum = $el.closest("[arnum]").attr "arnum"
    @applied_templates[arnum] = null

    # trigger form:changed event
    $(this).trigger "form:changed"


  ###*
   * Event handler when an Analysis Profile was selected.
   *
   * @param event {Object} The event object
  ###
  on_analysis_profile_selected: (event) =>
    console.debug "°°° on_analysis_profile_selected °°°"
    # trigger form:changed event
    $(this).trigger "form:changed"


  ###*
   * Event handler when an Analysis Profile was removed.
   *
   * @param event {Object} The event object
  ###
  on_analysis_profile_removed: (event) =>
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


  ###*
   * Event handler for Analysis Service Checkboxes.
   *
   * @param event {Object} The event object
  ###
  on_analysis_checkbox_click: (event) =>
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


  ###*
   * Event handler for analysis service category header rows.
   *
   * Toggles the visibility of all categories within this poc.
   *
   * @param event {Object} The event object
  ###
  on_service_listing_header_click: (event) =>
    $el = $(event.currentTarget)
    poc = $el.data("poc")
    visible = $el.hasClass("visible")
    toggle = not visible
    @toggle_poc_categories poc, toggle


  ###*
   * Event handler for analysis service category rows.
   *
   * Toggles the visibility of all services within this category.
   * NOTE: Selected services always stay visible.
   *
   * @param event {Object} The event object
  ###
  on_service_category_click: (event) =>
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


  ###*
   * Event handler for the field copy button per row.
   *
   * Copies the value of the first field in this row to the remaining.
   *
   * XXX: Refactor this method, it is way too long
   *
   * @param event {Object} The event object
  ###
  on_copy_button_click: (event) =>
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
        me.flush_fields_for arnum, _field_name

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
   * Event handler when Ajax request started
   *
   * @param event {Object} The event object
  ###
  on_ajax_start: =>
    console.debug "°°° on_ajax_start °°°"

    # deactivate the save button
    save_button = $("input[name=save_button]")
    save_button.prop "disabled": yes
    save_button[0].value = _t("Loading ...")

    # deactivate the save and copy button
    save_and_copy_button = $("input[name=save_and_copy_button]")
    save_and_copy_button.prop "disabled": yes


  ###*
   * Event handler when Ajax request finished
   *
   * @param event {Object} The event object
  ###
  on_ajax_end: =>
    console.debug "°°° on_ajax_end °°°"

    # reactivate the save button
    save_button = $("input[name=save_button]")
    save_button.prop "disabled": no
    save_button[0].value = _t("Save")

    # reactivate the save and copy button
    save_and_copy_button = $("input[name=save_and_copy_button]")
    save_and_copy_button.prop "disabled": no


  ###*
   * Event handler when Ajax when cancel button was clicked
   *
   * @param event {Object} The event object
   * @param callback {Function}
  ###
  on_cancel: (event, callback) =>
    console.debug "°°° on_cancel °°°"
    event.preventDefault()
    base_url = this.get_base_url()

    @ajax_post_form("cancel").done (data) ->
      if data["redirect_to"]
        window.location.replace data["redirect_to"]
      else
        window.location.replace base_url


  ###*
   * Event handler for the form submit button.
   *
   * Extracts all form data and submits them asynchronously
   *
   * @param event {Object} The event object
  ###
  on_form_submit: (event, callback) =>
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


  ###*
   * Event handler when the file add button was clicked
   *
   * @param event {Object} The event object
   * @param element {Object} jQuery file field
  ###
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
