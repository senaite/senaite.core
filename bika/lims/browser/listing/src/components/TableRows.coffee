import React from "react"
import TableRow from "./TableRow.coffee"
import TableCategoryRow from "./TableCategoryRow.coffee"
import TableRemarksRow from "./TableRemarksRow.coffee"


class TableRows extends React.Component

  constructor: (props) ->
    super(props)
    # Bind event handler to local context
    @on_row_expand_click = @on_row_expand_click.bind @

  on_row_expand_click: (event) ->
    row = event.currentTarget
    first_td = row.children.item(0)
    if event.target == first_td
      uid = row.getAttribute "uid"
      if @props.on_row_expand_click
        @props.on_row_expand_click uid

  is_selected: (item) ->
    uid = item.uid
    selected_uids = @props.selected_uids or []
    return uid in selected_uids

  is_expanded: (item) ->
    expanded = @props.expanded_rows or []
    return item.uid in expanded

  get_children: (item) ->
    uid = item.uid
    children = @props.children or {}
    item_children = children[uid] or []
    return item_children

  is_category_expanded: (category) ->
    return category in @props.expanded_categories

  is_item_disabled: (item) ->
    return item.disabled or no

  is_child_item: (item) ->
    return yes if item.parent

  get_item_category: (item) ->
    return item.category or null

  get_item_children: (item) ->
    # list of UIDs in the folderitem
    return item.children or []

  has_item_children: (item) ->
    children = @get_item_children item
    return children.length > 0

  get_remarks_columns: ->
    columns = []
    for key, value of @props.columns
      if value.type == "remarks"
        columns.push key
    return columns

  get_item_uid: (item) ->
    return item.uid

  get_item_css: (item) ->
    cls = ["contentrow"]

    # review state
    if item.state_class
      cls = cls.concat item.state_class.split " "

    # selected
    if @is_selected item
      cls.push "info"

    # child/parent
    if @is_child_item item
      cls.push "child"
    else
      cls.push "parent"

    # expandable
    if @has_item_children item
      if @is_expanded item
        cls.push "expanded"
      else
        cls.push "collapsed"

    return cls.join " "

  render_categorized_rows: ->
    rows = []

    # Render categorized rows
    if @props.show_categories
      for category in @props.categories
        expanded = @is_category_expanded category
        rows.push(
          <TableCategoryRow
            {...@props}
            key={category}
            category={category}
            expanded={expanded}
            className="categoryrow"
            />)
        # append expanded rows
        if expanded
          content_rows = @build_rows category: category
          rows = rows.concat content_rows
    # Render uncatgorized rows
    else
      rows = @build_rows()

    return rows

  build_rows: ({category, folderitems} = {}) ->
    rows = []

    category ?= null
    folderitems ?= @props.folderitems

    for item in folderitems

      # skip items of other categories
      if category and @get_item_category(item) != category
        continue

      uid = @get_item_uid item
      css = @get_item_css item

      # list of child UIDs in the folderitem
      children = @get_item_children item

      expanded = @is_expanded item
      selected = @is_selected item
      disabled = @is_item_disabled item
      expandable = @has_item_children item

      rows.push(
        <TableRow
          {...@props}
          key={uid}
          item={item}
          uid={uid}
          expanded={expanded}
          selected={selected}
          disabled={disabled}
          className={css}
          onClick={expandable and @on_row_expand_click or undefined}
          />)

      # columns with type="remarks" set are rendered in their own row
      for column_key in @get_remarks_columns()
        column = @props.columns[column_key]
        # support rowspanning for WS header slot
        skip = item.skip or []
        colspan = @props.column_count - skip.length
        rows.push(
          <TableRemarksRow
            {...@props}
            key={uid + column_key}
            item={item}
            item_key={column_key}
            expanded={expanded}
            selected={selected}
            disabled={disabled}
            className={css + " remarksrow"}
            colspan={colspan}
            className={css}
            />)

      # append expanded rows
      if expanded
        # use the global children mapping to get the lazy fetched folderitem
        children = @get_children item
        if children.length > 0
          child_rows = @build_rows folderitems: children
          rows = rows.concat child_rows

    return rows

  render: ->
    return @render_categorized_rows()


export default TableRows
