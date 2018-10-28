import React from "react"

import Select from "./Select.coffee"
import NumericField from "./NumericField.coffee"
import Checkbox from "./Checkbox.coffee"


class TableCell extends React.Component
  ###
   * The table cell component renders a single cell
  ###

  constructor: (props) ->
    super(props)

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
    content = <span dangerouslySetInnerHTML={{__html: @props.html}}></span>

    item = @props.item
    item_key = @props.item_key
    item_uid = item.uid
    name = "#{item_key}.#{item_uid}:records"
    value = item[item_key]

    if item_key of item.choices
      options = item.choices[item_key]
      return <Select value={value}
                     name={name}
                     className="form-control input-sm"
                     options={options} />

    else if item_key in item.allow_edit
      if typeof(value) == "boolean"
        return <Checkbox name={name}
                         value={value}
                         checked={value}/>

      return <NumericField
               size="5"
               name={name}
               value={value}
               className="form-control input-sm" />

    return content

  render: ->
    <td className={@props.className}>
      {@render_before_content()}
      {@render_content()}
      {@render_after_content()}
    </td>


export default TableCell
