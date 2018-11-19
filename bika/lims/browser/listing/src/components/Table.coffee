import React from "react"

import TableCategoryRow from "./TableCategoryRow.coffee"
import TableHeaderRow from "./TableHeaderRow.coffee"
import TableRow from "./TableRow.coffee"


class Table extends React.Component
  ###
   * The table component renders the header, body and footer cells
  ###

  constructor: (props) ->
    super(props)

    # bind event handler to local context
    @on_select_checkbox_checked = @on_select_checkbox_checked.bind @

  on_select_checkbox_checked: (event) ->
    ###
     * Event handler when a row checkbox was checked/unchecked
    ###
    el = event.currentTarget
    uid = el.value
    checked = el.checked

    # call the parent event handler
    @props.on_select_checkbox_checked uid, checked

  get_column_count: ->
    ###
     * Calculate the current number of displayed columns
    ###
    count = 0
    for k, v of @props.columns
      if v.toggle
        count += 1
    # add 1 if the select column is rendered
    if @props.show_select_column
      count += 1
    return count

  build_header_rows: ->
    ###
     * Build the table header rows (actually just one row)
    ###
    rows = []

    rows.push(
      <TableHeaderRow
        {...@props}  # pass in all properties from the table component
        key="header_row"  # internal key
        on_select_checkbox_checked={@on_select_checkbox_checked}
        />
    )

    return rows

  build_body_rows: ->
    ###
     * Build the table body rows
    ###
    if @props.show_categories
      return @build_category_rows()
    return @build_content_rows()

  build_footer_rows: ->
    ###
     * Build the table footer rows
    ###
    return []

  build_category_rows: ->
    ###
     * Build category rows
    ###
    rows = []

    for category in @props.categories
      expanded = category in @props.expanded_categories
      rows.push(
        <TableCategoryRow
          key={category}  # internal key
          {...@props}  # pass in all properties from the table component
          className="category"
          category={category}
          expanded={expanded}
          on_select_checkbox_checked={@on_select_checkbox_checked}
          />
      )

    return rows

  build_content_rows: ->
    ###
     * Build content rows
    ###
    rows = []

    for index, item of @props.folderitems
      rows.push(
        <TableRow
          key={index}  # internal key
          {...@props}  # pass in all properties from the table component
          className={item.state_class}
          on_select_checkbox_checked={@on_select_checkbox_checked}
          item={item}
          />
      )

    return rows

  render: ->
    <table id={@props.id}
           className={@props.className}>
      <thead>
        {@build_header_rows()}
      </thead>
      <tbody>
        {@build_body_rows()}
      </tbody>
      <tfoot>
        {@build_footer_rows()}
      </tfoot>
    </table>


export default Table
