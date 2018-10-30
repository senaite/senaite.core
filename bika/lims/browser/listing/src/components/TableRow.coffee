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

    # XXX Refactor this!
    # A JSON structure coming from bika.lims.analysisrequest.manage_analyses to
    # determine if the row can be selected or not
    row_data = item.row_data or "{}"
    row_data = JSON.parse row_data
    disabled = row_data.disabled

    # global allow_edit
    allow_edit = @props.allow_edit

    # insert select column
    if @props.show_select_column
      cells.push(
        <td key={item.uid}>
          <Checkbox
            name={checkbox_name}
            value={uid}
            disabled={disabled}
            checked={selected}
            allow_edit={allow_edit}
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

      # form field name
      name = "#{key}.#{uid}"
      # form field value
      value = item[key]
      # replacement html or plain value of the current column
      formatted_value = item.replace[key] or value

      cells.push(
        <TableCell
          key={key}  # internal key
          {...@props}  # pass in all properties from the table component
          item={item}  # a single folderitem
          item_key={key}  # the current rendered column key
          name={name}  # the form field name
          value={value}  # the form field value
          formatted_value={formatted_value}  # the formatted value for readonly fields
          selected={selected}  # true if the row is selected
          disabled={disabled}  # true if the fields should be frozen
          allow_edit={allow_edit}  # the global allow_edit flag
          column={column}  # the current rendered column object
          />
      )

    return cells

  render: ->
    <tr className={@get_row_css_class()}>
      {@build_cells()}
    </tr>


export default TableRow
