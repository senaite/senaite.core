import React from "react"


class TableHeaderCell extends React.Component

  constructor: (props) ->
    super(props)

  render: ->
    <th index={@props.index}
        sort_order={@props.sort_order}
        className={@props.className}
        onClick={@props.onClick}>
      <span>{@props.title}</span>
    </th>


export default TableHeaderCell
