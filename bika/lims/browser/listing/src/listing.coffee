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

    @el = document.getElementById "ajax-contents-table-wrapper"

    # get initial configuration data from the HTML attribute
    @columns = JSON.parse @el.dataset.columns
    @review_states = JSON.parse @el.dataset.review_states
    @form_id = @el.dataset.form_id
    @pagesize = parseInt @el.dataset.pagesize

    @api = new ListingAPI()

    @state =
      api_url: ""
      columns: @columns
      filter: @api.get_url_parameter("#{@form_id}_filter")
      folderitems: []
      form_id: @form_id
      pagesize: parseInt @api.get_url_parameter("#{@form_id}_pagesize") or @pagesize
      review_state: @api.get_url_parameter("#{@form_id}_review_state")
      review_states: @review_states
      sort_on: @api.get_url_parameter("#{@form_id}_sort_on")
      sort_order: @api.get_url_parameter("#{@form_id}_sort_order")
      total: 0
      url_query: ""

  getRequestOptions: ->
    ###
     * Options to be sent to the server
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

  sortBy: (sort_on, sort_order) ->
    ###
     * Sort the results by the given sort_on index with the given sort_order
    ###
    console.log "sort_on=#{sort_on} sort_order=#{sort_order}"

    me = this

    @setState
      sort_on: sort_on
      sort_order: sort_order
    , ->
      me.fetch_folderitems()

  showMore: (pagesize) ->
    ###
     * Show more items
    ###
    console.debug "showMore: pagesize=#{pagesize}"

    me = this

    pagesize = parseInt pagesize

    @setState
      pagesize: pagesize
    , ->
      me.fetch_folderitems()


  fetch_folderitems: ->
    ###
     * Fetch the folderitems
    ###
    me = this

    promise = @api.fetch_folderitems @getRequestOptions()

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
          <SearchBox onSearch={@filterBySearchterm} placeholder="Search ..." />
        </div>
      </div>
      <div className="row">
        <div className="col-sm-12 table-responsive">
          <Table
            className="contentstable table table-condensed table-hover table-striped table-sm small"
            onSort={@sortBy}
            sort_on={@state.sort_on}
            sort_order={@state.sort_order}
            columns={@state.columns}
            review_states={@state.review_states}
            folderitems={@state.folderitems}/>
        </div>
      </div>
      <div className="row">
        <div className="col-sm-9">
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
