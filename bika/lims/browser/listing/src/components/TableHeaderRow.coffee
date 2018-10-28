import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableHeaderCell from "./TableHeaderCell.coffee"


class TableHeaderRow extends React.Component
  ###
   * The table header row component renders a single row with cells
  ###

  constructor: (props) ->
    super(props)
    @on_header_column_click = @on_header_column_click.bind @

  on_header_column_click: (event) ->
    ###
     * Event handler when a header columns was clicked
    ###
    el = event.currentTarget

    index = el.getAttribute "index"
    sort_order = el.getAttribute "sort_order"

    if not index
      return

    console.debug "HEADER CLICKED sort_on='#{index}' sort_order=#{sort_order}"

    # toggle the sort order if the clicked column was the active one
    if "active" in el.classList
      if sort_order == "ascending"
        sort_order = "descending"
      else
        sort_order = "ascending"

    # call the parent event handler with the sort index and the sort order
    @props.on_header_column_click index, sort_order

  get_sort_index: (key, column) ->
    ###
     * Get the sort index of the given column
    ###

    # disallow sorting when categories are shown
    if @props.show_categories
      return null

    index = column.index

    # if the index is set, return immediately
    if index
      return index

    # lookup the column key in the available indexes
    catalog_indexes = @props.catalog_indexes

    # lookup the title in the available indexes
    if key in catalog_indexes
      return key

    # lookup the title getter in the available indexes
    get_key = "get" + key.charAt(0).toUpperCase() + key.slice(1)
    if get_key in catalog_indexes
      return get_key
    return null

  all_selected: ->
    ###
     * Checks if all visible items are selected
    ###
    for item in @props.folderitems
      if item.uid not in @props.selected_uids
        return no
    return yes

  build_cells: ->
    ###
     * Build all cells for the row
    ###

    cells = []

    item = @props.item
    checkbox_name = "select_all"
    checkbox_value = "all"

    # insert select column
    if @props.show_select_column

      # check if all visible rows are selected
      all_selected = @all_selected()

      show_select_all_checkbox = @props.show_select_all_checkbox

      cells.push(
        <th key="select_all">
          {show_select_all_checkbox and
            <Checkbox
              name={checkbox_name}
              value={checkbox_value}
              checked={all_selected}
              onChange={@props.on_select_checkbox_checked}/>}
        </th>
      )

    # insert visible columns in the right order
    for key in @props.column_order

      # get the column object
      column = @props.columns[key]

      # skip hidden colums
      if not column.toggle
        continue

      title = column.title
      index = @get_sort_index key, column
      sortable = index or no
      # sort_on is the current sort index
      sort_on = @props.sort_on or "created"
      sort_order = @props.sort_order or "ascending"
      # check if the current sort_on is the index of this column
      is_sort_column = index is sort_on

      cls = [key]
      if sortable
        cls.push "sortable"
      if is_sort_column
        cls.push "active #{sort_order}"
      cls = cls.join " "

      cells.push(
        <TableHeaderCell
          key={key}
          title={column.title}
          index={index}
          sort_order={sort_order}
          className={cls}
          onClick={@on_header_column_click}
          />
      )

    return cells

  render: ->
    <tr className={this.props.className}>
      {this.build_cells()}
    </tr>


export default TableHeaderRow
