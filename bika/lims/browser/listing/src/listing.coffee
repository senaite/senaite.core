###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"
import ListingAPI from "./api.coffee"
import Table from "./components/Table.coffee"
import FilterBar from "./components/FilterBar.coffee"
import SearchBox from "./components/SearchBox.coffee"
import Pagination from "./components/Pagination.coffee"
import ButtonBar from "./components/ButtonBar.coffee"

CONTAINER_ID = "ajax-contents-table-wrapper"


# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** SENAITE.CORE.LISTING::DOMContentLoaded: --> Loading ReactJS Controller"
  controller = ReactDOM.render <ListingController/>, document.getElementById CONTAINER_ID


class ListingController extends React.Component
  ###
   * Listing Table Controller
  ###

  constructor: (props) ->
    super(props)
    console.log "ListingController::constructor:props=", props

    # bind callbacks
    @filterByState = @filterByState.bind @
    @filterBySearchterm = @filterBySearchterm.bind @
    @sortBy = @sortBy.bind @
    @showMore = @showMore.bind @
    @selectUID = @selectUID.bind @
    @doAction = @doAction.bind @

    @el = document.getElementById "ajax-contents-table-wrapper"

    # get initial configuration data from the HTML attribute
    @columns = JSON.parse @el.dataset.columns
    @review_states = JSON.parse @el.dataset.review_states
    @form_id = @el.dataset.form_id
    @pagesize = parseInt @el.dataset.pagesize

    @api = new ListingAPI()

    @state =
      # filter, pagesize, sort_on, sort_order and review_state are initially set
      # from the request to allow bookmarks to specific searches
      filter: @api.get_url_parameter("#{@form_id}_filter")
      pagesize: parseInt @api.get_url_parameter("#{@form_id}_pagesize") or @pagesize
      sort_on: @api.get_url_parameter("#{@form_id}_sort_on")
      sort_order: @api.get_url_parameter("#{@form_id}_sort_order")
      review_state: @api.get_url_parameter("#{@form_id}_review_state")
      # The url_query is computed on the server and allows to bookmark listings
      url_query: ""
      # The API URL to call
      api_url: ""
      # form_id, columns and review_states are defined in the listing view and
      # passed in via a data attribute in the template, because they can be seen
      # as constant values
      form_id: @form_id
      columns: @columns
      review_states: @review_states
      # The data from the folderitems view call
      folderitems: []
      # total number of items in the database
      total: 0
      # The current active review_state item
      review_state_item: {}
      # UIDs of selected rows are stored in selected_uids.
      # These are sent when a transition action is clicked.
      selected_uids: []
      # The possible transition buttons
      transitions: []
      # Listing specific configs
      show_select_all_checkbox: no
      show_select_column: no


  getRequestOptions: ->
    ###
     * Only these state values should be sent to the server
    ###
    options =
      "review_state": @state.review_state
      "filter": @state.filter
      "sort_on": @state.sort_on
      "sort_order": @state.sort_order
      "pagesize": @state.pagesize

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
    console.log "ListingController::filterByState: review_state=#{review_state}"
    me = this
    @set_state
      review_state: review_state
    , ->
      me.fetch_transitions()

  filterBySearchterm: (filter="") ->
    ###
     * Filter the results by the given sarchterm
    ###
    console.log "ListingController::filterBySearchter: filter=#{filter}"
    @set_state filter: filter

  sortBy: (sort_on, sort_order) ->
    ###
     * Sort the results by the given sort_on index with the given sort_order
    ###
    console.log "sort_on=#{sort_on} sort_order=#{sort_order}"
    @set_state
      sort_on: sort_on
      sort_order: sort_order

  showMore: (pagesize) ->
    ###
     * Show more items
    ###
    console.debug "ListingController::showMore: pagesize=#{pagesize}"
    @set_state pagesize: parseInt pagesize

  doAction: (id) ->
    ###
     * Perform an action coming from the WF Action Buttons
    ###
    console.debug "ListingController::doAction: id=#{id}"

    if id == "clear_selection"
      @setState selected_uids: []
      return

  selectUID: (uid, toggle) ->
    ###
     * select/deselect the UID
    ###
    selected_uids = @state.selected_uids

    if toggle
      if uid == "all"
        all_uids = @state.folderitems.map (item) -> item.uid
        selected_uids = all_uids
      else
        selected_uids.push uid
    else
      if uid == "all"
        selected_uids = []
      else
        pos = selected_uids.indexOf uid
        selected_uids.splice pos, 1

    # set the new state
    me = this
    @setState selected_uids: selected_uids, ->
      # fetch all possible transitions
      me.fetch_transitions()

  set_state: (data, fetch=yes) ->
    ###
     * Set the state and fetch the folderitems
    ###
    me = this
    @setState data, ->
      if fetch then me.fetch_folderitems()

  fetch_transitions: ->
    ###
     * Fetch the possible transitions
    ###
    selected_uids = @state.selected_uids

    if selected_uids.length == 0
      @setState transitions: []
      return

    promise = @api.fetch_transitions uids: selected_uids

    me = this
    promise.then (data) ->
      me.setState data


  fetch_folderitems: ->
    ###
     * Fetch the folderitems
    ###
    promise = @api.fetch_folderitems @getRequestOptions()

    me = this
    promise.then (data) ->
      me.setState data, ->
        console.info "New State: ", me.state

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
          <SearchBox onSearch={@filterBySearchterm}
                     filter={@state.filter}
                     placeholder="Search ..." />
        </div>
      </div>
      <div className="row">
        <div className="col-sm-12 table-responsive">
          <Table
            className="contentstable table table-condensed table-hover table-striped table-sm small"
            onSort={@sortBy}
            onSelect={@selectUID}
            sort_on={@state.sort_on}
            sort_order={@state.sort_order}
            columns={@state.columns}
            review_states={@state.review_states}
            folderitems={@state.folderitems}
            selected_uids={@state.selected_uids}
            show_select_column={@state.show_select_column}
            show_select_all_checkbox={@state.show_select_all_checkbox}
            />
        </div>
      </div>
      <div className="row">
        <div className="col-sm-9">
          <ButtonBar className="buttonbar nav nav-pills"
                     onClick={@doAction}
                     selected_uids={@state.selected_uids}
                     transitions={@state.transitions}/>
        </div>
        <div className="col-sm-3">
          <Pagination
            id="pagination"
            className="pagination-controls"
            total={@state.total}
            onShowMore={@showMore}
            count={@state.count}
            pagesize={@pagesize}/>
        </div>
      </div>
    </div>
