import React from "react"
import TableHeaderRow from "./TableHeaderRow.coffee"
import TableRows from "./TableRows.coffee"


class Table extends React.Component

  constructor: (props) ->
    super(props)

  render: ->
    <table id={@props.id} className={@props.className}>
      <thead>
        <TableHeaderRow {...@props}/>
      </thead>
      <tbody>
        <TableRows {...@props}/>
      </tbody>
    </table>


export default Table
