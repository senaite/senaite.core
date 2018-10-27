import React from "react"


class TableHeaderCell extends React.Component
  ###
   * The table header cell component renders a single header cell
  ###

  constructor: (props) ->
    super(props)

  render: ->
    <th title={@props.title}
        index={@props.index}
        sort_order={@props.sort_order}
        className={@props.className}
        onClick={@props.onClick}>
      <span>{@props.title}</span>
    </th>


export default TableHeaderCell
