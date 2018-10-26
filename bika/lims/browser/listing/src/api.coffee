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

  fetch_columns: ->
    ###
     * Fetch columns
     * @returns {Promise}
    ###
    return @get_json "columns",
      method: "GET"

  fetch_review_states: ->
    ###
     * Fetch review states
     * @returns {Promise}
    ###
    return @get_json "review_states",
      method: "GET"

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
