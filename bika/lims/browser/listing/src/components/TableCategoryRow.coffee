import React from "react"

import TableRow from "./TableRow.coffee"


class TableCategoryRow extends React.Component
  ###
   * A collapsible category table row
  ###

  constructor: (props) ->
    super(props)

    @state =
      expanded: no

    @on_row_click = @on_row_click.bind @

  on_row_click: (event) ->
    ###
     * Event handler when the row was clicked
    ###
    el = event.currentTarget
    category = el.getAttribute "category"
    @setState
      expanded: not @state.expanded
    console.debug "TableCategoryRow::on_row_click: category #{category} clicked"

  build_category_cells: ->
    ###
     * Build the category cells
    ###
    cells = []

    cls = "collapsed"
    icon_cls = "glyphicon glyphicon-collapse-up"

    # calculate the CSS class for expanded
    if @state.expanded
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

  build_rows: ->
    ###
     * Build the category row + the content rows
    ###
    rows = []

    rows.push(
      <tr key={@props.category}
          onClick={@on_row_click}
          category={@props.category}
          className={@props.className}>
      {@build_category_cells()}
      </tr>
    )

    # return only the category row if it is not expanded
    if not @state.expanded
      return rows

    for index, item of @props.folderitems
      if item.category != @props.category
        continue

      console.info "Adding Item #{item.title} to the category #{@props.category}"

      rows.push(
        <TableRow
          key={index}
          className={item.state_class}
          on_select_checkbox_checked={@props.on_select_checkbox_checked}
          item={item}
          review_states={@props.review_states}
          selected_uids={@props.selected_uids}
          select_checkbox_name={@props.select_checkbox_name}
          columns={@props.columns}
          column_order={@props.column_order}
          show_select_column={@props.show_select_column}
          />
      )

    return rows

  render: ->
    @build_rows()


export default TableCategoryRow
