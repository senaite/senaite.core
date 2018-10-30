import React from "react"

import TableRow from "./TableRow.coffee"


class TableCategoryRow extends React.Component
  ###
   * A collapsible category table row
  ###

  constructor: (props) ->
    super(props)

    # bind event handler to local context
    @on_category_click = @on_category_click.bind @

  on_category_click: (event) ->
    ###
     * Event handler when the row was clicked
    ###
    el = event.currentTarget
    category = el.getAttribute "category"
    console.debug "TableCategoryRow::on_row_click: category #{category} clicked"

    if @props.on_category_click then @props.on_category_click category

  build_category_cells: ->
    ###
     * Build the category cells
    ###
    cells = []

    cls = "collapsed"
    icon_cls = "glyphicon glyphicon-collapse-up"

    # calculate the CSS class for expanded
    if @props.expanded
      cls = "expanded"
      icon_cls = "glyphicon glyphicon-collapse-down"

    # insert the toggle cell
    cells.push(
      <td key="toggle" className={cls}>
        <span className={icon_cls}></span>
      </td>
    )

    # subtract 1 for the toggle cell
    colspan = @props.column_count - 1

    cells.push(
      <td key={@props.category}
          colSpan={colspan}>
       {@props.category}
      </td>
    )

    return cells

  build_rows: ->
    ###
     * Build the category row + the content rows
    ###
    rows = []

    rows.push(
      <tr key={@props.category}
          onClick={@on_category_click}
          category={@props.category}
          className={@props.className}>
        {@build_category_cells()}
      </tr>
    )

    # return only the category row if it is not expanded
    if not @props.expanded
      return rows

    for index, item of @props.folderitems

      # skip items of other categories
      if item.category != @props.category
        continue

      rows.push(
        <TableRow
          key={index}  # internal key
          {...@props}  # pass in all properties from the table component
          className={item.state_class}
          item={item}
          />
      )

    return rows

  render: ->
    @build_rows()


export default TableCategoryRow
