import React from "react"
import TableRow from "./TableRow.coffee"
import TableHeaderRow from "./TableHeaderRow.coffee"


class Table extends React.Component

  constructor: (props) ->
    super(props)

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
        <TableHeaderRow sort_on={this.props.sort_on}
                        sort_order={this.props.sort_order}
                        onSort={this.props.onSort}
                        columns={this.props.columns}/>
      </thead>
      <tbody>
        {@buildFolderItems()}
      </tbody>
      <tfoot>
      </tfoot>
    </table>


export default Table
