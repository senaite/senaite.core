### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../js -c email.coffee
###

# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** Loading Email Controller"
  controller = new EmailController()
  controller.initialize()


class EmailController

  constructor: () ->
    @bind_eventhandler()
    return @


  initialize: ->
    console.debug "senaite.core:Email::initialize"
    # Initialize overlays
    @init_overlays()


  init_overlays: ->
    ###
     * Initialize all overlays for later loading
     *
    ###
    console.debug "senaite.core:Email::init_overlays"

    $("a.attachment-link,a.report-link").prepOverlay
      subtype: "iframe"
      config:
        closeOnClick: yes
        closeOnEsc: yes
        onLoad: (event) ->
          overlay = this.getOverlay()
          iframe = overlay.find "iframe"
          iframe.css
            "background": "white"


  bind_eventhandler: =>
    ###
     * Binds callbacks on elements
     *
     * N.B. We attach all the events to the body and refine the selector to
     * delegate the event: https://learn.jquery.com/events/event-delegation/
     *
    ###
    console.debug "senaite.core::bind_eventhandler"

    # Toggle additional attachments visibility
    $("body").on "click", "#add-attachments", @on_add_attachments_click

    # Select/deselect additional attachments
    $("body").on "change", ".attachments input[type='checkbox']", @on_attachments_select


  get_base_url: ->
    ###
     * Calculate the current base url
    ###
    return document.URL.split("?")[0]


  get_api_url: (endpoint) ->
    ###
     * Build API URL for the given endpoint
     * @param {string} endpoint
     * @returns {string}
    ###
    base_url = @get_base_url()
    return "#{base_url}/#{endpoint}"


  ajax_fetch: (endpoint, init) ->
    ###
     * Call resource on the server
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
    ###

    url = @get_api_url endpoint

    init ?= {}
    init.method ?= "POST"
    init.credentials ?= "include"
    init.body ?= null
    init.header ?= null

    console.info "Email::fetch:endpoint=#{endpoint} init=",init
    request = new Request(url, init)
    return fetch(request).then (response) ->
      return response.json()


  is_visible: (element) ->
    ###
     * Checks if the element is visible
    ###
    if $(element).css("display") is "none"
      return no
    return yes


  toggle_attachments_container: (toggle=null) =>
    ###
     * Toggle the visibility of the attachments container
    ###

    button = $("#add-attachments")
    container = $("#additional-attachments-container")

    visible = @is_visible container
    if toggle isnt null
      visible = if toggle then no else yes

    if visible is yes
      container.hide()
      button.text "+"
    else
      container.show()
      button.text "-"


  update_size_info: (data) ->
    ###
     * Update the total size of the selected attachments
    ###
    if not data
      console.warn "No valid size information: ", data
      return null

    unit = "kB"
    $("#attachment-files").text "#{data.files}"

    if data.limit_exceeded
      $("#email-size").addClass "text-danger"
      $("#email-size").text "#{data.size} #{unit} > #{data.limit} #{unit}"
      $("input[name='send']").prop "disabled", on
    else
      $("#email-size").removeClass "text-danger"
      $("#email-size").text "#{data.size} #{unit}"
      $("input[name='send']").prop "disabled", off


  on_add_attachments_click: (event) =>
    console.debug "°°° Email::on_add_attachments_click"
    event.preventDefault()
    @toggle_attachments_container()


  on_attachments_select: (event) =>
    console.debug "°°° Email::on_attachments_select"

    # extract the form data
    form = $("#send_email_form")
    # form.serialize does not include file attachments
    # form_data = form.serialize()
    form_data = new FormData(form[0])

    init =
      body: form_data
    @ajax_fetch "recalculate_size", init
    .then (data) =>
      @update_size_info data
