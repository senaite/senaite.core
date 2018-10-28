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


  get_review_state_by_id: (id) ->
    ###
     * Fetch the current review_state item by id
    ###

    current = null

    # review_states is the list of review_state items from the listing view
    for review_state in @props.review_states
      if review_state.id == id
        current = review_state
        break

    if not current
      throw "No review_state definition found for ID #{id}"

    return current

  get_column_order: ->
    ###
     * Get the column order defined in the current selected review_state item
    ###
    review_state_item = @get_review_state_by_id @props.review_state
    return review_state_item.columns

  build_header_rows: ->
    ###
     * Build the table header rows (actually just one row)
    ###
    rows = []

    rows.push(
      <TableHeaderRow
        key="header_row"
        sort_on={@props.sort_on}
        on_select_checkbox_checked={@on_select_checkbox_checked}
        sort_order={@props.sort_order}
        catalog_indexes={@props.catalog_indexes}
        on_header_column_click={@props.onSort}
        folderitems={@props.folderitems}
        selected_uids={@props.selected_uids}
        select_checkbox_name={@props.select_checkbox_name}
        columns={@props.columns}
        column_order={@get_column_order()}
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

  get_expanded_categories: ->
    ###
     * calculate expanded categories
    ###

    # return all categories if the flag is on
    if @props.expand_all_categories
      return @props.categories

    # expand all categories for searches
    if @filter
      return @props.categories

    # no categories are expanded if no items are selected
    if not @props.selected_uids
      return []

    categories = []
    for folderitem in @props.folderitems
      # item is selected, get the category
      if folderitem.uid in @props.selected_uids
        category = folderitem.category
        if category not in categories
          categories.push category

    return categories

  build_category_rows: ->
    ###
     * Build category rows
    ###
    rows = []

    # calculate expanded categories
    expanded_categories = @get_expanded_categories()

    for category in @props.categories
      expanded = category in expanded_categories

      rows.push(
        <TableCategoryRow
            key={category}
            className="category"
            colspan={@get_column_count()}
            category={category}
            expanded={expanded}
            on_select_checkbox_checked={@on_select_checkbox_checked}
            folderitems={@props.folderitems}
            review_states={@props.review_states}
            selected_uids={@props.selected_uids}
            select_checkbox_name={@props.select_checkbox_name}
            columns={@props.columns}
            column_order={@get_column_order()}
            show_select_column={@props.show_select_column}
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
          key={index}
          className={item.state_class}
          on_select_checkbox_checked={@on_select_checkbox_checked}
          item={item}
          review_states={@props.review_states}
          selected_uids={@props.selected_uids}
          select_checkbox_name={@props.select_checkbox_name}
          columns={@props.columns}
          column_order={@get_column_order()}
          show_select_column={@props.show_select_column}
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
