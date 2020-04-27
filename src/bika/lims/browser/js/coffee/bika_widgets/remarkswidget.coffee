### Please use this command to compile this file into the proper folder:
    coffee --no-header -w -o ../../../../skins/bika/bika_widgets -c remarkswidget.coffee
###


class window.RemarksWidgetView

  load: =>
    console.debug "RemarksWidgetView::load"

    # bind the event handler to the elements
    @bind_eventhandler()

  ### INITIALIZERS ###

  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the form and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
    ###
    console.debug "RemarksWidgetView::bind_eventhandler"

    $("body").on "click", "input.saveRemarks", @on_remarks_submit
    $("body").on "keyup", "textarea[name='Remarks']", @on_remarks_change

    # dev only
    window.rem = @

  ### METHODS ###

  get_remarks_widget: (uid) =>
    ###
     * Shortcut to retrieve remarks widget from current page.
     * if uid is not specified, attempts to find widget.
    ###
    if uid?
      widgets = $(".ArchetypesRemarksWidget[data-uid='#{uid}']")
      if widgets.length == 0
        console.warn "[RemarksWidgetView] No widget found with uid #{uid}"
        return null
      return $(widgets[0])
    else
      widgets = $(".ArchetypesRemarksWidget")
      if widgets.length == 0
        console.warn "[RemarksWidgetView] No widget found"
        return null
      if widgets.length > 1
        msg = "[RemarksWidgetView] Multiple widgets found, please specify uid"
        console.warn msg
        return null
    return $(widgets[0])

  format: (value) =>
    ###
     * Output HTML string.
    ###
    remarks = value.replace(new RegExp("\n", "g"), "<br/>")
    return remarks

  update_remarks_history: (value, uid) =>
    ###
     * Clear and update the widget's History with the provided value.
    ###
    return if value.length < 1
    widget = @get_remarks_widget(uid)
    return if widget is null
    el = widget.find('.remarks_history')
    val = value[0]
    record_header = $("<div class='record-header'/>")
    record_header.append $("<span class='record-user'>"+val["user_id"]+"</span>")
    record_header.append $("<span class='record-username'>"+val["user_name"]+"</span>")
    record_header.append $("<span class='record-date'>"+val["created"]+"</span>")
    record_content = $("<div class='record-content'/>")
    record_content.html(@format(val["content"]))
    record = $("<div class='record' id='"+val['id']+"'/>")
    record.append record_header
    record.append record_content
    el.prepend record

  clear_remarks_textarea: (uid) =>
    ###
     * Clear textarea contents
    ###
    widget = @get_remarks_widget(uid)
    return if widget is null
    el = widget.find('textarea')
    el.val("")

  get_remarks: (uid) =>
    ###
     * Return the value currently displayed for the widget's remarks
     (HTML value)
     *
    ###
    widget = @get_remarks_widget(uid)
    return if widget is null
    return widget.find('.remarks_history').html()

  set_remarks: (value, uid) =>
    ###
     * Single function to post remarks, update widget, and clear textarea.
     *
    ###
    @post_remarks value, uid
    .done (data) ->
      @fetch_remarks uid
      .done (remarks) ->
        @update_remarks_history(remarks, uid)
        @clear_remarks_textarea(uid)
      .fail ->
        console.warn "Failed to get remarks"
    .fail ->
      console.warn "Failed to set remarks"

  ### ASYNC DATA METHODS ###

  fetch_remarks: (uid) =>
    ###
     * Get current value of field from /@@API/read
    ###

    deferred = $.Deferred()

    widget = @get_remarks_widget(uid)

    if widget is null
      return deferred.reject()

    fieldname = widget.attr("data-fieldname")

    @ajax_submit
      url: @get_portal_url() + "/@@API/read"
      data:
        catalog_name: "uid_catalog"
        UID: widget.attr('data-uid')
        include_fields: [fieldname]
    .done (data) ->
      return deferred.resolveWith this, [data.objects[0][fieldname]]
    return deferred.promise()

  post_remarks: (value, uid) =>
    ###
     * Submit the value to the field setter via /@@API/update.
     *
    ###
    deferred = $.Deferred()

    widget = @get_remarks_widget(uid)

    if widget is null
      return deferred.reject()

    fieldname = widget.attr("data-fieldname")

    options =
      url: @get_portal_url() + "/@@API/update"
      data:
        obj_uid: widget.attr('data-uid')
    options.data[fieldname] = value
    @ajax_submit options
    .done (data) ->
      return deferred.resolveWith this, [[]]
    return deferred.promise()

  ### EVENT HANDLERS ###

  on_remarks_change: (event) =>
    ###
     * Eventhandler for RemarksWidget's textarea changes
     *
    ###
    console.debug "°°° RemarksWidgetView::on_remarks_change °°°"
    el = event.target
    return unless el.value
    btn = el.parentElement.querySelector("input.saveRemarks")
    # Enable the button
    btn.disabled = false


  on_remarks_submit: (event) =>
    ###
     * Eventhandler for RemarksWidget's "Save Remarks" button
     *
    ###
    console.debug "°°° RemarksWidgetView::on_remarks_submit °°°"
    event.preventDefault()
    widget = $(event.currentTarget).parents(".ArchetypesRemarksWidget")
    @set_remarks widget.children("textarea").val(), widget.attr('data-uid')

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
    options.timeout ?= 600000  # 10 minutes timeout

    console.debug ">>> ajax_submit::options=", options

    $(this).trigger "ajax:submit:start"
    done = ->
      $(this).trigger "ajax:submit:end"
    fail = (request, status, error) ->
      msg = _("Sorry, an error occured: #{status}")
      window.bika.lims.portalMessage msg
      window.scroll 0, 0
    return $.ajax(options).done(done).fail(fail)

  get_portal_url: =>
    ###
     * Return the portal url (calculated in code)
    ###
    url = $("input[name=portal_url]").val()
    return url or window.portal_url
