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


    @handleSubmit = @handleSubmit.bind(this)
    @handleChange = @handleChange.bind(this)

    @el = document.getElementById "ajax-contents-table-wrapper"
    @view_name = @el.dataset.view_name
    @json_columns = @el.dataset.columns
    @json_review_states = @el.dataset.review_states

    @api = new ListingAPI(
      view_name: @view_name
    )

    @state =
      folderitems: []
      columns: JSON.parse @json_columns
      review_states: JSON.parse @json_review_states

  componentDidMount: ->
    ###
     * ReactJS event handler when the component did mount
    ###
    console.debug "ListingController::componentDidMount"

    @api.fetch_folderitems().then (
      (folderitems) ->
        @setState folderitems: folderitems
      ).bind(this)

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
    el = event.target
    console.log "ListingController:Filter button '#{el.id}' was clicked"


  render: ->
    ###
     * Listing Table
    ###
    <div className="row">
      <div className="col-sm-12">
        <FilterBar className="filterbar nav nav-pills"
                   onClick={@filterResults}
                   review_states={@state.review_states}/>
      </div>
      <div className="col-sm-12">
        <Table
          className="contentstable table table-condensed table-hover table-striped table-sm small"
          columns={@state.columns}
          review_states={@state.review_states}
          folderitems={@state.folderitems}/>
      </div>
    </div>
