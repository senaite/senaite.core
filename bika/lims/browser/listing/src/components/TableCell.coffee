import React from "react"

import Select from "./Select.coffee"
import NumericField from "./NumericField.coffee"
import Checkbox from "./Checkbox.coffee"
import StringField from "./StringField.coffee"


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

    @editable_fields = [
      "warn_min"
      "min"
      "warn_max"
      "max"
      "Price"
      "Hidden"
    ]

  on_cell_select_field_change: (event) ->
    ###
     * Event handler when the select field changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "TableCell:on_cell_select_field_change: value=#{value}"

  on_cell_checkbox_field_change: (event) ->
    ###
     * Event handler when the checkbox field changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "TableCell:on_cell_checkbox_field_change: value=#{value}"

  on_cell_numeric_field_change: (event) ->
    ###
     * Event handler when the numeric field changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "TableCell:on_cell_numeric_field_change: value=#{value}"

  on_cell_string_field_change: (event) ->
    ###
     * Event handler when the string field changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "TableCell:on_cell_string_field_change: value=#{value}"

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

    # row is not selected
    if not selected
      return no

    # XXX Fix inconsistent behavior
    if item_key of item.choices
      return yes

    # check if the field is listed in the item's allow_edit list
    if item_key in item.allow_edit
      return yes

    if item_key in @editable_fields
      return yes

    return no

  render_content: ->
    ###
      * Render the table cell content
    ###

    # return a plain text field if the cell can not be edited
    if not @is_edit_allowed()
      return <span dangerouslySetInnerHTML={{__html: @props.html}}></span>


    # Handle editable cell

    item = @props.item
    item_key = @props.item_key
    item_uid = item.uid
    name = "#{item_key}.#{item_uid}"
    value = item[item_key]
    cell = []

    # Render selection field
    if item_key of item.choices
      fieldname = "#{name}:records"
      options = item.choices[item_key]
      return <Select name={fieldname}
                     value={value}
                     title={item_key}
                     options={options}
                     disabled={@props.disabled}
                     onChange={@on_cell_select_field_change}
                     className="listing_select_entry" />

    # Render boolean field
    if typeof(value) == "boolean"
      key = "boolean"
      fieldname = "#{name}:record:ignore-empty"
      return <Checkbox name={fieldname}
                       value={value}
                       title={item_key}
                       defaultChecked={value}
                       disabled={@props.disabled}
                       onChange={@on_cell_checkbox_field_change}
                       className="listing_checkbox_entry" />


    # Render numerif field
    fieldname = "#{name}:records"
    return <NumericField key={key}
                         name={fieldname}
                         defaultValue={value}
                         title={item_key}
                         disabled={@props.disabled}
                         onChange={@on_cell_numeric_field_change}
                         className="listing_string_entry numeric" />

  render: ->
    <td className={@props.className}>
      <div className="form-group">
        {@render_before_content()}
        {@render_content()}
        {@render_after_content()}
      </div>
    </td>


export default TableCell
