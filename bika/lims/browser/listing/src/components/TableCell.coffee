import React from "react"

import Select from "./Select.coffee"
import NumericField from "./NumericField.coffee"
import Checkbox from "./Checkbox.coffee"
import StringField from "./StringField.coffee"
import ReadonlyField from "./ReadonlyField.coffee"
import HiddenField from "./HiddenField.coffee"


class TableCell extends React.Component
  ###
   * The table cell component renders a single cell
  ###

  constructor: (props) ->
    super(props)

    # bind context of event handlers
    @on_cell_select_field_change = @on_cell_select_field_change.bind @
    @on_cell_checkbox_field_change = @on_cell_checkbox_field_change.bind @
    @on_cell_numeric_field_change = @on_cell_numeric_field_change.bind @
    @on_cell_string_field_change = @on_cell_string_field_change.bind @

  on_cell_select_field_change: (event) ->
    ###
     * Event handler when the select field changed
    ###
    el = event.currentTarget
    name = el.name
    value = el.value
    console.debug "TableCell:on_cell_select_field_change: value=#{value}"

    if @props.on_editable_field_change
      @props.on_editable_field_change @props.item.uid, name, value

  on_cell_checkbox_field_change: (event) ->
    ###
     * Event handler when the checkbox field changed
    ###
    el = event.currentTarget
    name = el.name
    value = el.checked
    console.debug "TableCell:on_cell_checkbox_field_change: checked=#{value}"

    if @props.on_editable_field_change
      @props.on_editable_field_change @props.item.uid, name, value

  on_cell_numeric_field_change: (event) ->
    ###
     * Event handler when the numeric field changed
    ###
    el = event.currentTarget
    name = el.name
    value = el.value
    console.debug "TableCell:on_cell_numeric_field_change: value=#{value}"

    if @props.on_editable_field_change
      @props.on_editable_field_change @props.item.uid, name, value

  on_cell_string_field_change: (event) ->
    ###
     * Event handler when the string field changed
    ###
    el = event.currentTarget
    name = el.name
    value = el.value
    console.debug "TableCell:on_cell_string_field_change: value=#{value}"

    if @props.on_editable_field_change
      @props.on_editable_field_change @props.item.uid, name, value

  render_before_content: ->
    ###
     * Render additional content *before* the cell title
    ###
    before = @props.item.before
    item_key = @props.item_key
    if @props.item_key not of before
      return null
    return <span className="before-item"
                 dangerouslySetInnerHTML={{__html: before[item_key]}}>
           </span>

  render_after_content: ->
    ###
     * Render additional content *after* the cell title
    ###
    after = @props.item.after
    item_key = @props.item_key
    if item_key not of after
      return null
    return <span className="after-item"
                 dangerouslySetInnerHTML={{__html: after[item_key]}}>
           </span>

  is_edit_allowed: ->
    ###
     * Checks if the field key is listed in the `allow_edit` list
    ###
    item = @props.item
    item_key = @props.item_key
    allow_edit = @props.allow_edit
    selected = @props.selected

    # the global allow_edit overrides all row specific settings
    if not allow_edit
      return no

    # calculated field
    if (item_key == "Result") and item.calculation
      return no

    # check if the field is listed in the item's allow_edit list
    if item_key in item.allow_edit
      return yes

    return no

  render_content: ->
    ###
      * Render the table cell content
    ###

    item = @props.item
    item_key = @props.item_key
    name = @props.name
    value = @props.value
    formatted_value = @props.formatted_value
    title = @props.title
    choices = item.choices or {}
    readonly = @props.readonly
    column_title = @props.column.title
    editable = @is_edit_allowed()
    required_fields = item.required or []
    required = item_key in required_fields

    # Render readonly fields
    if not editable
      field = [
        <ReadonlyField
          key={name}
          name={name}
          value={value}
          title={column_title}
          formatted_value={formatted_value}
          className="readonly"
          />
      ]
      return field

    # Select
    if item_key of choices
      fieldname = "#{name}:records"
      options = choices[item_key]
      field = [
        <Select
          key={name}
          name={fieldname}
          defaultValue={value}
          title={column_title}
          disabled={readonly}
          required={required}
          options={options}
          onChange={@on_cell_select_field_change}
          className="form-control input-sm"
          />
      ]
      if readonly
        field.push (
          <HiddenField
            key={name + "_hidden"}
            name={fieldname}
            value={value}
            className=""
          />
        )
      return field

    # Checkbox
    if typeof(value) == "boolean"
      fieldname = "#{name}:record:ignore-empty"
      field = [
        <Checkbox
          key={name}
          name={fieldname}
          value="on"
          title={column_title}
          defaultChecked={value}
          disabled={readonly}
          editable={editable}
          onChange={@on_cell_checkbox_field_change}
          className=""
          />
      ]
      if readonly
        field.push (
          <HiddenField
            key={name + "_hidden"}
            name={fieldname}
            value={value}
            className=""
          />
        )
      return field

    # Numeric
    if typeof(value) == "string"
      fieldname = "#{name}:records"
      field = [
        <NumericField
          key={name}
          name={fieldname}
          defaultValue={value}
          editable={editable}
          title={column_title}
          formatted_value={formatted_value}
          placeholder={column_title}
          disabled={readonly}
          onChange={@on_cell_numeric_field_change}
          className="form-control input-sm"
          />
      ]
      if readonly
        field.push (
          <HiddenField
            key={name + "_hidden"}
            name={fieldname}
            value={value}
            className=""
          />
        )
      return field

  render: ->
    <td className={@props.className}>
      <div className="form-group">
        {@render_before_content()}
        {@render_content()}
        {@render_after_content()}
      </div>
    </td>


export default TableCell
