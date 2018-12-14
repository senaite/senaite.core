import React from "react"

import Checkbox from "./Checkbox.coffee"
import HiddenField from "./HiddenField.coffee"
import MultiSelect from "./MultiSelect.coffee"
import NumericField from "./NumericField.coffee"
import CalculatedField from "./CalculatedField.coffee"
import ReadonlyField from "./ReadonlyField.coffee"
import Select from "./Select.coffee"


class TableCell extends React.Component

  constructor: (props) ->
    super(props)

    # Zope Publisher Converter Argument Mapping
    @ZPUBLISHER_CONVERTER = {
      "boolean": ":record:ignore_empty"
      "select": ":records"
      "choices": ":records"
      "multiselect": ":record:list"
      "multichoices": ":record:list"
      "numeric": ":records"
      "readonly": ""
      "default": ":records"
    }

  get_item: ->
    return @props.item

  get_column_key: ->
    return @props.column_key

  render_before_content: (props={}) ->
    column_key = @get_column_key()
    item = @get_item()
    return unless item
    before = item.before
    if column_key not of before
      return null
    # support to render React components
    before_components = item.before_components or {}
    return (
      <span key={column_key + "_before"}
            className="before-item">
        {before_components[column_key]}
        <span dangerouslySetInnerHTML={{__html: before[column_key]}} {...props}></span>
      </span>)

  render_after_content: (props={}) ->
    column_key = @get_column_key()
    item = @get_item()
    return unless item
    after = item.after
    if column_key not of after
      return null
    # support to render React components
    after_components = item.after_components or {}
    return (
      <span key={column_key + "_after"}
            className="after-item">
        {after_components[column_key]}
        <span dangerouslySetInnerHTML={{__html: after[column_key]}} {...props}></span>
      </span>)

  is_edit_allowed: ->
    column_key = @get_column_key()
    item = @get_item()

    # the global allow_edit overrides all row specific settings
    if not @props.allow_edit
      return no

    # check if the field is listed in the item's allow_edit list
    if column_key in item.allow_edit
      return yes

    return no

  is_disabled: ->
    item = @get_item()
    return item.disabled or no

  is_required: ->
    column_key = @get_column_key()
    item = @get_item()
    required_fields = item.required or []
    required = column_key in required_fields
    # make the field conditionally required if the row is selected
    selected = @props.selected
    return required and selected

  get_name: ->
    uid = @get_uid()
    column_key = @get_column_key()
    return "#{column_key}.#{uid}"

  get_uid: ->
    item = @get_item()
    return item.uid

  is_selected: ->
    item = @get_item()
    return item.uid in @props.selected_uids

  get_value: ->
    column_key = @get_column_key()
    item = @get_item()
    value = item[column_key]

    # check if the field is an interim
    interims = @get_interimfields()
    if interims.hasOwnProperty column_key
        # extract the value from the interim field
        # {value: "", keyword: "", formatted_value: "", unit: "", title: ""}
        value = interims[column_key].value or ""

    # values of input fields should not be null
    if value is null
      value = ""

    return value

  ###*
   *  Returns the unit of the interimfield or of the folderitem
  ###
  get_formatted_unit: ->
    column_key = @get_column_key()
    item = @get_item()
    unit = item.Unit
    # extract the unit from the interim field
    # {value: "", keyword: "", formatted_value: "", unit: "", title: ""}
    if @is_interimfield()
      unit = item[column_key].unit
    if not unit
      return ""
    return "<span class='unit'>#{unit}</span>"

  ###*
   * Create a mapping of interim keyword -> interim field
   *
   * Interim fields are record fields with a format like this:
   * {value: "", keyword: "", formatted_value: "", unit: "", title: ""}
  ###
  get_interimfields: ->
    item = @get_item()
    interims = item.interimfields or []
    mapping = {}
    interims.map (item, index) ->
      mapping[item.keyword] = item
    return mapping

  is_interimfield: ->
    column_key = @get_column_key()
    interims = @get_interimfields()
    return interims.hasOwnProperty column_key

  get_choices: ->
    item = @get_item()
    return item.choices or {}

  is_result_column: ->
    column_key = @get_column_key()
    if column_key == "Result"
      return yes
    return no

  get_formatted_value: ->
    column_key = @get_column_key()
    item = @get_item()

    # replacement html or plain value of the current column
    formatted_value = item.replace[column_key] or @get_value()

    # use the formatted result
    if @is_result_column()
      formatted_value = item.formatted_result or formatted_value
      # Append the unit to the formatted value
      if formatted_value
        formatted_value += @get_formatted_unit()
    else if @is_interimfield()
      # Append the unit to the formatted value
      if formatted_value
        formatted_value += @get_formatted_unit()

    return formatted_value

  get_type: ->
    column_key = @get_column_key()
    item = @get_item()

    # true if the field is editable
    editable = @is_edit_allowed()
    resultfield = @is_result_column()

    # readonly field
    if not editable
      return "readonly"

    # calculated fields are also in editable mode readonly
    if resultfield and item.calculation
      return "calculated"

    # type definition of the column has precedence
    column = @props.column or {}
    if "type" of column
      return column["type"]

    # check if the field is a boolean
    value = @get_value()
    if typeof(value) == "boolean"
      return "boolean"

    # check if the field is listed in choices
    choices = @get_choices()
    if column_key of choices
      return "select"

    # check if the field is an interim
    if @is_interimfield()
      return "interim"

    # the default
    return "numeric"

  ###*
   * Creates a readonly field component
   * @param props {object} properties passed to the component
   * @returns ReadonlyField component
  ###
  create_readonly_field: ({props}={}) ->
    column_key = @get_column_key()
    item = @get_item()
    props ?= {}

    name = @get_name()
    value = @get_value()
    formatted_value = @get_formatted_value()
    uid = @get_uid()
    css_class = "readonly"

    return (
      <ReadonlyField
        key={name}
        uid={uid}
        name={name}
        value={value}
        formatted_value={formatted_value}
        className={css_class}
        {...props}
        />)

  ###*
   * Creates a calculated field component
   * @param props {object} properties passed to the component
   * @returns CalculatedField component
  ###
  create_calculated_field: ({props}={}) ->
    column_key = @get_column_key()
    item = @get_item()
    props ?= {}

    name = @get_name()
    value = @get_value()
    formatted_value = @get_formatted_value()
    unit = @get_formatted_unit()
    uid = @get_uid()
    title = @props.column.title or column_key
    selected = @is_selected()
    required = @is_required()
    css_class = "form-control input-sm calculated"
    if required then css_class += " required"

    return (
      <CalculatedField
        key={name}
        uid={uid}
        item={item}
        name={name}
        value={value}
        column_key={column_key}
        title={title}
        formatted_value={formatted_value}
        placeholder={title}
        selected={selected}
        required={required}
        className={css_class}
        after={unit}
        update_editable_field={@props.update_editable_field}
        save_editable_field={@props.save_editable_field}
        {...props}
        />)

  ###*
   * Creates a hidden field component
   * @param props {object} properties passed to the component
   * @returns HiddenField component
  ###
  create_hidden_field: ({props}={}) ->
    column_key = @get_column_key()
    item = @get_item()
    props ?= {}

    name = @get_name()
    value = @get_value()
    formatted_value = @get_formatted_value()
    uid = @get_uid()
    title = @props.column.title or column_key

    return (
      <HiddenField
        key={name + "_hidden"}
        uid={uid}
        name={name}
        value={value}
        column_key={column_key}
        {...props}
        />)

  ###*
   * Creates a numeric field component
   * @param props {object} properties passed to the component
   * @returns NumericField component
  ###
  create_numeric_field: ({props}={}) ->
    column_key = @get_column_key()
    item = @get_item()
    props ?= {}

    name = @get_name()
    value = @get_value()
    formatted_value = @get_formatted_value()
    unit = @get_formatted_unit()
    uid = @get_uid()
    converter = @ZPUBLISHER_CONVERTER["numeric"]
    fieldname = name + converter
    title = @props.column.title or column_key
    selected = @is_selected()
    disabled = @is_disabled()
    required = @is_required()
    css_class = "form-control input-sm"
    if required then css_class += " required"

    return (
      <NumericField
        key={name}
        uid={uid}
        item={item}
        name={fieldname}
        defaultValue={value}
        column_key={column_key}
        title={title}
        formatted_value={formatted_value}
        placeholder={title}
        selected={selected}
        disabled={disabled}
        required={required}
        className={css_class}
        after={unit}
        update_editable_field={@props.update_editable_field}
        save_editable_field={@props.save_editable_field}
        {...props}
        />)

  ###*
   * Creates a select field component
   * @param props {object} properties passed to the component
   * @returns SelectField component
  ###
  create_select_field: ({props}={}) ->
    column_key = @get_column_key()
    item = @get_item()
    props ?= {}

    name = @get_name()
    value = @get_value()
    options = item.choices[column_key] or []
    formatted_value = @get_formatted_value()
    uid = @get_uid()
    converter = @ZPUBLISHER_CONVERTER["select"]
    fieldname = name + converter
    title = @props.column.title or column_key
    selected = @is_selected()
    disabled = @is_disabled()
    required = @is_required()
    css_class = "form-control input-sm"
    if required then css_class += " required"

    return (
      <Select
        key={name}
        uid={uid}
        item={item}
        name={fieldname}
        defaultValue={value}
        column_key={column_key}
        title={title}
        disabled={disabled}
        selected={selected}
        required={required}
        options={options}
        className={css_class}
        update_editable_field={@props.update_editable_field}
        save_editable_field={@props.save_editable_field}
        {...props}
        />)

  ###*
   * Creates a multiselect field component
   * @param props {object} properties passed to the component
   * @returns SelectField component
  ###
  create_multiselect_field: ({props}={}) ->
    column_key = @get_column_key()
    item = @get_item()
    props ?= {}

    name = @get_name()
    value = @get_value()
    options = item.choices[column_key] or []
    formatted_value = @get_formatted_value()
    uid = @get_uid()
    converter = @ZPUBLISHER_CONVERTER["multiselect"]
    fieldname = name + converter
    title = @props.column.title or column_key
    selected = @is_selected()
    disabled = @is_disabled()
    required = @is_required()
    css_class = "form-control input-sm"
    if required then css_class += " required"

    return (
      <MultiSelect
        key={name}
        uid={uid}
        item={item}
        name={fieldname}
        defaultValue={value}
        column_key={column_key}
        title={title}
        disabled={disabled}
        selected={selected}
        required={required}
        options={options}
        className={css_class}
        update_editable_field={@props.update_editable_field}
        save_editable_field={@props.save_editable_field}
        {...props}
        />)

  ###*
   * Creates a checkbox field component
   * @param props {object} properties passed to the component
   * @returns Checkbox component
  ###
  create_checkbox_field: ({props}={}) ->
    column_key = @get_column_key()
    item = @get_item()
    props ?= {}

    name = @get_name()
    value = @get_value()
    options = item.choices[column_key] or []
    formatted_value = @get_formatted_value()
    uid = @get_uid()
    converter = @ZPUBLISHER_CONVERTER["boolean"]
    fieldname = name + converter
    title = @props.column.title or column_key
    selected = @is_selected()
    disabled = @is_disabled()
    required = @is_required()
    css_class = "checkbox"
    if required then css_class += " required"

    return (
      <Checkbox
        key={name}
        uid={uid}
        item={item}
        name={fieldname}
        value="on"
        column_key={column_key}
        title={title}
        defaultChecked={value}
        disabled={disabled}
        className={css_class}
        update_editable_field={@props.update_editable_field}
        save_editable_field={@props.save_editable_field}
        {...props}
        />)

  render_content: ->
    # the current rendered column cell name
    column_key = @get_column_key()
    # single folderitem
    item = @get_item()
    # return if there is no item
    if not item
      console.warn "Skipping empty folderitem for column '#{column_key}'"
      return null
    # the UID of the folderitem
    uid = @get_uid()
    # field type to render
    type = @get_type()
    # the field to return
    field = []

    if type == "readonly"
      field = field.concat @create_readonly_field()
    else if type == "calculated"
      field = field.concat @create_calculated_field()
    else if type == "interim"
      field = field.concat @create_numeric_field()
    else if type in ["select", "choices"]
      field = field.concat @create_select_field()
    else if type in ["multiselect", "multichoices"]
      field = field.concat @create_multiselect_field()
    else if type == "boolean"
      field = field.concat @create_checkbox_field()
    else if type == "numeric"
      field = field.concat @create_numeric_field()

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
