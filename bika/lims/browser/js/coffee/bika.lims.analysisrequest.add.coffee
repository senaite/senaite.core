### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.analysisrequest.add.coffee
###


class window.AnalysisRequestAdd

  load: =>
    console.debug "AnalysisRequestAdd::load"

    # load translations
    jarn.i18n.loadCatalog 'bika'
    @_ = window.jarn.i18n.MessageFactory('bika')

    # disable browser autocomplete
    $('input[type=text]').prop 'autocomplete', 'off'

    # storage for global Bika settings
    @global_settings = {}

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

    # recalculate records on load (needed for AR copies)
    @recalculate_records()


  ### METHODS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
    ###
    console.debug "AnalysisRequestAdd::bind_eventhandler"
    # Categories header clicked
    $(".service-listing-header").on "click", @on_service_listing_header_click
    # Category toggle button clicked
    $("tr.category").on "click", @on_service_category_click
    # Save button clicked
    $("[name='save_button']").on "click", @on_form_submit
    # AdHoc Checkbox clicked
    $("tr[fieldname=AdHoc] input[type='checkbox']").on "click", @recalculate_records
    # Composite Checkbox clicked
    $("tr[fieldname=Composite] input[type='checkbox']").on "click", @recalculate_records
    # InvoiceExclude Checkbox clicked
    $("tr[fieldname=InvoiceExclude] input[type='checkbox']").on "click", @recalculate_records
    # Analysis Checkbox clicked
    $("tr[fieldname=Analyses] input[type='checkbox']").on "click", @on_analysis_checkbox_click
    # Client changed
    $("tr[fieldname=Client] input[type='text']").on "selected change", @on_client_changed
    # Contact changed
    $("tr[fieldname=Contact] input[type='text']").on "selected change", @on_contact_changed
    # ReportDryMatter Checkbox clicked
    $("tr[fieldname=ReportDryMatter] input[type='checkbox']").on "click", @on_reportdrymatter_click
    # Analysis Specification changed
    $("input.min").on "change", @on_analysis_specification_changed
    $("input.max").on "change", @on_analysis_specification_changed
    $("input.err").on "change", @on_analysis_specification_changed
    # Analysis lock button clicked
    $(".service-lockbtn").on "click", @on_analysis_lock_button_click
    # Analysis info button clicked
    $(".service-infobtn").on "click", @on_analysis_details_click
    # Sample changed
    $("tr[fieldname=Sample] input[type='text']").on "selected change", @on_sample_changed
    # SampleType changed
    $("tr[fieldname=SampleType] input[type='text']").on "selected change", @on_sampletype_changed
    # Specification changed
    $("tr[fieldname=Specification] input[type='text']").on "selected change", @on_specification_changed
    # Analysis Template changed
    $("tr[fieldname=Template] input[type='text']").on "selected change", @on_analysis_template_changed
    # Analysis Profile selected
    $("tr[fieldname=Profiles] input[type='text']").on "selected", @on_analysis_profile_selected
    # Analysis Profile deselected
    $("tr[fieldname=Profiles] img.deletebtn").live "click", @on_analysis_profile_removed
    # Copy button clicked
    $("img.copybutton").on "click", @on_copy_button_click

    ### internal events ###

    # handle value changes in the form
    $(this).on "form:changed", @recalculate_records
    # update form from records
    $(this).on "data:updated", @update_form
    # recalculate prices after data changed
    $(this).on "data:updated", @recalculate_prices
    # hide open service info after data changed
    $(this).on "data:updated", @hide_all_service_info
    # handle Ajax events
    $(this).on "ajax:start", @on_ajax_start
    $(this).on "ajax:end", @on_ajax_end


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

      # set client
      $.each record.client_metadata, (uid, client) ->
        me.set_client arnum, client

      # set contact
      $.each record.contact_metadata, (uid, contact) ->
        me.set_contact arnum, contact

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
        # service is part of the drymatter service
        if uid of record.service_to_dms
          lock.show()

        # select the service
        me.set_service arnum, uid, yes

      # set template
      $.each record.template_metadata, (uid, template) ->
        me.set_template arnum, template

      # set specification
      $.each record.specification_metadata, (uid, spec) ->
        $.each spec.specifications, (uid, service_spec) ->
          me.set_service_spec arnum, uid, service_spec

      # set sample
      $.each record.sample_metadata, (uid, sample) ->
        me.set_sample arnum, sample

      # set sampletype
      $.each record.sampletype_metadata, (uid, sampletype) ->
        me.set_sampletype arnum, sampletype

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


  flush_reference_field: (field) ->
    ###
     * Empty the reference field
    ###

    catalog_name = field.attr "catalog_name"
    return unless catalog_name

    # flush values
    field.val("")
    $("input[type=hidden]", field.parent()).val("")
    $(".multiValued-listing", field.parent()).empty()


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


  set_client: (arnum, client) =>
    ###
     * Filter Contacts
     * Filter CCContacts
     * Filter InvoiceContacts
     * Filter SamplePoints
     * Filter ARTemplates
     * Filter Specification
     * Filter SamplingRound
    ###

    # filter Contacts
    field = $("#Contact-#{arnum}")
    query = client.filter_queries.contact
    @set_reference_field_query field, query

    # filter CCContacts
    field = $("#CCContact-#{arnum}")
    query = client.filter_queries.cc_contact
    @set_reference_field_query field, query

    # filter InvoiceContact
    # XXX Where is this field?
    field = $("#InvoiceContact-#{arnum}")
    query = client.filter_queries.invoice_contact
    @set_reference_field_query field, query

    # filter Sample Points
    field = $("#SamplePoint-#{arnum}")
    query = client.filter_queries.samplepoint
    @set_reference_field_query field, query

    # filter AR Templates
    field = $("#Template-#{arnum}")
    query = client.filter_queries.artemplates
    @set_reference_field_query field, query

    # filter Analysis Profiles
    field = $("#Profiles-#{arnum}")
    query = client.filter_queries.analysisprofiles
    @set_reference_field_query field, query

    # filter Analysis Specs
    field = $("#Specification-#{arnum}")
    query = client.filter_queries.analysisspecs
    @set_reference_field_query field, query

    # filter Samplinground
    field = $("#SamplingRound-#{arnum}")
    query = client.filter_queries.samplinground
    @set_reference_field_query field, query

    # filter Sample
    field = $("#Sample-#{arnum}")
    query = client.filter_queries.sample
    @set_reference_field_query field, query


  set_contact: (arnum, contact) =>
    ###
     * Set CC Contacts
    ###
    me = this

    field = $("#CCContact-#{arnum}")

    $.each contact.cccontacts, (uid, cccontact) ->
      fullname = cccontact.fullname
      me.set_reference_field field, uid, fullname


  set_sample: (arnum, sample) =>
    ###
     * Apply the sample data to all fields of arnum
    ###

    # set the sampling date
    field = $("#SamplingDate-#{arnum}")
    value = sample.sampling_date
    field.val value

    # set the date sampeld
    field = $("#DateSampled-#{arnum}")
    value = sample.date_sampled
    field.val value

    # set the sample type (required)
    field = $("#SampleType-#{arnum}")
    uid = sample.sample_type_uid
    title = sample.sample_type_title
    @set_reference_field field, uid, title

    # set environmental conditions
    field = $("#EnvironmentalConditions-#{arnum}")
    value = sample.environmental_conditions
    field.val value

    # set client sample ID
    field = $("#ClientSampleID-#{arnum}")
    value = sample.client_sample_id
    field.val value

    # set client reference
    field = $("#ClientReference-#{arnum}")
    value = sample.client_reference
    field.val value

    # set adhoc
    field = $("#AdHoc-#{arnum}")
    field.prop "checked", sample.adhoc

    # set composite
    field = $("#Composite-#{arnum}")
    field.prop "checked", sample.composite

    # set the sample condition
    field = $("#SampleCondition-#{arnum}")
    uid = sample.sample_condition_uid
    title = sample.sample_condition_title
    @set_reference_field field, uid, title

    # set the sample point
    field = $("#SamplePoint-#{arnum}")
    uid = sample.sample_point_uid
    title = sample.sample_point_title
    @set_reference_field field, uid, title

    # set the storage location
    field = $("#StorageLocation-#{arnum}")
    uid = sample.storage_location_uid
    title = sample.storage_location_title
    @set_reference_field field, uid, title

    # set the default container type
    field = $("#DefaultContainerType-#{arnum}")
    uid = sample.container_type_uid
    title = sample.container_type_title
    @set_reference_field field, uid, title


  set_sampletype: (arnum, sampletype) =>
    ###
     * Recalculate partitions
     * Filter Sample Points
    ###

    # restrict the sample points
    field = $("#SamplePoint-#{arnum}")
    query = sampletype.filter_queries.samplepoint
    @set_reference_field_query field, query

    # set the default container
    field = $("#DefaultContainerType-#{arnum}")
    # apply default container if the field is empty
    if not field.val()
      uid = sampletype.container_type_uid
      title = sampletype.container_type_title
      @flush_reference_field field
      @set_reference_field field, uid, title

    # restrict the specifications
    field = $("#Specification-#{arnum}")
    query = sampletype.filter_queries.specification
    @set_reference_field_query field, query


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
    uid = template.sample_type_uid
    title = template.sample_type_title
    @flush_reference_field field
    @set_reference_field field, uid, title

    # set the sample point
    field = $("#SamplePoint-#{arnum}")
    uid = template.sample_point_uid
    title = template.sample_point_title
    @flush_reference_field field
    @set_reference_field field, uid, title

    # set the analysis profile
    field = $("#Profiles-#{arnum}")
    uid = template.analysis_profile_uid
    title = template.analysis_profile_title
    @flush_reference_field field
    @set_reference_field field, uid, title

    # set the remarks
    field = $("#Remarks-#{arnum}")
    field.text template.remarks

    # set the composite checkbox
    field = $("#Composite-#{arnum}")
    field.prop "checked", template.composite

    # set the drymatter checkbox
    field = $("#ReportDryMatter-#{arnum}")
    field.prop "checked", template.report_dry_matter

    # set the services
    $.each template.service_uids, (index, uid) ->
      # select the service
      me.set_service arnum, uid, yes

    # PARTITIONS
    me = this
    part_selectors = $(".part-select-#{arnum}")

    $.each part_selectors, (index, part_selector) ->
      # the selection widget of a service
      $el = $(part_selector)

      # make the selector visible
      $el.parent().show()

      # flush existing options (usually part-1)
      $el.empty()

      # service uid
      uid = $el.attr "uid"

      # lookup which part is selected for this service
      selected_part = "part-1"
      if uid of template.analyses_partitions
        selected_part = template.analyses_partitions[uid]

      # prepare the context for the template
      partitions = []
      $.each template.partitions, (index, part) ->
        part_id = part.part_id
        partitions.push
          part_id: part_id
          selected: part_id == selected_part
      context =
        partitions: partitions

      parts = me.render_template "part-select-template", context
      $el.append(parts)


  set_service: (arnum, uid, checked) =>
    ###
     * Select the checkbox of a service by UID
    ###
    console.debug "*** set_service::AR=#{arnum} UID=#{uid} checked=#{checked}"
    # get the service checkbox element
    el = $("td[fieldname='Analyses-#{arnum}'] #cb_#{uid}")
    # select the checkbox
    el.prop "checked", checked
    # get the point of capture of this element
    poc = el.closest("tr[poc]").attr "poc"
    # make the element visible if the categories are visible
    if @is_poc_expanded poc
      el.closest("tr").addClass "visible"


  set_service_spec: (arnum, uid, spec) =>
    ###
     * Set the specification of the service
    ###
    console.debug "*** set_service_spec::AR=#{arnum} UID=#{uid} spec=", spec

    # get the service specifications
    el = $("div##{uid}-#{arnum}-specifications")

    min = $(".min", el)
    max = $(".max", el)
    err = $(".err", el)

    min.val spec.min
    max.val spec.max
    err.val spec.error


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

  on_client_changed: (event) =>
    ###
     * Eventhandler when the client changed (happens on Batches)
    ###

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $el.attr "uid"
    arnum = $el.closest("[arnum]").attr "arnum"

    console.debug "°°° on_client_changed: arnum=#{arnum} °°°"

    # Flush client depending fields
    field_ids = [
      "Contact"
      "CCContact"
      "InvoiceContact"
      "SamplePoint"
      "Template"
      "Profiles"
      "Specification"
    ]
    $.each field_ids, (index, id) ->
      field = me.get_field_by_id id, arnum
      me.flush_reference_field field

    # trigger form:changed event
    $(me).trigger "form:changed"


  on_contact_changed: (event) =>
    ###
     * Eventhandler when the contact changed
    ###

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $el.attr "uid"
    arnum = $el.closest("[arnum]").attr "arnum"

    console.debug "°°° on_contact_changed: arnum=#{arnum} °°°"

    # Flush client depending fields
    field_ids = [
      "CCContact"
    ]
    $.each field_ids, (index, id) ->
      field = me.get_field_by_id id, arnum
      me.flush_reference_field field

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
      drymatter: []

    # get the current snapshot record for this column
    record = @records_snapshot[arnum]

    # inject drymatter info
    if uid of record.service_to_dms
      dms = record.service_to_dms[uid]
      $.each dms, (index, uid) ->
        extra["drymatter"].push record.dms_metadata[uid]

    # inject profile info
    if uid of record.service_to_profiles
      profiles = record.service_to_profiles[uid]
      $.each profiles, (index, uid) ->
        extra["profiles"].push record.profile_metadata[uid]

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
    context["drymatter"] = []

    # collect profiles
    if uid of record.service_to_profiles
      profile_uid = record.service_to_profiles[uid]
      context["profiles"].push record.profile_metadata[profile_uid]

    # collect templates
    if uid of record.service_to_templates
      template_uid = record.service_to_templates[uid]
      context["templates"].push record.template_metadata[template_uid]

    # collect drymatter
    if uid of record.service_to_dms
      dms_uid = record.service_to_dms[uid]
      context["drymatter"].push record.dms_metadata[dms_uid]

    buttons =
      OK: ->
        $(@).dialog "close"

    dialog = @template_dialog "service-dependant-template", context, buttons


  on_sample_changed: (event) =>
    ###
     * Eventhandler when the Sample was changed.
    ###

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $(el).attr "uid"
    val = $el.val()
    arnum = $el.closest("[arnum]").attr "arnum"
    has_sample_selected = $el.val()
    console.debug "°°° on_sample_change::UID=#{uid} Sample=#{val}°°°"

    # deselect the sample if the field is empty
    if not has_sample_selected
      # XXX manually flush UID field
      $("input[type=hidden]", $el.parent()).val("")

    # trigger form:changed event
    $(me).trigger "form:changed"


  on_sampletype_changed: (event) =>
    ###
     * Eventhandler when the SampleType was changed.
     * Fires form:changed event
    ###

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $(el).attr "uid"
    val = $el.val()
    arnum = $el.closest("[arnum]").attr "arnum"
    has_sampletype_selected = $el.val()
    console.debug "°°° on_sampletype_change::UID=#{uid} SampleType=#{val}°°°"

    # deselect the sampletype if the field is empty
    if not has_sampletype_selected
      # XXX manually flush UID field
      $("input[type=hidden]", $el.parent()).val("")

    # Flush sampletype depending fields
    field_ids = [
      "SamplePoint"
      "Specification"
    ]
    $.each field_ids, (index, id) ->
      field = me.get_field_by_id id, arnum
      me.flush_reference_field field

    # trigger form:changed event
    $(me).trigger "form:changed"


  on_specification_changed: (event) =>
    ###
     * Eventhandler when the Specification was changed.
    ###

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $(el).attr "uid"
    val = $el.val()
    arnum = $el.closest("[arnum]").attr "arnum"
    has_specification_selected = $el.val()
    console.debug "°°° on_specification_change::UID=#{uid} Specification=#{val}°°°"

    # deselect the specification if the field is empty
    if not has_specification_selected
      # XXX manually flush UID field
      $("input[type=hidden]", $el.parent()).val("")

    # trigger form:changed event
    $(me).trigger "form:changed"


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

      if template_services
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
    profile_metadata = record.profile_metadata[uid]
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


  on_reportdrymatter_click: (event) =>
    ###
     * Eventhandler for ReportDryMatter Checkbox.
    ###

    me = this
    el = event.currentTarget
    checked = el.checked
    $el = $(el)
    arnum = $el.closest("[arnum]").attr "arnum"

    console.debug "°°° on_reportdrymatter_click:: checked=#{checked}°°°"

    # drymatter service deselected -> ask the user to deselect the services as well
    if not checked
      record = @records_snapshot[arnum]

      dms_metadata = {}
      dms_services = []

      # prepare a list of services used by the drymatter service
      $.each record.dms_to_services, (dms_uid, service_uids) ->
        dms_metadata = record.dms_metadata[dms_uid]
        $.each service_uids, (index, service_uid) ->
          dms_services.push record.service_metadata[service_uid]

      context = {}
      context["drymatter"] = dms_metadata
      context["services"] = dms_services

      me = this
      dialog = @template_dialog "drymatter-remove-template", context
      dialog.on "yes", ->
        # deselect the services
        $.each dms_services, (index, service) ->
          me.set_service arnum, service.uid, no
        # trigger form:changed event
        $(me).trigger "form:changed"
      dialog.on "no", ->
        # trigger form:changed event
        $(me).trigger "form:changed"

    # trigger form:changed event
    $(me).trigger "form:changed"


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

    # Update Options
    $.extend(ajax_options, options)

    ### Execute the request ###

    # Notify Ajax start
    me = this
    $(me).trigger "ajax:start"
    $.ajax(ajax_options).always (data) ->
      # Always notify Ajax end
      $(me).trigger "ajax:end"


  on_ajax_start: =>
    ###
     * Ajax request started
    ###
    console.debug "°°° on_ajax_start °°°"

    # deactivate the button
    button = $("input[name=save_button]")
    button.prop "disabled": yes


  on_ajax_end: =>
    ###
     * Ajax request finished
    ###
    console.debug "°°° on_ajax_end °°°"

    # reactivate the button
    button = $("input[name=save_button]")
    button.prop "disabled": no


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
