import React from "react"
import TableCell from "./TableCell.coffee"


class Row extends React.Component

  buildTableCells: ->
    cells = []
    item = @props.item

    for key, column of @props.columns
      if (!column.toggle)
        continue

      value = item.replace[key] or item[key]
      cells.push(
        <TableCell key={key}
                   className={key}
                   value={value}/>
      )
    return cells

  render: ->
    <tr className={this.props.className}>
      {this.buildTableCells()}
    </tr>


export default Row
