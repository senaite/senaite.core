import React from "react"

import Checkbox from "./Checkbox.coffee"
import HiddenField from "./HiddenField.coffee"
import MultiSelect from "./MultiSelect.coffee"
import NumericField from "./NumericField.coffee"
import ReadonlyField from "./ReadonlyField.coffee"
import Select from "./Select.coffee"
import StringField from "./StringField.coffee"
import TableCell from "./TableCell.coffee"


class TableTransposedCell extends TableCell

  constructor: (props) ->
    super(props)

  get_transposed_item: ->
    # The transposed item is the original folder item,
    # stored below the key of the current column (column_key)
    return @props.item[@props.column_key]

  get_transposed_key: ->
    # The transposed key points to a key inside the transposed item
    return @props.item.item_key or @props.column_key

  get_type: (column_key, item) ->
    # true if the field is editable
    editable = @is_edit_allowed column_key, item
    resultfield = @is_result_field column_key, item

    # readonly field
    if not editable
      return "readonly"

    # check if the field is a boolean
    value = @get_value column_key, item
    if typeof(value) == "boolean"
      return "boolean"

    # check if the field is listed in choices
    choices = item.choices or {}
    if column_key of choices
      return "select"

    # check if the field is an interim
    interims = item.interimfields or []
    if interims.length > 0
      interim_keys = item.interimfields.map (interim) ->
        return interim.keyword
      if column_key in interim_keys
        return "interim"

    # check if the field is a calculated field
    if resultfield and item.calculation
      return "calculated"

    # the default
    return "numeric"

  render_content: ->
    # transposed item key
    column_key = @get_transposed_key()
    # transposed item
    item = @get_transposed_item()
    # skip empty folderitems
    if not item
      return null
    # the current column definition
    column = @props.column
    # the UID of the current item
    uid = item.uid
    # form field title
    title = column.title or column_key
    # form field name
    name = @get_name column_key, item
    # form field value
    value = @get_value column_key, item
    # formatted display value of the form field
    formatted_value = @get_formatted_value column_key, item
    # true if the holding row is selected
    selected = @props.selected
    # true if the field should be disabled
    disabled = @is_disabled column_key, item
    # true if the field is required
    required = @is_required column_key, item
    # field type to render
    type = @get_type column_key, item
    # interim fields
    interims = item.interimfields or []
    # result field
    result_field = @is_result_field column_key, item
    # input field css class
    field_css_class = "form-control input-sm"
    if required then field_css_class += " required"

    # the field to return
    field = []

    # render readonly field
    if type == "readonly"
      field.push (
        <ReadonlyField
          key={name}
          uid={uid}
          name={name}
          value={value}
          title={title}
          formatted_value={formatted_value}
          />)

    # render calculated field
    else if type == "calculated"
      fieldname = "#{name}:records"
      field.push (
        <ReadonlyField
          key={name}
          uid={uid}
          name={fieldname}
          value={value}
          title={title}
          formatted_value={formatted_value}
          />)
      field.push (
        <HiddenField
          key={name + "_hidden"}
          uid={uid}
          name={fieldname}
          value={value}
          title={title}
          />)

    # render interim field
    else if type == "interim"
      fieldname = "#{name}:records"
      field.push (
        <NumericField
          key={name}
          uid={uid}
          name={fieldname}
          defaultValue={value}
          column_key={column_key}
          title={title}
          formatted_value={formatted_value}
          placeholder={title}
          disabled={disabled}
          onChange={@on_numeric_field_change}
          onBlur={@on_numeric_field_blur}
          className={field_css_class}
          />)
      # XXX Fake in interims for browser.analyses.workflow.workflow_action_submit
      if interims.length > 0
        item_data = {}
        item_data[item.uid] = interims
        field.push (
          <HiddenField
            key={name + "_item_data"}
            uid={uid}
            name="item_data"
            value={JSON.stringify item_data}
            />)

    # render select field
    else if type in ["select", "choices"]
      fieldname = "#{name}:records"
      options = item.choices[column_key]
      field.push (
        <Select
          key={name}
          uid={uid}
          name={fieldname}
          defaultValue={value}
          column_key={column_key}
          title={title}
          disabled={disabled}
          selected={selected}
          required={required}
          options={options}
          onChange={@on_select_field_change}
          onBlur={@on_select_field_blur}
          className={field_css_class}
          />)

    # render multiselect field
    else if type in ["multiselect", "multichoices"]
      # This gives a dictionary of UID -> UID list of selected items
      fieldname = "#{name}:record:list"
      options = item.choices[column_key]
      field.push (
        <MultiSelect
          key={name}
          uid={uid}
          name={fieldname}
          defaultValue={value}
          column_key={column_key}
          title={title}
          disabled={disabled}
          selected={selected}
          required={required}
          options={options}
          onChange={@on_multiselect_field_change}
          onBlur={@on_multiselect_field_blur}
          className={field_css_class}
          />)

    # render checkbox field
    else if type == "boolean"
      fieldname = "#{name}:record:ignore-empty"
      field.push (
        <Checkbox
          key={name}
          uid={uid}
          name={fieldname}
          value="on"
          column_key={column_key}
          title={title}
          defaultChecked={value}
          disabled={disabled}
          onChange={@on_checkbox_field_change}
          />)

    # render numeric field
    else if type == "numeric"
      fieldname = "#{name}:records"
      field.push (
        <NumericField
          key={name}
          uid={uid}
          name={fieldname}
          defaultValue={value}
          column_key={column_key}
          title={title}
          formatted_value={formatted_value}
          placeholder={title}
          disabled={disabled}
          selected={selected}
          required={required}
          onChange={@on_numeric_field_change}
          onBlur={@on_numeric_field_blur}
          className={field_css_class}
          />)

    # N.B. Disabled fields are not send on form submit.
    #      Therefore, we render a hidden field when disabled.
    if disabled
      field.push (
        <HiddenField
          key={name + "_hidden"}
          uid={uid}
          name={fieldname}
          value={value}
          column_key={column_key}
          />)

    return field

  render: ->
    <td className={@props.className}
        colSpan={@props.colspan}
        rowSpan={@props.rowspan}>
      <div className="form-group">
        {@render_content()}
      </div>
    </td>

export default TableTransposedCell
