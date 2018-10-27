import React from "react"


class TableCategoryRow extends React.Component
  ###
   * A collapsible category table row
  ###

  constructor: (props) ->
    super(props)
    @on_row_click = @on_row_click.bind @

  on_row_click: (event) ->
    ###
     * Event handler when the row was clicked
    ###
    el = event.currentTarget
    category = el.getAttribute "category"
    console.debug "TableCategoryRow::on_row_click: category #{category} clicked"

  build_category_cells: ->
    ###
     * Build the category cells
    ###

    cells = []

    expanded = @props.expanded

    cls = "collapsed"
    icon_cls = "glyphicon glyphicon-collapse-up"

    # calculate the CSS class for expanded
    if expanded
      cls = "expanded"
      icon_cls = "glyphicon glyphicon-collapse-down"

    # insert the toggle cell
    cells.push(
      <td key="toggle" className={cls}>
        <span className={icon_cls}></span>
      </td>
    )

    # subtract 1 for the toggle cell
    colspan = @props.colspan - 1

    cells.push(
      <td key={@props.category}
          colSpan={colspan}>
        {@props.category}
      </td>
    )

    return cells

  render: ->
    <tr onClick={@on_row_click}
        category={@props.category}
        className={@props.className}>
     {@build_category_cells()}
    </tr>


export default TableCategoryRow
