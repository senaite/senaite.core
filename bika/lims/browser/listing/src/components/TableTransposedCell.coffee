import React from "react"

import Checkbox from "./Checkbox.coffee"
import TableCell from "./TableCell.coffee"
import RemarksField from "./RemarksField.coffee"

###*
 * This component is currently only used for the Transposed Layout in Worksheets
###
class TableTransposedCell extends TableCell

  ###*
   * Get the transposed folderitem
   *
   * also see bika.lims.browser.worksheet.views.analyses_transposed.py
   *
   * The "transposed item" is the original folderitem, which is stored below the
   * `column_key` of the transposed column, e.g.
   *
   * columns: {1: {…}, 2: {…}, column_key: {…}}
   * folderitems: [
   *   {1: {original-folderitem}, 2: {original-folderitem}, item_key: "Pos", column_key: "Positions"},
   *   {1: {original-folderitem}, 2: {original-folderitem}, item_key: "Result", column_key: "Calcium"},
   *   {1: {original-folderitem}, 2: {original-folderitem}, item_key: "Result", column_key: "Magnesiumn"},
   * ]
  ###
  get_item: ->
    # @props.item: transposed folderitem (see TableCells.coffee)
    # @props.column_key: current column key rendered, e.g. "1", "2", "column_key"
    return @props.item[@props.column_key]

  ###*
   * Get the value within the transposed folderitem to render
   *
   * also see bika.lims.browser.worksheet.views.analyses_transposed.py
   *
   * The `item_key` (see also above) within a transposed folderitems item,
   * points to the value to be rendered from the original folderitem.
   *
  ###
  get_column_key: ->
    # @props.item is a transposed folderitem
    # @props.column_key is the actual column key rendered, e.g. "1", "2", "column_key"
    return @props.item.item_key or @props.item.column_key

  ###*
   * Calculate CSS Class for the <td> cell based on the original folderitem
  ###
  get_css: ->
    item = @get_item()
    css = ["transposed", @props.className]
    if @is_result_column()
      css.push "result"
    if not item
      css.push "empty"
    else
      css.push item.state_class
      if item.uid in @props.selected_uids
        css.push "info"
    return css.join " "

  get_remarks_columns: ->
    columns = []
    for key, value of @props.columns
      if value.type == "remarks"
        columns.push key
    return columns

  ###*
   * Creates a select checkbox for the original folderitem
   * @param props {object} properties passed to the component
   * @returns ReadonlyField component
  ###
  create_select_checkbox: ({props}={}) ->
    props ?= {}
    uid = @get_uid()
    name = "#{@props.select_checkbox_name}:list"
    disabled = @is_disabled()
    selected = @is_selected()
    return (
      <div key="select" className="checkbox">
        <Checkbox
          name={name}
          value={uid}
          disabled={disabled}
          checked={selected}
          onChange={@props.on_select_checkbox_checked}
          {...props}
          />
      </div>)

  ###*
   * Creates all interim fields
   * @param props {object} properties passed to the component
   * @returns Interim Fields
  ###
  create_interim_fields: ({props}={}) ->
    props ?= {}
    uid = @get_uid()
    item = @get_item()
    fields = []
    interims = item.interimfields or []
    # [{value: 10, keyword: "F_cl", formatted_value: "10,0", unit: "mg/mL", title: "Faktor cl"}, ...]
    for interim, index in interims
      # get the keyword of the interim field
      keyword = interim.keyword
      # skip interims which are not listed in the columns
      # -> see: bika.lims.browser.analyses.view.folderitems
      continue unless @props.columns.hasOwnProperty keyword
      # get the unit of the interim
      unit = interim.unit or ""
      # prepare the field properties
      props =
        key: keyword
        column_key: keyword
        name: "#{keyword}.#{uid}"
        defaultValue: interim.value
        placeholder: interim.title or keyword
        formatted_value: interim.formatted_value
        after: "<span class='unit'>#{unit}</span>"

      if @is_edit_allowed()
        # add a numeric field per interim
        fields = fields.concat @create_numeric_field props: props
      else
        # add a readonly field per interim
        fields = fields.concat @create_readonly_field props: props

    return fields

  ###*
   * Render the fields for a single transposed cell
  ###
  render_content: ->
    # the current rendered column ID
    column_key = @get_column_key()
    # single folderitem
    item = @get_item()
    # return if there is no item
    if not item
      console.debug "Skipping empty item for '#{column_key}' in column '#{@props.column_key}'"
      return null
    # the UID of the original folderitem
    uid = @get_uid()
    # field type to render
    type = @get_type()

    # the fields to return
    fields = []

    if @is_result_column()
      # render the select checkbox and the remarks toggle in the before box
      before_components = []
      # Add a select checkbox for result cells
      before_components = before_components.concat @create_select_checkbox()
      # Append remarks toggle
      before_components.push(
        <a key={uid + "_remarks"}
           href="#"
           className="transposed_remarks"
           uid={uid}
           onClick={@props.on_remarks_expand_click}>
          <span className="remarksicon glyphicon glyphicon-comment"></span>
        </a>)
      item["before_components"] = before_components

    if type == "readonly"
      fields = fields.concat @create_readonly_field()
    else if type == "calculated"
      # prepend interim fields
      fields = fields.concat @create_interim_fields()
      # add the calculated results field
      fields = fields.concat @create_readonly_field()
    # The "transposed" type is defined in the column definition, see analyses_transposed.py
    # -> full folderitem is located below the column key in this item
    else if type == "transposed"
      # insert all visible interims first
      fields = fields.concat @create_interim_fields()
      # calculated field
      if item.calculation
        fields = fields.concat @create_readonly_field()
      # select
      else if column_key of @get_choices()
        fields = fields.concat @create_select_field()
      # numeric
      else
        fields = fields.concat @create_numeric_field()

    if @is_result_column()
      # Append Remarks field(s)
      for column_key, column_index in @get_remarks_columns()
        value = item[column_key]
        fields.push(
          <div key={column_index + "_remarks"}>
            <RemarksField
              {...@props}
              uid={uid}
              item={item}
              column_key={column_key}
              value={item[column_key]}
            />
          </div>)

      # Append Attachments
      if item.replace.Attachments
        fields = fields.concat @create_readonly_field
            props:
              key: column_index + "_attachments"
              uid: uid
              item: item
              column_key: "Attachments"
              formatted_value: item.replace.Attachments
              attrs:
                style: {display: "block"}

    return fields

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
