import React from "react"

import Select from "./Select.coffee"


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
    if item_key of item.choices
      options = item.choices[item_key]
      value = item[item_key]
      return <Select
               value={value}
               name={item_key}
               className="form-control input-sm"
               options={options} />
    return content

  render: ->
    <td className={@props.className}>
      {@render_before_content()}
      {@render_content()}
      {@render_after_content()}
    </td>


export default TableCell
