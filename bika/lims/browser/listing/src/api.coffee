###
 * Listing API Module
###

class ListingAPI

  constructor: (props) ->
    console.debug "ListingAPI::constructor"
    @api_url = props.api_url
    return @

  get_api_url: (endpoint) ->
    ###
     * Build API URL for the given endpoint
     * @param {string} endpoint
     * @returns {string}
    ###
    return "#{@api_url}/#{endpoint}"

  get_url_parameter: (name) ->
    ###
     * Parse a request parameter by name
    ###
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]')
    regex = new RegExp('[\\?&]' + name + '=([^&#]*)')
    results = regex.exec(location.search)
    if results == null
      return ""
    return decodeURIComponent(results[1].replace(/\+/g, ' '))

  get_json: (endpoint, options) ->
    ###
     * Fetch Ajax API resource from the server
     * @param {string} endpoint
     * @param {object} options
     * @returns {Promise}
    ###
    options ?= {}

    method = options.method or "POST"
    data = JSON.stringify(options.data) or "{}"

    url = @get_api_url endpoint
    init =
      method: method
      headers:
        "Content-Type": "application/json"
      body: if method is "POST" then data else null
      credentials: "include"
    console.info "ListingAPI::fetch:endpoint=#{endpoint} init=",init
    request = new Request(url, init)
    return fetch(request).then (response) ->
      return response.json()

  set: (data) ->
    ###
     * Set value of an editable field to the server
     * @returns {Promise}
    ###
    options =
      data: data or {}
      method: "POST"
    return @get_json "set", options

  set_fields: (data) ->
    ###
     * Set values of multiple fields
     * @returns {Promise}
    ###
    options =
      data: data or {}
      method: "POST"
    return @get_json "set_fields", options

  query_folderitems: (data) ->
    ###
     * Query folderitems
     * @returns {Promise}
    ###
    options =
      data: data or {}
      method: "POST"
    return @get_json "query_folderitems", options

  fetch_children: (data) ->
    ###
     * Query children
     * @returns {Promise}
    ###
    options =
      data: data or {}
      method: "POST"
    return @get_json "get_children", options

  fetch_folderitems: (data) ->
    ###
     * Fetch folder items
     * @returns {Promise}
    ###
    options =
      data: data or {}
      method: "POST"
    return @get_json "folderitems", options

  fetch_transitions: (data) ->
    ###
     * Fetch possible transitions
     * @returns {Promise}
    ###
    options =
      data: data or {}
      method: "POST"
    return @get_json "transitions", options


export default ListingAPI
