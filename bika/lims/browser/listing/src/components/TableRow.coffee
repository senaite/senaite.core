import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"


class TableRow extends React.Component
  ###
   * The table row component renders a single row with cells
  ###

  constructor: (props) ->
    super(props)

  is_selected: (item) ->
    ###
     * Check if the current row is selected
    ###
    uid = item.uid
    selected_uids = @props.selected_uids or []
    return uid in selected_uids

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

    if @is_child_row item
      cls += " child"

    if @is_parent_row item
      cls += " parent"

    return cls

  is_parent_row: (item) ->
    ###
     * Checks if the folderitem contains children
    ###

    # only parent items have the children key set
    return "children" of item

  is_child_row: (item) ->
    ###
     * Checks if the folderitem is a child
    ###

    # only child items have the primary_uid key set
    primary_uid = item.primary_uid or ""
    if primary_uid.length == 0
      return no
    return yes

  is_orphan_row: (item) ->
    ###
     * Check if the item
    ###

    # only child rows can be orphan
    if not @is_child_row item
      return no

    # get the parent UID
    primary_uid = item.primary_uid

    # check if the parent is contained in the current folderitems
    return primary_uid not of @props.folderitems_by_uid

  build_row: ->
    ###
     * Build the Table row and eventual child-rows
    ###
    row = []

    # The folderitem
    item = @props.item
    uid = item.uid
    children = item.children or []
    orphaned = no

    if @is_child_row item
      # no need to render this child item, because the parent will do it
      if not @is_orphan_row item
        return null

    # Handle row
    row.push(
      <tr key={uid}
          className={@get_row_css_class(item)}>
        {@build_cells(item)}
      </tr>
    )

    # Handle child rows
    for child in children
      child_uid = child.uid
      row.push(
        <tr key={child_uid}
            className={@get_row_css_class(child)}>
          {@build_cells(child)}
        </tr>
      )

    return row

  build_cells: (item) ->
    ###
     * Build all cells for the row
    ###

    cells = []

    checkbox_name = "#{@props.select_checkbox_name}:list"
    uid = item.uid
    selected = @is_selected item

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
          {@is_parent_row(item) and
           <div title={@props.parent_row_title}>
             <span className="glyphicon glyphicon-chevron-down"></span>
           </div>
          }
          {@is_child_row(item) and
           <div title={@props.child_row_title}>
             <div className="text-muted small">{@props.child_row_title}</div>
           </div>
          }
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
    @build_row()


export default TableRow
