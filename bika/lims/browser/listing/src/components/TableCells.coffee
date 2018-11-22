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

  get_colspan: (item_key, item) ->
    colspan = item.colspan or {}
    return colspan[item_key]

  get_rowspan: (item_key, item) ->
    rowspan = item.rowspan or {}
    return rowspan[item_key]

  skip_cell_rendering: (item_key, item) ->
    # return yes unless item_key of item
    skip = item.skip or []
    return item_key in skip

  show_select: (item) ->
    if "show_select" of item
      return item.show_select
    return @props.show_select_column

  build_cells: ->
    cells = []

    item = @props.item
    uid = item.uid
    checkbox_name = "#{@props.select_checkbox_name}:list"
    show_select = @show_select item

    expanded = @props.expanded
    selected = @props.selected
    disabled = @props.disabled

    # insert select column
    if show_select
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

      # Skip single cell rendering to support rowspans
      if @skip_cell_rendering key, item
        continue

      # get the column definition from the listing view
      column = @get_column key
      colspan = @get_colspan key, item
      rowspan = @get_rowspan key, item

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
          colspan={colspan}
          rowspan={rowspan}
          />)

    return cells

  render: ->
    return @build_cells()


export default TableCells
