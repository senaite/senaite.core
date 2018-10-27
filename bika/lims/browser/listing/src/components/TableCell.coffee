import React from "react"


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
    contents <span className="before-item"
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

  render: ->
    <td className={@props.className}>
      {this.render_before_content()}
      <span dangerouslySetInnerHTML={{__html: @props.html}}></span>
      {this.render_after_content()}
    </td>


export default TableCell
