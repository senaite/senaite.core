###
 * ReactJS controlled component
###
import React from "react"
import ReactDOM from "react-dom"

import ButtonBar from "./components/ButtonBar.coffee"
import FilterBar from "./components/FilterBar.coffee"
import ListingAPI from "./api.coffee"
import Loader from "./components/Loader.coffee"
import Pagination from "./components/Pagination.coffee"
import SearchBox from "./components/SearchBox.coffee"
import Table from "./components/Table.coffee"
import TableContextMenu from "./components/TableContextMenu.coffee"

import "./listing.css"

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
    @toggleContextMenu = @toggleContextMenu.bind @
    @toggleColumn = @toggleColumn.bind @

    # get the container element
    @el = document.getElementById CONTAINER_ID

    # get initial configuration data from the HTML attribute
    @columns = JSON.parse @el.dataset.columns
    @review_states = JSON.parse @el.dataset.review_states
    @form_id = @el.dataset.form_id
    @api_url = @el.dataset.api_url
    @pagesize = parseInt @el.dataset.pagesize

    # the API is responsible for async calls and knows about the endpoints
    @api = new ListingAPI
      api_url: @api_url

    @state =
      # loading indicator
      loading: yes
      # context menu visibility and coordinates
      contextmenu_show: no
      contextmenu_x: 0
      contextmenu_y: 0
      # filter, pagesize, sort_on, sort_order and review_state are initially set
      # from the request to allow bookmarks to specific searches
      filter: @api.get_url_parameter("#{@form_id}_filter")
      pagesize: parseInt(@api.get_url_parameter("#{@form_id}_pagesize")) or @pagesize
      sort_on: @api.get_url_parameter("#{@form_id}_sort_on")
      sort_order: @api.get_url_parameter("#{@form_id}_sort_order")
      review_state: @api.get_url_parameter("#{@form_id}_review_state") or "default"
      # The query string is computed on the server and allows to bookmark listings
      query_string: ""
      # The column toggles define the visible columns per user setting
      column_toggles: []
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
      # The categories of the folderitems
      categories: []
      # total number of items in the database
      total: 0
      # UIDs of selected rows are stored in selected_uids.
      # These are sent when a transition action is clicked.
      selected_uids: []
      # The possible transition buttons
      transitions: []
      # The available catalog indexes for sorting
      catalog_indexes: []
      # Listing specific configs
      allow_edit: no
      show_select_all_checkbox: no
      show_select_column: no
      select_checkbox_name: "uids"
      post_action: "workflow_action"
      show_categories: no
      expand_all_categories: no
      show_more: no
      limit_from: 0

    # dev only
    window.lv = @

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
      "limit_from": @state.limit_from
      "selected_uids": @state.selected_uids,

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

  toggleContextMenu: (x, y, toggle) ->
    ###
     * Toggle the context menu
    ###
    console.debug "ListingController::toggleContextMenu: x=#{x} y=#{y}"

    toggle ?= not @state.contextmenu_show

    @setState
      contextmenu_show: toggle
      contextmenu_x: x
      contextmenu_y: y

  toggleColumn: (column) ->
    ###
     * Toggle the column on or off
    ###
    console.debug "ListingController::toggleColumn: column=#{column}"

    # reset the default visible columns
    if column == "reset"
      columns = @get_default_columns()
      @set_column_toggles columns

      return columns

    # get the current displayed columns
    columns = @get_visible_columns()
    # check if the current column is displayed
    index = columns.indexOf column

    if index > -1
      # remove the column
      columns.splice index, 1
    else
      # add the column
      columns.push column

    # set the new column toggles
    @set_column_toggles columns

    return columns

  filterByState: (review_state="default") ->
    ###
     * Filter the results by the given state
    ###
    console.debug "ListingController::filterByState: review_state=#{review_state}"

    @set_state
      review_state: review_state
      pagesize: @pagesize  # reset to the initial pagesize on state change
      limit_from: 0

  filterBySearchterm: (filter="") ->
    ###
     * Filter the results by the given sarchterm
    ###
    console.debug "ListingController::filterBySearchter: filter=#{filter}"

    @set_state
      filter: filter
      pagesize: @pagesize  # reset to the initial pagesize on search
      limit_from: 0

  sortBy: (sort_on, sort_order) ->
    ###
     * Sort the results by the given sort_on index with the given sort_order
    ###
    console.debug "sort_on=#{sort_on} sort_order=#{sort_order}"

    @set_state
      sort_on: sort_on
      sort_order: sort_order
      pagesize: @get_item_count() # keep the current number of items on sort
      limit_from: 0

  showMore: (pagesize) ->
    ###
     * Show more items
    ###
    console.debug "ListingController::showMore: pagesize=#{pagesize}"

    # the existing folderitems
    folderitems = @state.folderitems

    me = this
    @setState
      pagesize: parseInt pagesize
      limit_from: @state.folderitems.length
    , ->
      # N.B. we're using limit_from here, so we must append the returning
      #      folderitems to the existing ones
      promise = me.api.fetch_folderitems me.getRequestOptions()
      promise.then (data) ->
        if data.folderitems.length > 0
          console.debug "Adding #{data.folderitems.length} more folderitems..."
          # append the new folderitems to the existing ones
          new_folderitems = folderitems.concat data.folderitems
          me.setState folderitems: new_folderitems

  doAction: (id, url) ->
    ###
     * Perform an action coming from the WF Action Buttons
    ###

    # handle clear button separate
    if id == "clear_selection"
      @setState selected_uids: []
      return

    # get the form element
    form = document.getElementById @state.form_id

    # N.B. Transition submit buttons are suffixed with `_transition`, because
    #      otherwise the form.submit call below retrieves the element instead of
    #      doing the method call.
    action = id.split("_transition")[0]

    # inject workflow action id for `BikaListing._get_form_workflow_action`
    input = document.createElement "input"
    input.setAttribute "type", "hidden"
    input.setAttribute "id", id
    input.setAttribute "name", "workflow_action_id"
    input.setAttribute "value", action
    form.appendChild input

    # Override the form action when a custom URL is given
    if url then form.action = url

    # inject all hidden input fields for UIDs that are currently not in the DOM
    for uid in @state.selected_uids
      # skip injection if the element is currently in the DOM
      if document.querySelectorAll("input[value='#{uid}']:not([disabled])").length > 0
        continue
      input = document.createElement "input"
      input.setAttribute "type", "hidden"
      input.setAttribute "name", "#{@state.select_checkbox_name}:list"
      input.setAttribute "value", uid
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
        # keep existing selected uids
        for uid in all_uids
          if uid not in selected_uids
            selected_uids.push uid
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
    @setState
     selected_uids: selected_uids
    , ->
      # fetch all possible transitions
      me.fetch_transitions()

  get_review_state_by_id: (id) ->
    ###
     * Fetch the current review_state item by id
    ###
    current = null

    # review_states is the list of review_state items from the listing view
    for review_state in @review_states
      if review_state.id == id
        current = review_state
        break

    if not current
      throw "No review_state definition found for ID #{id}"

    return current

  get_column_order: ->
    ###
     * Get the column order defined in the current selected review_state item
    ###
    review_state_item = @get_review_state_by_id @state.review_state
    return review_state_item.columns or []

  get_visible_columns: ->
    ###
     * Get the visible columns according to the user settings
    ###

    # get the current user defined column toggles
    column_toggles = @get_column_toggles()

    if column_toggles.length > 0
      columns = []
      for key in @get_column_order()
        if key in column_toggles
          columns.push key
      return columns

    return @get_default_columns()

  get_default_columns: ->
    ###
     * Get the default visible columns of the listing
    ###

    columns = []
    for key in @get_column_order()
      column = @columns[key]
      if column.toggle
        columns.push key
    return columns

  set_column_toggles: (columns) ->
    ###
     * Set the user defined column toggles to the local state and local storage
    ###
    console.debug "ListingController::set_column_toggles: columns=", columns

    # set the columns to the local storage
    key = location.pathname
    storage = window.localStorage
    storage.setItem key, JSON.stringify(columns)

    @setState
      column_toggles: columns

  get_column_toggles: ->
    ###
     * Return the current column toggles from the local storage
    ###

    key = location.pathname
    storage = window.localStorage
    columns = storage.getItem key

    if not columns
      return @state.column_toggles

    try
      return JSON.parse columns
    catch
      return @state.column_toggles

  get_column_count: ->
    ###
     * Calculate the current number of displayed columns
    ###
    # get the current visible columns
    visible_columns = @get_visible_columns()

    count = visible_columns.length
    # add 1 if the select column is rendered
    if @state.show_select_column
      count += 1
    return count

  get_item_count: ->
    ###
     * Return the current shown items
    ###
    return @state.folderitems.length

  toggle_loader: (toggle=off) ->
    ###
     * Toggle the loader on/off
    ###
    @setState loading: toggle

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

    # turn loader on
    @toggle_loader on

    # fetch the transitions from the server
    promise = @api.fetch_transitions uids: selected_uids

    me = this
    promise.then (data) ->
      # data looks like this: {"transitions": [...]}
      me.setState data, ->
        console.debug "ListingController::fetch_transitions: NEW STATE=", me.state
        # turn loader off
        me.toggle_loader off

  fetch_folderitems: ->
    ###
     * Fetch the folderitems
    ###

    # turn loader on
    @toggle_loader on

    # fetch the folderitems from the server
    promise = @api.fetch_folderitems @getRequestOptions()

    me = this
    promise.then (data) ->
      console.debug "ListingController::fetch_folderitems: GOT RESPONSE=", data
      me.setState data, ->
        console.debug "ListingController::fetch_folderitems: NEW STATE=", me.state
        # turn loader off
        me.toggle_loader off

    return promise

  render: ->
    ###
     * Listing Table
    ###
    <div className="listing-container">
      <div className="row">
        <div className="col-sm-8">
          <FilterBar
            className="filterbar nav nav-pills"
            on_filter_button_clicked={@filterByState}
            review_state={@state.review_state}
            review_states={@state.review_states}/>
        </div>
        <div className="col-sm-1 text-right">
          <Loader loading={@state.loading} />
        </div>
        <div className="col-sm-3 text-right">
          <SearchBox
            on_search={@filterBySearchterm}
            filter={@state.filter}
            placeholder={_("Search")} />
        </div>
      </div>
      <div className="row">
        <div className="col-sm-12 table-responsive">
          {@state.loading and <div id="table-overlay"/>}
          <TableContextMenu
            show={@state.contextmenu_show}
            x={@state.contextmenu_x}
            y={@state.contextmenu_y}
            title={_("Display Columns")}
            columns={@state.columns}
            column_order={@get_column_order()}
            table_columns={@get_visible_columns()}
            on_column_toggle={@toggleColumn}
            on_context_menu={@toggleContextMenu}
            />
          <Table
            className="contentstable table table-condensed table-hover table-striped table-sm small"
            allow_edit={@state.allow_edit}
            on_header_column_click={@sortBy}
            on_select_checkbox_checked={@selectUID}
            on_context_menu={@toggleContextMenu}
            sort_on={@state.sort_on}
            sort_order={@state.sort_order}
            catalog_indexes={@state.catalog_indexes}
            columns={@state.columns}
            column_toggles={@state.column_toggles}
            column_count={@get_column_count()}
            column_order={@get_column_order()}
            table_columns={@get_visible_columns()}
            review_state={@state.review_state}
            review_states={@state.review_states}
            folderitems={@state.folderitems}
            selected_uids={@state.selected_uids}
            select_checkbox_name={@state.select_checkbox_name}
            show_select_column={@state.show_select_column}
            show_select_all_checkbox={@state.show_select_all_checkbox}
            categories={@state.categories}
            show_categories={@state.show_categories}
            filter={@state.filter}
            />
        </div>
      </div>
      <div className="row">
        <div className="col-sm-8">
          <ButtonBar className="buttonbar nav nav-pills"
                     on_transition_button_click={@doAction}
                     selected_uids={@state.selected_uids}
                     transitions={@state.transitions}/>
        </div>
        <div className="col-sm-1 text-right">
          <Loader loading={@state.loading} />
        </div>
        <div className="col-sm-3 text-right">
          <Pagination
            id="pagination"
            className="pagination-controls"
            total={@state.total}
            show_more_button_title={_("Show more")}
            onShowMore={@showMore}
            show_more={@state.show_more}
            count={@get_item_count()}
            pagesize={@state.pagesize}/>
        </div>
      </div>
    </div>
