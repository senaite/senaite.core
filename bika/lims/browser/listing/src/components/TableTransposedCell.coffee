import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"

###*
 * This component is currently only used for the Transposed Layout in Worksheets
###
class TableTransposedCell extends TableCell

  ###*
   * Get the transposed folderitem
   *
   * also see bika.lims.browser.worksheet.views.analyses_transposed.py
   *
   * The transposed `item` is the original folderitem, which is stored below the
   * `column_key` of the transposed column, e.g.
   *
   * `{"1": {"uid": ..., }, "2": {"uid": ..., }}`
  ###

  get_item: ->
    return @props.item[@props.column_key]

  get_column_key: ->
    # The `item_key` points to a key inside the transposed folderitem
    return @props.item.item_key or @props.item.column_key

  get_css: ->
    if @is_result_column()
      item = @get_item()
      state_class = if item then item.state_class
      return "result #{state_class}"
    return @props.className

  render_content: ->
    # the current rendered column cell name
    column_key = @get_column_key()
    # single folderitem
    item = @get_item()
    # return if there is no item
    if not item
      console.warn "Skipping cell rendering for column '#{column_key}'"
      return null
    # the UID of the transposed folderitem
    uid = @get_uid()
    # field type to render
    type = @get_type()
    # interims
    interims = @get_interimfields()
    # the field to return
    field = []

    # Always prepend a select checkbox before the results cell
    if column_key == "Result"
      field.push (
        <div key="select" className="checkbox input-sm">
          <Checkbox
            name={"#{@props.select_checkbox_name}:list"}
            value={uid}
            disabled={@is_disabled()}
            checked={@is_selected()}
            onChange={@props.on_select_checkbox_checked}
            />
        </div>)

    if type == "readonly"
      # Render the results field + all interim fields
      if column_key == "Result"
        field = field.concat @create_readonly_field
          props:
            after: " #{item.Unit}"
      else
        field = field.concat @create_readonly_field()
    else if type == "transposed"
      if column_key of @get_choices()
        field = field.concat @create_select_field()
      else
        # Render the results field + all interim fields
        if column_key == "Result"
          # render editable interim fields first
          for interim, index in @get_interimfields()
            # {value: 10, keyword: "F_cl", formatted_value: "10,0", unit: "mg/mL", title: "Faktor cl"}
            field = field.concat @create_numeric_field
              props:
                key: interim.keyword
                column_key: interim.keyword
                name: "#{interim.keyword}.#{uid}"
                defaultValue: interim.value
                placeholder: interim.title
                formatted_value: interim.formatted_value
          if item.calculation
            field = field.concat @create_readonly_field()
          else
            field = field.concat @create_numeric_field()

    return field

  render: ->
    <td className={@get_css()}
        colSpan={@props.colspan}
        rowSpan={@props.rowspan}>
      <div className="form-group">
        {@render_before_content()}
        {@render_content()}
        {@render_after_content()}
      </div>
    </td>

export default TableTransposedCell
