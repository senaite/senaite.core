import React from "react"
import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"
import TableTransposedCell from "./TableTransposedCell.coffee"


class TableCells extends React.Component

  constructor: (props) ->
    super(props)
    @on_remarks_expand_click = @on_remarks_expand_click.bind @

  on_remarks_expand_click: (event) ->
    event.preventDefault()
    el = event.currentTarget
    uid = el.getAttribute "uid"

    # notify parent event handler with the extracted uid
    if @props.on_remarks_expand_click
      @props.on_remarks_expand_click uid

  get_column: (column_key) ->
    return @props.columns[column_key]

  get_table_columns: ->
    return @props.table_columns or []

  get_colspan: (column_key, item) ->
    colspan = item.colspan or {}
    return colspan[column_key]

  get_rowspan: (column_key, item) ->
    rowspan = item.rowspan or {}
    return rowspan[column_key]

  skip_cell_rendering: (column_key, item) ->
    skip = item.skip or []
    return column_key in skip

  show_select: (item) ->
    if typeof item.show_select == "boolean"
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
    remarks = @props.remarks  # True if this row follows a remarks row

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

          {remarks and
          <a uid={uid}
             href="#"
             className="remarks"
             onClick={@on_remarks_expand_click}>
            <span className="remarksicon glyphicon glyphicon-comment"></span>
          </a>}
        </td>)

    # insert visible columns in the right order
    for column_key, column_index in @get_table_columns()

      # Skip single cell rendering to support rowspans
      if @skip_cell_rendering column_key, item
        continue

      # get the column definition from the listing view
      column = @get_column column_key
      colspan = @get_colspan column_key, item
      rowspan = @get_rowspan column_key, item

      css = "contentcell #{column_key}"

      # Transposed cell items contain an object key "key", which points to the
      # transposed folderitem requested.
      #
      # E.g. a transposed worksheet would have the positions (1, 2, 3, ...) as
      # columns and the contained services of each position as rows.
      # {"key": "1", "1": {"Service": "Calcium", ...}}
      # The column for "1" would then contain the type "transposed".
      if column.type == "transposed"
        # Transposed Cell
        cells.push(
          <TableTransposedCell
            {...@props}
            key={column_index}
            item={item}
            column_key={column_key}
            column={column}
            expanded={expanded}
            selected={selected}
            disabled={disabled}
            colspan={colspan}
            rowspan={rowspan}
            on_remarks_expand_click={@on_remarks_expand_click}
            className={css}
            />)
      else
        # Regular Cell
        cells.push(
          <TableCell
            {...@props}
            key={column_key}
            item={item}
            column_key={column_key}
            column={column}
            expanded={expanded}
            selected={selected}
            disabled={disabled}
            colspan={colspan}
            rowspan={rowspan}
            className={css}
            />)

    return cells

  render: ->
    return @build_cells()


export default TableCells
