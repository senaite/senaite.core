import React from "react"
import TableCell from "./TableCell.coffee"
import Checkbox from "./Checkbox.coffee"


class TableRow extends React.Component

  constructor: (props) ->
    super(props)

  getRowClass: ->
    cls = @props.className
    uid = @props.item.uid
    selected_uids = @props.selected_uids or []
    if uid in selected_uids
      cls += " info"
    return cls

  buildTableCells: ->
    cells = []
    item = @props.item

    # insert select column
    if @props.show_select_column
      cells.push(
        <td key={item.uid}>
          <Checkbox name={@props.select_checkbox_name}
                    onSelect={@props.onSelect}
                    checked={item.uid in @props.selected_uids}
                    value={item.uid}/>
        </td>
    )

    for key, column of @props.columns
      if (!column.toggle)
        continue
      value = item.replace[key] or item[key]

      cells.push(
        <TableCell key={key}
                   item={item}
                   item_key={key}
                   className={key}
                   html={value}/>
      )
    return cells

  render: ->
    <tr className={@getRowClass()}>
      {this.buildTableCells()}
    </tr>


export default TableRow
