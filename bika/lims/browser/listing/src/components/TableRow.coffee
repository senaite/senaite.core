import React from "react"
import TableCells from "./TableCells.coffee"


class TableRow extends React.Component

  constructor: (props) ->
    super(props)

  render: ->
    <tr className={@props.className}
        onClick={@props.onClick}
        category={@props.category}
        uid={@props.uid}>
      <TableCells {...@props}/>
    </tr>


export default TableRow
