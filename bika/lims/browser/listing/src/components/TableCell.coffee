import React from "react"


class TableCell extends React.Component

  constructor: (props) ->
    super(props)

  componentDidMount: ->

  render: ->
    <td className={@props.className}
        dangerouslySetInnerHTML={{__html: @props.value}}>
    </td>


export default TableCell
