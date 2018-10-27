import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableHeaderCell from "./TableHeaderCell.coffee"


class TableHeaderRow extends React.Component
  ###
   * The table header row component renders a single row with cells
  ###

  constructor: (props) ->
    super(props)
    @onHeaderCellClick = @onHeaderCellClick.bind @

  onHeaderCellClick: (event) ->
    el = event.currentTarget
    index = el.getAttribute "index"
    sort_order = el.getAttribute "sort_order"
    console.debug "HEADER CLICKED sort_on='#{index}' sort_order=#{sort_order}"

    if "active" in el.classList
      if sort_order == "ascending"
        sort_order = "descending"
      else
        sort_order = "ascending"

    @props.onSort index, sort_order

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
      selected_count = @props.selected_uids.length
      folderitems_count = @props.folderitems.length
      checked = selected_count > 0 and selected_count == folderitems_count

      show_select_all_checkbox = @props.show_select_all_checkbox

      cells.push(
        <th key="select_all">
          {show_select_all_checkbox and
            <Checkbox
              name={checkbox_name}
              value={checkbox_value}
              checked={checked}
              onChange={@props.on_select_checkbox_checked}/>}
        </th>
      )

    # insert column titles for visible columns
    for key, column of @props.columns

      # skip hidden colums
      if not column.toggle
        continue

      title = column.title
      index = column.index or ""
      sortable = column.sortable or no
      sort_on = @props.sort_on or "created"
      sort_order = @props.sort_order or "ascending"
      is_sort_column = index == sort_on

      cls = [key]
      if sortable
        cls.push "sortable"
      if is_sort_column
        cls.push "active #{sort_order}"

      cells.push(
        <TableHeaderCell
          key={key}
          className={cls.join " "}
          onClick={@onHeaderCellClick}
          index={index}
          sort_order={sort_order}
          title={column.title}/>
      )

    return cells

  render: ->
    <tr className={this.props.className}>
      {this.build_cells()}
    </tr>


export default TableHeaderRow
