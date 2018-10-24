import React from "react"


class TableCell extends React.Component

  constructor: (props) ->
    super(props)

  renderBefore: ->
    before = @props.item.before
    item_key = @props.item_key
    if @props.item_key not of before
      return null
    return <span className="before-item"
                 dangerouslySetInnerHTML={{__html: before[item_key]}}>
           </span>

  renderAfter: ->
    after = @props.item.after
    item_key = @props.item_key
    if item_key not of after
      return null
    return <span className="after-item"
                 dangerouslySetInnerHTML={{__html: after[item_key]}}>
           </span>

  render: ->
    <td className={@props.className}>
      {this.renderBefore()}
      <span dangerouslySetInnerHTML={{__html: @props.html}}></span>
      {this.renderAfter()}
    </td>


export default TableCell
