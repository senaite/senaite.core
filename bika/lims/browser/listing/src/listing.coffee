###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"

import ButtonBar from "./components/ButtonBar.coffee"
import FilterBar from "./components/FilterBar.coffee"
import ListingAPI from "./api.coffee"
import Pagination from "./components/Pagination.coffee"
import SearchBox from "./components/SearchBox.coffee"
import Table from "./components/Table.coffee"

CONTAINER_ID = "ajax-contents-table"


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

    # bind callbacks
    @filterByState = @filterByState.bind @
    @filterBySearchterm = @filterBySearchterm.bind @
    @sortBy = @sortBy.bind @
    @showMore = @showMore.bind @
    @selectUID = @selectUID.bind @
    @doAction = @doAction.bind @

    # get the container element
    @el = document.getElementById CONTAINER_ID

    # get initial configuration data from the HTML attribute
    @columns = JSON.parse @el.dataset.columns
    @review_states = JSON.parse @el.dataset.review_states
    @form_id = @el.dataset.form_id
    @pagesize = parseInt @el.dataset.pagesize
    @api_url = @el.dataset.api_url

    # the API is responsible for async calls and knows about the endpoints
    @api = new ListingAPI
      api_url: @api_url

    @state =
      # loading indicator
      loading: no
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
      select_checkbox_name: "uids"
      post_action: "workflow_action"
      ajax_categories: no
      expand_all_categories: no

    # dev only
    window.list = @

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
      "ajax_categories": @state.ajax_categories

    console.debug("Request Options=", options)
    return options

  componentDidMount: ->
    ###
     * ReactJS event handler when the component did mount
    ###
    console.debug "ListingController::componentDidMount"

    # initial fetch of the folderitems
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
    console.debug "ListingController::filterByState: review_state=#{review_state}"
    me = this

    @set_state
      review_state: review_state

  filterBySearchterm: (filter="") ->
    ###
     * Filter the results by the given sarchterm
    ###
    console.debug "ListingController::filterBySearchter: filter=#{filter}"

    @set_state
     filter: filter

  sortBy: (sort_on, sort_order) ->
    ###
     * Sort the results by the given sort_on index with the given sort_order
    ###
    console.debug "sort_on=#{sort_on} sort_order=#{sort_order}"

    @set_state
      sort_on: sort_on
      sort_order: sort_order

  showMore: (pagesize) ->
    ###
     * Show more items
    ###
    console.debug "ListingController::showMore: pagesize=#{pagesize}"

    @set_state
      pagesize: parseInt pagesize

  doAction: (id) ->
    ###
     * Perform an action coming from the WF Action Buttons
    ###
    console.debug "ListingController::doAction: id=#{id}"

    # handle clear button separate
    if id == "clear_selection"
      @setState selected_uids: []
      return

    # get the form element
    form = document.getElementById @state.form_id

    # inject workflow action id for `BikaListing._get_form_workflow_action`
    input = document.createElement "input"
    input.setAttribute "type", "hidden"
    input.setAttribute "name", "workflow_action_id"
    input.setAttribute "value", id
    form.appendChild input

    return form.submit()

  selectUID: (uid, toggle) ->
    ###
     * select/deselect the UID
    ###

    # the selected UIDs from the state
    selected_uids = @state.selected_uids

    if toggle is yes
      # handle the select all checkbox
      if uid == "all"
        all_uids = @state.folderitems.map (item) -> item.uid
        selected_uids = all_uids
      # push the uid into the list of selected_uids
      else
        selected_uids.push uid
    else
      # flush all selected UIDs when the select_all checkbox is deselected
      if uid == "all"
        selected_uids = []
      else
        # remove the selected UID from the list of selected_uids
        pos = selected_uids.indexOf uid
        selected_uids.splice pos, 1

    # set the new list of selected UIDs to the state
    me = this
    @setState selected_uids: selected_uids, ->
      # fetch all possible transitions
      me.fetch_transitions()

  set_state: (data, fetch=yes) ->
    ###
     * Helper to set the state and reload the folderitems
    ###
    me = this
    @setState data, ->
      if fetch then me.fetch_folderitems()

  fetch_transitions: ->
    ###
     * Fetch the possible transitions
    ###
    selected_uids = @state.selected_uids

    # empty the possible transitions if no UID is selected
    if selected_uids.length == 0
      @setState transitions: []
      return

    # toggle loading on
    @setState loading: yes

    # fetch the transitions from the server
    promise = @api.fetch_transitions uids: selected_uids

    me = this
    promise.then (data) ->
      # data looks like this: {"transitions": [...]}
      me.setState data, ->
        console.debug "ListingController::fetch_transitions: NEW STATE=", me.state
      # toggle loading off
      me.setState loading: no

  fetch_folderitems: ->
    ###
     * Fetch the folderitems
    ###

    # toggle loading on
    @setState loading: yes

    # fetch the folderitems from the server
    promise = @api.fetch_folderitems @getRequestOptions()

    me = this
    promise.then (data) ->
      me.setState data, ->
        console.debug "ListingController::fetch_folderitems: NEW STATE=", me.state
      # toggle loading off
      me.setState loading: no

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
            select_checkbox_name={@state.select_checkbox_name}
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
