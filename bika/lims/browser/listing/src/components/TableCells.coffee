import React from "react"
import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"


class TableCells extends React.Component

  constructor: (props) ->
    super(props)

  get_column: (key) ->
    return @props.columns[key]

  get_table_columns: ->
    return @props.table_columns or []

  build_cells: ->
    cells = []

    item = @props.item
    uid = item.uid
    checkbox_name = "#{@props.select_checkbox_name}:list"

    expanded = @props.expanded
    selected = @props.selected
    disabled = @props.disabled

    # insert select column
    if @props.show_select_column
      cells.push(
        <td key={uid}>
          <Checkbox
            name={checkbox_name}
            value={uid}
            disabled={disabled}
            checked={selected}
            onChange={@props.on_select_checkbox_checked}/>
        </td>)

    # insert visible columns in the right order
    for key in @get_table_columns()

      # get the column definition from the listing view
      column = @get_column key

      cells.push(
        <TableCell
          {...@props}
          key={key}
          item={item}
          item_key={key}
          column={column}
          expanded={expanded}
          selected={selected}
          disabled={disabled}
          />)

    return cells

  render: ->
    return @build_cells()


export default TableCells
