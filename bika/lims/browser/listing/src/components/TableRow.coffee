import React from "react"
import TableCells from "./TableCells.coffee"


class TableRow extends React.Component

  constructor: (props) ->
    super(props)

  is_category_expanded: ->
    category = @props.category
    if not category
      return yes
    return category in @props.expanded_categories

  is_visible: ->
    if not @is_category_expanded()
      return no
    return yes

  render: ->
    <tr className={@props.className}
        onClick={@props.onClick}
        style={{display: if @is_visible() then "table-row" else "none"}}
        uid={@props.uid}>
      <TableCells {...@props}/>
    </tr>


export default TableRow
