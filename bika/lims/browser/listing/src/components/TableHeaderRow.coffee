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
    @on_context_menu = @on_context_menu.bind @

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

  on_context_menu: (event) ->
    ###
     * Event handler for contextmenu
    ###
    event.preventDefault()

    rect = event.currentTarget.getBoundingClientRect()

    x = event.clientX - rect.x
    y = event.clientY - rect.y

    console.debug "TableHeaderRow::on_context_menu: x=#{x} y=#{y}"

    @props.on_context_menu x, y

  is_required_column: (key) ->
    ###
     * Check if the column is required
    ###

    # XXX This is a workaround for a missing key within the column definition
    folderitems = @props.folderitems or []
    if folderitems.length == 0
      return no
    first_item = folderitems[0]
    required = first_item.required or []
    return key in required

  get_sort_index: (key, column) ->
    ###
     * Get the sort index of the given column
    ###

    # disallow sorting when categories are shown
    if @props.show_categories
      return null

    index = column.index

    # lookup the column key in the available indexes
    catalog_indexes = @props.catalog_indexes

    # if the index is set, return immediately
    if index and index in catalog_indexes
      return index

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

    # insert table columns in the right order
    for key in @props.table_columns

      # get the column object
      column = @props.columns[key]

      title = column.title
      index = @get_sort_index key, column
      sortable = index or no
      # overwrite if sortable is explicitly set to false
      if column.sortable is no
        sortable = no
      # sort_on is the current sort index
      sort_on = @props.sort_on or "created"
      sort_order = @props.sort_order or "ascending"
      # check if the current sort_on is the index of this column
      is_sort_column = index is sort_on
      # check if the column is required
      required = @is_required_column key

      cls = [key]
      if sortable
        cls.push "sortable"
      if is_sort_column and sortable
        cls.push "active #{sort_order}"
      if required
        cls.push "required"
      cls = cls.join " "

      cells.push(
        <TableHeaderCell
          key={key}  # internal key
          {...@props}  # pass in all properties from the table component
          title={title}
          index={index}
          sort_order={sort_order}
          className={cls}
          onClick={if sortable then @on_header_column_click else undefined}
          />
      )

    return cells

  render: ->
    <tr onContextMenu={@on_context_menu}>
      {@build_cells()}
    </tr>


export default TableHeaderRow
