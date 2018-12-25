import React from "react"
import TableRow from "./TableRow.coffee"


class TableCategoryRow extends React.Component

  constructor: (props) ->
    super(props)
    # Bind event handler to local context
    @on_category_click = @on_category_click.bind @

  on_category_click: (event) ->
    el = event.currentTarget
    category = el.getAttribute "category"
    console.debug "TableCategoryRow::on_row_click: category #{category} clicked"

    # notify parent event handler with the extracted values
    if @props.on_category_click
      # @param {string} category: The category title
      @props.on_category_click category

  build_category: ->
    # collaped css
    cls = "collapsed"
    icon_cls = "glyphicon glyphicon-collapse-up"

    # expanded css
    if @props.expanded
      cls = "expanded"
      icon_cls = "glyphicon glyphicon-collapse-down"

    return (
      <td key="toggle"
          className={cls}
          colSpan={@props.column_count}>
        <span className={icon_cls}></span> {@props.category}
      </td>
    )

  render: ->
    <tr category={@props.category}
        onClick={@on_category_click}
        className={@props.className}>
      {@build_category()}
    </tr>


export default TableCategoryRow
