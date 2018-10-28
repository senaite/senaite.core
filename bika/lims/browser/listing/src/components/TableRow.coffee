import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"


class TableRow extends React.Component
  ###
   * The table row component renders a single row with cells
  ###

  constructor: (props) ->
    super(props)

  get_row_css_class: ->
    ###
     * Calculate the row CSS class
    ###
    cls = @props.className

    # check if the current item UID is in the list selected UIDs
    uid = @props.item.uid
    selected_uids = @props.selected_uids or []

    # add info class if the row is selected
    if uid in selected_uids
      cls += " info"

    return cls

  build_cells: ->
    ###
     * Build all cells for the row
    ###

    cells = []

    item = @props.item
    checkbox_name = "#{@props.select_checkbox_name}:list"
    checkbox_value = item.uid
    checked = item.uid in @props.selected_uids

    # insert select column
    if @props.show_select_column
      cells.push(
        <td key={item.uid}>
          <Checkbox
            name={checkbox_name}
            value={checkbox_value}
            checked={checked}
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
        <TableCell key={key}
                   item={item}
                   item_key={key}
                   className={key}
                   html={title}/>
      )
    return cells

  render: ->
    <tr className={@get_row_css_class()}>
      {@build_cells()}
    </tr>


export default TableRow
