###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"
import ListingAPI from "./api.coffee"
import Table from "./components/Table.coffee"
import FilterBar from "./components/FilterBar.coffee"


# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** SENAITE.CORE.LISTING::DOMContentLoaded: --> Loading ReactJS Controller"
  controller = ReactDOM.render <ListingController/>, document.getElementById "ajax-contents-table-wrapper"


class ListingController extends React.Component
  ###
   * Listing Table Controller
  ###

  constructor: (props) ->
    super(props)
    console.log "ListingController::constructor:props=", props

    @handleSubmit = @handleSubmit.bind @
    @handleChange = @handleChange.bind @
    @filterResults = @filterResults.bind @

    @el = document.getElementById "ajax-contents-table-wrapper"
    @view_name = @el.dataset.view_name

    @json_columns = @el.dataset.columns
    @json_review_states = @el.dataset.review_states

    @columns = JSON.parse @json_columns
    @review_states = JSON.parse @json_review_states

    @api = new ListingAPI(
      view_name: @view_name
      form_id: @view_name
    )

    @state =
      folderitems: []
      columns: @columns or {}
      review_state: @api.get_url_parameter("review_state") or "default"
      review_states: @review_states or []

  getRequestOptions: ->
    ###
     * Options to be sent to the server
    ###
    options =
      review_state: @state.review_state

    console.debug("Request Options=", options)
    return options

  componentDidMount: ->
    ###
     * ReactJS event handler when the component did mount
    ###
    console.debug "ListingController::componentDidMount"
    @fetch_folderitems()

  componentDidUpdate: ->
    ###
     * ReactJS event handler when the component did update
    ###
    console.debug "ListingController::componentDidUpdate"

  handleSubmit: (event) ->
    ###
     * Intercept form submit of the react form component
    ###
    console.debug "ListingController::handleSubmit"
    event.preventDefault()

  handleChange: (event) ->
    ###
     * Handle changes of the of any introduced form components
    ###
    console.debug "ListingController::handleChange"
    target = event.target

  filterResults: (event) ->
    ###
     * Handler for the Review State filter buttons
    ###

    me = this
    el = event.currentTarget
    review_state = el.id

    console.log "ListingController::filterResults: review_state='#{review_state}'"

    @setState
      review_state: review_state
    , ->
      me.fetch_folderitems()

  fetch_folderitems: ->
    ###
     * Fetch the folderitems
    ###
    me = this

    promise = @api.fetch_folderitems
      review_state: @state.review_state

    promise.then (folderitems) ->
      me.setState
        folderitems: folderitems

    return promise

  render: ->
    ###
     * Listing Table
    ###
    <div className="row">
      <div className="col-sm-12">
        <FilterBar className="filterbar nav nav-pills"
                   onClick={@filterResults}
                   review_state={@state.review_state}
                   review_states={@state.review_states}/>
      </div>
      <div className="col-sm-12 table-responsive">
        <Table
          className="contentstable table table-condensed table-hover table-striped table-sm small"
          columns={@state.columns}
          review_states={@state.review_states}
          folderitems={@state.folderitems}/>
      </div>
    </div>
