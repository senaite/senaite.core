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

    # Bind checkbox field events
    @on_checkbox_field_change = @on_checkbox_field_change.bind @

    # Bind select field events
    @on_select_field_blur = @on_select_field_blur.bind @
    @on_select_field_change = @on_select_field_change.bind @

    # Bind numeric field events
    @on_numeric_field_blur = @on_numeric_field_blur.bind @
    @on_numeric_field_change = @on_numeric_field_change.bind @

    # Bind string field events
    @on_string_field_blur = @on_string_field_blur.bind @
    @on_string_field_change = @on_string_field_change.bind @

  on_checkbox_field_change: (event) ->
    ###
     * Event handler when the checkbox field changed
    ###
    el = event.currentTarget
    name = el.getAttribute("item_key") or el.name
    value = el.checked
    console.debug "TableCell:on_checkbox_field_change: checked=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field @props.item.uid, name, value, @props.item

    # Call the *save* field handler (no blur event here necessary)
    if @props.save_editable_field
      @props.save_editable_field @props.item.uid, name, value, @props.item

  on_select_field_blur: (event) ->
    ###
     * Event handler when the select field blurred
    ###
    el = event.currentTarget
    name = el.getAttribute("item_key") or el.name
    value = el.value
    console.debug "TableCell:on_select_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field @props.item.uid, name, value, @props.item

  on_select_field_change: (event) ->
    ###
     * Event handler when the select field changed
    ###
    el = event.currentTarget
    name = el.getAttribute("item_key") or el.name
    value = el.value
    console.debug "TableCell:on_select_field_change: value=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field @props.item.uid, name, value, @props.item

  on_numeric_field_blur: (event) ->
    ###
     * Event handler when the numeric field blurred
    ###
    el = event.currentTarget
    name = el.getAttribute("item_key") or el.name
    value = el.value
    console.debug "TableCell:on_numeric_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field @props.item.uid, name, value, @props.item

  on_numeric_field_change: (event) ->
    ###
     * Event handler when the numeric field changed
    ###
    el = event.currentTarget
    name = el.getAttribute("item_key") or el.name
    value = el.value
    console.debug "TableCell:on_numeric_field_change: value=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field @props.item.uid, name, value, @props.item

  on_string_field_blur: (event) ->
    ###
     * Event handler when the string field blurred
    ###
    el = event.currentTarget
    name = el.getAttribute("item_key") or el.name
    value = el.value
    console.debug "TableCell:on_string_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field @props.item.uid, name, value, @props.item

  on_string_field_change: (event) ->
    ###
     * Event handler when the string field changed
    ###
    el = event.currentTarget
    name = el.getAttribute("item_key") or el.name
    value = el.value
    console.debug "TableCell:on_string_field_change: value=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field @props.item.uid, name, value, @props.item

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

  is_edit_allowed: (item_key, item) ->
    ###
     * Checks if the field key is listed in the `allow_edit` list
    ###

    # the global allow_edit overrides all row specific settings
    if not @props.allow_edit
      return no

    # check if the field is listed in the item's allow_edit list
    if item_key in item.allow_edit
      return yes

    return no

  is_disabled: (item_key, item) ->
    ###
     * Checks if the field is marked as disabled
    ###
    return item.disabled or no

  is_required: (item_key, item) ->
    ###
     * Check if the field is marked as required
    ###
    required_fields = item.required or []
    return item_key in required_fields

  get_name: (item_key, item) ->
    ###
     * Get the field name
    ###
    return "#{item_key}.#{item.uid}"

  get_value: (item_key, item) ->
    ###
     * Get the field value
    ###
    value = item[item_key]
    return value

  get_formatted_value: (item_key, item) ->
    ###
     * Get the formatted field value
    ###

    # replacement html or plain value of the current column
    formatted_value = item.replace[item_key] or @get_value item_key, item

    # use the formatted result
    if item_key == "Result"
      formatted_value = item.formatted_result or formatted_value

    return formatted_value

  get_type: (item_key, item) ->
    ###
     * Get the field type
    ###

    # return the type definition of the column
    column = @props.column or {}
    if "type" of column
      return column["type"]

    # check the value
    value = @get_value item_key, item
    if typeof(value) == "boolean"
      return "boolean"

    # check if the field is listed in choices
    choices = item.choices or {}
    if item_key of choices
      return "select"

    # check if the field is an interim
    interims = item.interimfields or []
    if interims.length > 0
      interim_keys = item.interimfields.map (interim) ->
        return interim.keyword
      if item_key in interim_keys
        return "interim"

    # check if the field is a calculated field
    if (item_key == "Result") and item.calculation
      return "calculated"

    # the default
    return "numeric"

  render_content: ->
    ###
      * Render the table cell content
    ###

    # the current rendered column cell name
    item_key = @props.item_key
    # single folderitem
    item = @props.item
    # the current column definition
    column = @props.column

    # form field title
    title = column.title or item_key
    # form field name
    name = @get_name item_key, item
    # form field value
    value = @get_value item_key, item
    # formatted display value of the form field
    formatted_value = @get_formatted_value item_key, item
    # true if the field is editable
    editable = @is_edit_allowed item_key, item
    # true if the field should be disabled
    disabled = @is_disabled item_key, item
    # true if the field is required
    required = @is_required item_key, item
    # field type to render
    type = @get_type item_key, item

    # render readonly field
    if not editable
      field = [
        <ReadonlyField
          key={name}
          name={name}
          value={value}
          title={title}
          formatted_value={formatted_value}
          className="readonly"
          />
      ]
      return field

    # render calculated field
    if type == "calculated"
      fieldname = "#{name}:records"
      field = [
        <ReadonlyField
          key={name}
          name={fieldname}
          value={value}
          title={title}
          formatted_value={formatted_value}
          className="readonly"
          />
        <HiddenField
          key={name + "_hidden"}
          name={fieldname}
          item_key={item_key}
          value={value}
          className="hidden"
          />
      ]
      return field

    # render interim field
    if type == "interim"
      fieldname = "#{name}:records"
      value = value.value
      field = [
        <NumericField
          key={name}
          name={fieldname}
          item_key={item_key}
          defaultValue={value}
          title={title}
          formatted_value={formatted_value}
          placeholder={title}
          disabled={disabled}
          onChange={@on_numeric_field_change}
          onBlur={@on_numeric_field_blur}
          className="form-control input-sm"
          />
      ]
      # N.B. Disabled fields are not send on form submit.
      #      Therefore, we render a hidden field when disabled.
      if disabled
        field.push (
          <HiddenField
            key={name + "_hidden"}
            name={fieldname}
            item_key={item_key}
            value={value}
            className="hidden"
          />
        )
      return field

    # render select field
    if type == "select"
      fieldname = "#{name}:records"
      options = item.choices[item_key]
      field = [
        <Select
          key={name}
          name={fieldname}
          item_key={item_key}
          defaultValue={value}
          title={title}
          disabled={disabled}
          required={required}
          options={options}
          onChange={@on_select_field_change}
          onBlur={@on_select_field_blur}
          className="form-control input-sm"
          />
      ]
      # N.B. Disabled fields are not send on form submit.
      #      Therefore, we render a hidden field when disabled.
      if disabled
        field.push (
          <HiddenField
            key={name + "_hidden"}
            name={fieldname}
            item_key={item_key}
            value={value}
            className="hidden"
          />
        )
      return field

    # render checkbox field
    if type == "boolean"
      fieldname = "#{name}:record:ignore-empty"
      field = [
        <Checkbox
          key={name}
          name={fieldname}
          item_key={item_key}
          value="on"
          title={title}
          defaultChecked={value}
          disabled={disabled}
          onChange={@on_checkbox_field_change}
          className="hidden"
          />
      ]
      # N.B. Disabled fields are not send on form submit.
      #      Therefore, we render a hidden field when disabled.
      if disabled
        field.push (
          <HiddenField
            key={name + "_hidden"}
            name={fieldname}
            item_key={item_key}
            value={value}
            className="hidden"
          />
        )
      return field

    # render numeric field
    if type == "numeric"
      fieldname = "#{name}:records"
      field = [
        <NumericField
          key={name}
          name={fieldname}
          item_key={item_key}
          defaultValue={value}
          title={title}
          formatted_value={formatted_value}
          placeholder={title}
          disabled={disabled}
          onChange={@on_numeric_field_change}
          onBlur={@on_numeric_field_blur}
          className="form-control input-sm"
          />
      ]
      # N.B. Disabled fields are not send on form submit.
      #      Therefore, we render a hidden field when disabled.
      if disabled
        field.push (
          <HiddenField
            key={name + "_hidden"}
            name={fieldname}
            item_key={item_key}
            value={value}
            className="hidden"
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
