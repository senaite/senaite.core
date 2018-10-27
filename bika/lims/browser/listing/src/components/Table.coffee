import React from "react"

import TableRow from "./TableRow.coffee"
import TableHeaderRow from "./TableHeaderRow.coffee"
import TableCategoryRow from "./TableCategoryRow.coffee"


class Table extends React.Component
  ###
   * The table component renders the header, body and footer cells
  ###

  constructor: (props) ->
    super(props)
    @on_select_checkbox_checked = @on_select_checkbox_checked.bind @

  on_select_checkbox_checked: (event) ->
    ###
     * Event handler when a row checkbox was checked/unchecked
    ###
    el = event.currentTarget
    uid = el.value
    checked = el.checked

    # call the parent event handler
    @props.onSelect uid, checked

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
        key="header_row"
        sort_on={this.props.sort_on}
        on_select_checkbox_checked={@on_select_checkbox_checked}
        sort_order={this.props.sort_order}
        onSort={this.props.onSort}
        folderitems={@props.folderitems}
        selected_uids={@props.selected_uids}
        select_checkbox_name={@props.select_checkbox_name}
        columns={this.props.columns}
        show_select_column={@props.show_select_column}
        show_select_all_checkbox={@props.show_select_all_checkbox}
        show_categories={@props.show_categories}
        expand_all_categories={@props.expand_all_categories}
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
      rows.push(
        <TableCategoryRow
            key={category}
            className="category"
            colspan={@get_column_count()}
            category={category}
            expand_all_categories={@props.expand_all_categories}
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
          className={item.state_class}
          on_select_checkbox_checked={@on_select_checkbox_checked}
          key={index}
          item={item}
          review_states={this.props.review_states}
          selected_uids={@props.selected_uids}
          select_checkbox_name={@props.select_checkbox_name}
          columns={this.props.columns}
          show_select_column={@props.show_select_column}
          show_select_all_checkbox={@props.show_select_all_checkbox}
          categories={@props.categories}
          show_categories={@props.show_categories}
          expand_all_categories={@props.expand_all_categories}
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
