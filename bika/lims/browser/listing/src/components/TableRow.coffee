import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"
import TableRemarksRow from "./TableRemarksRow.coffee"


class TableRow extends React.Component
  ###
   * The table row component renders a single row with cells
  ###

  constructor: (props) ->
    super(props)

    # bind event handler to local context
    @on_row_click = @on_row_click.bind @

  on_row_click: (event) ->
    ###
     * Event handler when the row was clicked
    ###
    el = event.currentTarget
    uid = el.getAttribute "uid"
    console.debug "TableRow::on_row_click: UID #{uid} clicked"

    if @props.on_row_click then @props.on_row_click uid

  is_selected: (item) ->
    ###
     * Check if the current row is selected
    ###
    uid = item.uid
    selected_uids = @props.selected_uids or []
    return uid in selected_uids

  is_expanded: (item) ->
    ###
     * Check if the row is expanded
    ###
    expanded = @props.expanded_rows or []
    return item.uid in expanded

  has_children: (item) ->
    ###
     * Check if the current row is selected
    ###
    children = item.children or []
    if children.length == 0
      return no
    return yes

  is_child_row: (item) ->
    ###
     * Checks if the item is a child row
    ###
    return yes if item.parent or no

  get_row_css_class: (item) ->
    ###
     * Calculate the row CSS class
    ###
    cls = @props.className

    # Add table row class
    if item.table_row_class
      cls += " #{item.table_row_class}"

    # Add CSS class when the row is selected
    if @is_selected item
      cls += " info"

    return cls

  build_rows: ->
    ###
     * Build the Table row and eventual child-rows
    ###
    rows = []

    # The folderitem
    item = @props.item
    uid = item.uid
    row_cls = @get_row_css_class item
    expanded = @is_expanded item
    has_children = @has_children item
    children = @props.children[uid] or []

    # Handle parent row
    rows.push(
      <tr key={uid}
          className={row_cls}>
        {@build_cells(item)}
      </tr>
      <TableRemarksRow
        className={row_cls}
        key={uid + "_remarks"}
        {...@props}
        item={item}
        />
    )

    # return the parent row if there are no children
    if not has_children
      return rows

    # calculate the CSS class for expanded
    if expanded
      icon_cls = "glyphicon glyphicon-chevron-down"
    else
      icon_cls = "glyphicon glyphicon-chevron-up"

    default_toggle_row_title = if expanded then "Collapse" else "Expand"

    # Insert a expand row
    rows.push(
      <tr key={uid + "_toggle_children"}
          uid={uid}
          onClick={@on_row_click}
          className={row_cls + " togglerow"}>
        <td colSpan={@props.column_count}>
          <span className={icon_cls}></span> {@props.toggle_row_title or default_toggle_row_title}
        </td>
      </tr>
    )

    if expanded
      for child in children
        child_uid = child.uid
        child_cls = @get_row_css_class child
        # Handle child row
        rows.push(
          <tr key={child_uid}
              uid={child_uid}
              className={child_cls + " childrow"}>
            {@build_cells(child)}
          </tr>
        )

    return rows

  build_cells: (item) ->
    ###
     * Build all cells for the row
    ###

    cells = []

    checkbox_name = "#{@props.select_checkbox_name}:list"
    uid = item.uid
    selected = @is_selected item
    expanded = @is_expanded item

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
    for key in @props.table_columns

      # get the column
      column = @props.columns[key]

      # form field name
      name = "#{key}.#{uid}"
      # form field value
      value = item[key]
      # replacement html or plain value of the current column
      formatted_value = item.replace[key] or value

      # use the formatted result
      if key == "Result"
        formatted_value = item.formatted_result or formatted_value

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
          className={key}  # set the column key as the CSS class name
          />
      )

    return cells

  render: ->
    @build_rows()


export default TableRow
