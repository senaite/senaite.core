import React from "react"

import Checkbox from "./Checkbox.coffee"
import HiddenField from "./HiddenField.coffee"
import MultiSelect from "./MultiSelect.coffee"
import NumericField from "./NumericField.coffee"
import ReadonlyField from "./ReadonlyField.coffee"
import Select from "./Select.coffee"
import StringField from "./StringField.coffee"


class TableCell extends React.Component

  constructor: (props) ->
    super(props)

    # Bind checkbox field events
    @on_checkbox_field_change = @on_checkbox_field_change.bind @

    # Bind select field events
    @on_select_field_blur = @on_select_field_blur.bind @
    @on_select_field_change = @on_select_field_change.bind @

    # Bind multiselect field events
    @on_multiselect_field_blur = @on_multiselect_field_blur.bind @
    @on_multiselect_field_change = @on_multiselect_field_change.bind @

    # Bind numeric field events
    @on_numeric_field_blur = @on_numeric_field_blur.bind @
    @on_numeric_field_change = @on_numeric_field_change.bind @

    # Bind string field events
    @on_string_field_blur = @on_string_field_blur.bind @
    @on_string_field_change = @on_string_field_change.bind @

  on_checkbox_field_change: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.checked
    console.debug "TableCell:on_checkbox_field_change: checked=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @get_item()

    # Call the *save* field handler (no blur event here necessary)
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @get_item()

  on_select_field_blur: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.value
    console.debug "TableCell:on_select_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @get_item()

  on_select_field_change: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.value
    console.debug "TableCell:on_select_field_change: value=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @get_item()

  on_multiselect_field_blur: (event) ->
    el = event.currentTarget
    ul = el.parentNode.parentNode
    checked = ul.querySelectorAll("input[type='checkbox']:checked")
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = (input.value for input in checked)
    console.debug "TableCell:on_multiselect_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @get_item()

  on_multiselect_field_change: (event) ->
    el = event.currentTarget
    ul = el.parentNode.parentNode
    checked = ul.querySelectorAll("input[type='checkbox']:checked")
    uid = el.getAttribute("uid")
    value = (input.value for input in checked)
    name = el.getAttribute("column_key") or el.name
    console.debug "TableCell:on_multiselect_field_change: value=#{value}"

    # Call the *on_blur* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @get_item()

  on_numeric_field_blur: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.value
    console.debug "TableCell:on_numeric_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @get_item()

  on_numeric_field_change: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.value
    console.debug "TableCell:on_numeric_field_change: value=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @get_item()

  on_string_field_blur: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.value
    console.debug "TableCell:on_string_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @get_item()

  on_string_field_change: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.value
    console.debug "TableCell:on_string_field_change: value=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @get_item()

  render_before_content: ->
    before = @get_item().before
    column_key = @get_column_key()
    if column_key not of before
      return null
    return <span className="before-item"
                 dangerouslySetInnerHTML={{__html: before[column_key]}}>
           </span>

  render_after_content: ->
    after = @get_item().after
    column_key = @get_column_key()
    if column_key not of after
      return null
    return <span className="after-item"
                 dangerouslySetInnerHTML={{__html: after[column_key]}}>
           </span>

  is_edit_allowed: (column_key, item) ->
    # the global allow_edit overrides all row specific settings
    if not @props.allow_edit
      return no

    # check if the field is listed in the item's allow_edit list
    if column_key in item.allow_edit
      return yes

    return no

  is_disabled: (column_key, item) ->
    return item.disabled or no

  is_required: (column_key, item) ->
    required_fields = item.required or []
    required = column_key in required_fields
    # make the field conditionally required if the row is selected
    selected = @props.selected
    return required and selected

  get_item: ->
    return @props.item

  get_column_key: ->
    return @props.column_key

  get_name: (column_key, item) ->
    return "#{column_key}.#{item.uid}"

  get_value: (column_key, item) ->
    value = item[column_key]

    # check if the field is an interim
    interims = item.interimfields or []
    for interim in interims
      if interim.keyword == column_key
        value = interim.value
        break

    return value

  is_result_field: (column_key, item) ->
    return column_key == "Result"

  get_formatted_value: (column_key, item) ->
    # replacement html or plain value of the current column
    formatted_value = item.replace[column_key] or @get_value column_key, item

    # use the formatted result
    if column_key == "Result"
      formatted_value = item.formatted_result or formatted_value

    return formatted_value

  get_type: (column_key, item) ->
    # true if the field is editable
    editable = @is_edit_allowed column_key, item
    resultfield = @is_result_field column_key, item

    # readonly field
    if not editable
      return "readonly"

    # type definition of the column has precedence
    column = @props.column or {}
    if "type" of column
      return column["type"]

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
    # the current rendered column cell name
    column_key = @get_column_key()
    # single folderitem
    item = @get_item()
    # return if there is no item
    if not item
      console.warn "Skipping cell rendering for column '#{column_key}'"
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
        {@render_before_content()}
        {@render_content()}
        {@render_after_content()}
      </div>
    </td>


export default TableCell
