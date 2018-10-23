import React from "react"

import TableHeaderCell from "./TableHeaderCell.coffee"


class TableHeaderRow extends React.Component

  constructor: (props) ->
    super(props)
    @onHeaderCellClick = @onHeaderCellClick.bind @

  onHeaderCellClick: (event) ->
    el = event.currentTarget
    index = el.getAttribute "index"
    sort_order = el.getAttribute "sort_order"
    console.debug "HEADER CLICKED sort_on='#{index}' sort_order=#{sort_order}"

    if "active" in el.classList
      if sort_order == "ascending"
        sort_order = "descending"
      else
        sort_order = "ascending"

    @props.onSort index, sort_order


  buildTableHeaderCells: ->
    cells = []
    item = @props.item

    for key, column of @props.columns

      # Skip hidden colums
      if (!column.toggle)
        continue

      title = column.title
      index = column.index or ""
      sort_on = @props.sort_on or "created"
      sort_order = @props.sort_order or "ascending"
      is_sort_column = index == sort_on

      cls = [key]
      if index
        cls.push "sortable"
      if is_sort_column
        cls.push "active #{sort_order}"

      cells.push(
        <TableHeaderCell key={key}
                         className={cls.join " "}
                         onClick={@onHeaderCellClick}
                         index={index}
                         sort_order={sort_order}
                         title={column.title}/>
      )
    return cells

  render: ->
    <tr className={this.props.className}>
      {this.buildTableHeaderCells()}
    </tr>


export default TableHeaderRow
