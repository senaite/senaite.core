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

  render_content: ->
    ###
     * Render the table cell content
    ###

    item = @props.item
    item_key = @props.item_key
    item_uid = item.uid
    name = "#{item_key}.#{item_uid}:records"
    value = item[item_key]

    # Render selection widget
    if item_key of item.choices
      options = item.choices[item_key]
      return <Select name={name}
                     value={value}
                     title={item_key}
                     options={options}
                     onChange={@on_cell_select_field_change}
                     className="form-control input-sm" />

    # check if the current field is listed in the allow_edit list
    else if item_key in item.allow_edit

      # Render boolean widget
      if typeof(value) == "boolean"
        return <Checkbox name={name}
                         value={value}
                         title={item_key}
                         defaultChecked={value}
                         onChange={@on_cell_checkbox_field_change}
                         className="checkbox" />

      # Render numeric widget
      return <NumericField
               name={name}
               defaultValue={value}
               title={item_key}
               onChange={@on_cell_numeric_field_change}
               className="numeric form-control input-sm" />

    else
      return (
        <StringField
          type="hidden"
          name={name}
          value={value}
          title={item_key} />
        <span dangerouslySetInnerHTML={{__html: @props.html}}></span>
      )

  render: ->
    <td className={@props.className}>
      {@render_before_content()}
      {@render_content()}
      {@render_after_content()}
    </td>


export default TableCell
