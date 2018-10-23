import React from "react"
import TableRow from "./TableRow.coffee"


class Table extends React.Component

  constructor: (props) ->
    super(props)

  componentDidMount: ->

  buildHeaderColumns: ->
    columns = []

    for key, value of @props.columns
      if (!value.toggle)
        continue

      columns.push(
        <th key={key}>{value.title}</th>
      )
    return columns

  buildFolderItems: ->
    rows = []

    for index, item of @props.folderitems
      rows.push(
        <TableRow className={item.state_class}
                  key={index}
                  item={item}
                  review_states={this.props.review_states}
                  columns={this.props.columns}/>
      )
    return rows

  render: ->
    <table id={@props.id}
            className={@props.className}>
      <thead>
        <tr>
          {@buildHeaderColumns()}
        </tr>
      </thead>
      <tbody>
        {@buildFolderItems()}
      </tbody>
      <tfoot>
      </tfoot>
    </table>


export default Table
