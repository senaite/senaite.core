###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"
import ListingAPI from "./api.coffee"
import Table from "./components/Table.coffee"
import FilterBar from "./components/FilterBar.coffee"
import SearchBox from "./components/SearchBox.coffee"


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

    @filterByState = @filterByState.bind @
    @filterBySearchterm = @filterBySearchterm.bind @

    @el = document.getElementById "ajax-contents-table-wrapper"
    @view_name = @el.dataset.view_name
    @form_id = @el.dataset.form_id

    @json_columns = @el.dataset.columns
    @json_review_states = @el.dataset.review_states

    @columns = JSON.parse @json_columns
    @review_states = JSON.parse @json_review_states

    @api = new ListingAPI()

    @state =
      folderitems: []
      columns: @columns or {}
      filter: @api.get_url_parameter("#{@form_id}_filter") or ""
      review_state: @api.get_url_parameter("#{@form_id}_review_state") or "default"
      review_states: @review_states or []

  getRequestOptions: ->
    ###
     * Options to be sent to the server
    ###
    options =
      "#{@form_id}_review_state": @state.review_state
      "#{@form_id}_filter": @state.filter

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

  filterByState: (review_state="default") ->
    ###
     * Filter the results by the given state
    ###
    me = this

    @setState
      review_state: review_state
    , ->
      me.fetch_folderitems()

  filterBySearchterm: (filter="") ->
    ###
     * Filter the results by the given sarchterm
    ###
    me = this

    @setState
      filter: filter
    , ->
      me.fetch_folderitems()

  fetch_folderitems: ->
    ###
     * Fetch the folderitems
    ###
    me = this

    promise = @api.fetch_folderitems @getRequestOptions()

    promise.then (folderitems) ->
      me.setState
        folderitems: folderitems

    return promise

  render: ->
    ###
     * Listing Table
    ###
    <div className="listing-container">
    <div className="row">
      <div className="col-sm-9">
        <FilterBar className="filterbar nav nav-pills"
                   onClick={@filterByState}
                   review_state={@state.review_state}
                   review_states={@state.review_states}/>
      </div>
      <div className="col-sm-3">
        <SearchBox onSearch={@filterBySearchterm} placeholder="Search ..." />
      </div>
    </div>
    <div className="row">
      <div className="col-sm-12 table-responsive">
        <Table
          className="contentstable table table-condensed table-hover table-striped table-sm small"
          columns={@state.columns}
          review_states={@state.review_states}
          folderitems={@state.folderitems}/>
      </div>
    </div>
    </div>
