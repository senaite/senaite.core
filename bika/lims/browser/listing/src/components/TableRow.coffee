import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"


class TableRow extends React.Component
  ###
   * The table row component renders a single row with cells
  ###

  constructor: (props) ->
    super(props)

  is_selected: ->
    ###
     * Check if the current row is selected
    ###
    uid = @props.item.uid
    selected_uids = @props.selected_uids or []
    return uid in selected_uids

  get_row_css_class: ->
    ###
     * Calculate the row CSS class
    ###
    cls = @props.className

    # Add CSS class when the row is selected
    if @is_selected()
      cls += " info"

    return cls

  build_cells: ->
    ###
     * Build all cells for the row
    ###

    cells = []

    item = @props.item
    checkbox_name = "#{@props.select_checkbox_name}:list"
    uid = item.uid
    selected = @is_selected()

    # insert select column
    if @props.show_select_column
      cells.push(
        <td key={item.uid}>
          <Checkbox
            name={checkbox_name}
            value={uid}
            checked={selected}
            onChange={@props.on_select_checkbox_checked}/>
        </td>
    )

    # insert visible columns in the right order
    for key in @props.column_order

      # get the column
      column = @props.columns[key]

      # skip hidden
      if not column.toggle
        continue

      # get either the replacement html or the plain value of the item
      title = item.replace[key] or item[key]

      cells.push(
        <TableCell
          key={key}
          item={item}
          item_key={key}
          selected={selected}
          html={title}/>
      )
    return cells

  render: ->
    <tr className={@get_row_css_class()}>
      {@build_cells()}
    </tr>


export default TableRow
