### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c bika.lims.sample.add.coffee
###


class window.SampleAdd

  load: =>
    console.debug "SampleAdd::load"

    # load translations
    jarn.i18n.loadCatalog 'bika'
    @_ = window.jarn.i18n.MessageFactory('bika')

    # disable browser autocomplete
    $('input[type=text]').prop 'autocomplete', 'off'

    # storage for global Bika settings
    @global_settings = {}

    # services data snapshot from recalculate_records
    # returns a mapping of samplenum -> services data
    @records_snapshot = {}

    # Remove the '.blurrable' class to avoid inline field validation
    $(".blurrable").removeClass("blurrable")

    # bind the event handler to the elements
    @bind_eventhandler()

    # N.B.: Sample Add form handles File fields like this:
    # - File fields can carry more than one field (see init_file_fields)
    # - All uploaded files are extracted and added as attachments to the new
    # created Sample
    # - The file field itself (Plone) will stay empty therefore
    @init_file_fields()

    # get the global settings on load
    @get_global_settings()

    # recalculate records on load (needed for Sample copies)
    @recalculate_records()


  ### METHODS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
    ###
    console.debug "SampleAdd::bind_eventhandler"
    # Save button clicked
    $("[name='save_button']").on "click", @on_form_submit
    # Client changed
    $("tr[fieldname=Client] input[type='text']").on "selected change", @on_client_changed
    # SampleType changed
    $("tr[fieldname=SampleType] input[type='text']").on "selected change", @on_sampletype_changed
    # Copy button clicked
    $("img.copybutton").on "click", @on_copy_button_click

    ### internal events ###
    # handle value changes in the form
    $(this).on "form:changed", @recalculate_records
    # update form from records
    $(this).on "data:updated", @update_form
    # handle Ajax events
    $(this).on "ajax:start", @on_ajax_start
    $(this).on "ajax:end", @on_ajax_end


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
      console.debug "Recalculate Sample: Records=", records
      # remember a services snapshot
      @records_snapshot = records
      # trigger event for whom it might concern
      $(@).trigger "data:updated", records

  update_form: (event, records) =>
    ###
     * Update form according to the server data
    ###
    console.debug "*** update_form ***"

    me = this

    # set all values for one record (a single column in the Sample Add form)
    $.each records, (samplenum, record) ->

      # set client
      $.each record.client_metadata, (uid, client) ->
        me.set_client samplenum, client

      # set sampletype
      $.each record.sampletype_metadata, (uid, sampletype) ->
        me.set_sampletype samplenum, sampletype


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
    return base_url.split("/sample_add")[0]


  get_authenticator: =>
    ###
     * Get the authenticator value
    ###
    return $("input[name='_authenticator']").val()


  get_form: =>
    ###
     * Return the form element
    ###
    return $("#sample_add_form")


  get_fields: (samplenum) =>
    ###
     * Get all fields of the form
    ###
    form = @get_form()

    fields_selector = "tr[fieldname] td[samplenum] input"
    if samplenum?
      fields_selector = "tr[fieldname] td[samplenum=#{samplenum}] input"
    fields = $(fields_selector, form)
    return fields


  get_field_by_id: (id, samplenum) =>
    ###
     * Query the field by id
    ###

    # split the fieldname from the suffix
    [name, suffix] = id.split "_"

    # append the samplenum
    field_id = "#{name}-#{samplenum}"

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


  set_client: (samplenum, client) =>
    ###
     * Filter SamplePoints
    ###
    # filter Sample Points
    field = $("#SamplePoint-#{samplenum}")
    query = client.filter_queries.samplepoint
    @set_reference_field_query field, query


  set_sampletype: (samplenum, sampletype) =>
    ###
     * Recalculate partitions
     * Filter Sample Points
    ###

    # restrict the sample points
    field = $("#SamplePoint-#{samplenum}")
    query = sampletype.filter_queries.samplepoint
    @set_reference_field_query field, query

    # set the default container
    field = $("#DefaultContainerType-#{samplenum}")
    # apply default container if the field is empty
    if not field.val()
      uid = sampletype.container_type_uid
      title = sampletype.container_type_title
      @flush_reference_field field
      @set_reference_field field, uid, title

  ### EVENT HANDLER ###

  on_client_changed: (event) =>
    ###
     * Eventhandler when the client changed
    ###

    me = this
    el = event.currentTarget
    $el = $(el)
    uid = $el.attr "uid"
    samplenum = $el.closest("[samplenum]").attr "samplenum"

    console.debug "°°° on_client_changed: samplenum=#{samplenum} °°°"

    # Flush client depending fields
    field_ids = [
      "SamplePoint"
    ]
    $.each field_ids, (index, id) ->
      field = me.get_field_by_id id, samplenum
      me.flush_reference_field field

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
    samplenum = $el.closest("[samplenum]").attr "samplenum"
    has_sampletype_selected = $el.val()
    console.debug "°°° on_sampletype_change::UID=#{uid} SampleType=#{val}°°°"

    # deselect the sampletype if the field is empty
    if not has_sampletype_selected
      # XXX manually flush UID field
      $("input[type=hidden]", $el.parent()).val("")

    # Flush sampletype depending fields
    field_ids = [
      "SamplePoint"
    ]
    $.each field_ids, (index, id) ->
      field = me.get_field_by_id id, samplenum
      me.flush_reference_field field

    # trigger form:changed event
    $(me).trigger "form:changed"


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

    td1 = $(tr).find('td[samplenum="0"]').first()
    $td1 = $(td1)

    sample_count = parseInt($('input[id="sample_count"]').val(), 10)
    return unless sample_count > 1

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

      $.each [1..sample_count], (samplenum) ->
        # skip the first column
        return unless samplenum > 0

        _td = $tr.find("td[samplenum=#{samplenum}]")
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
      $.each [1..sample_count], (samplenum) ->
        # skip the first column
        return unless samplenum > 0
        _td = $tr.find("td[samplenum=#{samplenum}]")
        _el = $(_td).find("input[type=checkbox]")[index]
        $(_el).prop "checked", checked

    # Copy <select> fields
    $td1.find("select").each (index, el) ->
      console.debug "-> Copy select field"
      $el = $(el)
      value = $el.val()
      $.each [1..sample_count], (samplenum) ->
        # skip the first column
        return unless samplenum > 0
        _td = $tr.find("td[samplenum=#{samplenum}]")
        _el = $(_td).find("select")[index]
        $(_el).val value

    # Copy <input type="text"> fields
    $td1.find("input[type=text]").each (index, el) ->
      console.debug "-> Copy text field"
      $el = $(el)
      value = $el.val()
      $.each [1..sample_count], (samplenum) ->
        # skip the first column
        return unless samplenum > 0
        _td = $tr.find("td[samplenum=#{samplenum}]")
        _el = $(_td).find("input[type=text]")[index]
        $(_el).val value

    # Copy <textarea> fields
    $td1.find("textarea").each (index, el) ->
      console.debug "-> Copy textarea field"
      $el = $(el)
      value = $el.val()
      $.each [1..sample_count], (samplenum) ->
        # skip the first column
        return unless samplenum > 0
        _td = $tr.find("td[samplenum=#{samplenum}]")
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
    form = $("#sample_add_form")
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
    [name, samplenum] = $(element).attr("name").split("-")

    # Get all existing input fields and their names
    holding_div = $(element).parent().parent()
    existing_file_fields = holding_div.find("input[type='file']")
    existing_file_field_names = existing_file_fields.map (index, element) ->
      $(element).attr("name")

    # Generate a new name for the field and ensure it is not taken by another field already
    counter = 0
    newfieldname = $(element).attr("name")
    while newfieldname in existing_file_field_names
      newfieldname = "#{name}_#{counter}-#{samplenum}"
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
