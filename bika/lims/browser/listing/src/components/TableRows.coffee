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

  get_remarks_columns: (item) ->
    columns = []
    for key, value of @props.columns
      if value.type == "remarks"
        # skip undefined values (e.g. reassignable slots)
        if item[key] is undefined
          continue
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
        # concatenate the categorized rows in the right order
        rows = rows.concat @build_rows
          props: {category: category}
    # Render uncatgorized rows
    else
      rows = @build_rows()

    return rows

  build_rows: ({props}={}) ->
    rows = []

    props ?= {}
    category = props.category or null
    folderitems = props.folderitems or @props.folderitems

    for item, item_index in folderitems

      # skip items of other categories
      if category and @get_item_category(item) != category
        continue

      # skip items in collapsed categories except the selected ones
      if category and not @is_category_expanded category
        if not @is_selected item
          continue

      uid = @get_item_uid item
      css = @get_item_css item

      # list of child UIDs in the folderitem
      children = @get_item_children item

      expanded = @is_expanded item
      selected = @is_selected item
      disabled = @is_item_disabled item
      expandable = @has_item_children item
      remarks_columns = @get_remarks_columns item
      transposed = no

      # transposed items have no uid, so use the index instead
      if uid is null
        transposed = yes
        uid = item_index

      rows.push(
        <TableRow
          {...@props}
          key={uid}
          item={item}
          uid={uid}
          category={category}
          expanded={expanded}
          remarks={remarks_columns.length > 0}
          selected={selected}
          disabled={disabled}
          className={css}
          onClick={expandable and @on_row_expand_click or undefined}
          />)

      # columns with type="remarks" set are rendered in their own row
      for column_key, column_index in remarks_columns
        # skip for transposed cells
        break if transposed
        column = @props.columns[column_key]
        # support rowspanning for WS header slot
        skip = item.skip or []
        colspan = @props.column_count - skip.length
        # get the remarks value
        value = item[column_key] or ""
        rows.push(
          <TableRemarksRow
            {...@props}
            key={"remarks_" + item_index}
            uid={uid}
            item={item}
            column_key={column_key}
            value={value}
            expanded={expanded}
            selected={selected}
            disabled={disabled}
            className={css + " remarksrow"}
            colspan={colspan}
            />)

      # append expanded rows
      if expanded
        # use the global children mapping to get the lazy fetched folderitem
        children = @get_children item
        if children.length > 0
          child_rows = @build_rows
            props:
              category: category
              folderitems: children
          rows = rows.concat child_rows

    return rows

  render: ->
    return @render_categorized_rows()


export default TableRows
