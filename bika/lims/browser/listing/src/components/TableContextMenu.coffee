import React from "react"


class TableContextMenu extends React.Component
  ###
   * Table column toggle context menu
  ###

  constructor: (props) ->
    super(props)
    @on_toggle_click = @on_toggle_click.bind @
    @on_mouse_leave = @on_mouse_leave.bind @

  on_mouse_leave: (event) ->
    @props.on_context_menu 0, 0, no

  on_toggle_click: (event) ->
    ###
     * Event handler when a column toggle was clicked
    ###
    event.preventDefault()
    el = event.currentTarget
    column_key = el.getAttribute "column"
    column_toggle = column_key in @props.table_columns

    console.log "TableContextMenu::on_toggle_click: column=#{column_key} column_toggle=#{column_toggle}"
    @props.on_column_toggle column_key

  get_style: ->
    ###
     * Calculate the style
    ###
    x = @props.x - 85  # half of the width - half of the padding - one border
    y = @props.y

    show = @props.show or no
    display = if show then "block" else "none"

    style =
      position: "absolute"
      display: display
      top: "#{y}px"
      left: "#{x}px"
      width: "200px"

    return style

  render_toggle_columns: ->
    ###
     * Render the toggle columns menu
    ###
    toggle_columns = []

    for key in @props.column_order
      toggle = key in @props.table_columns
      column = @props.columns[key]
      title = column.title or key

      cls = "text-primary"
      sel_cls = "glyphicon glyphicon-ok"
      if not toggle
        cls = "text-muted"
        sel_cls = "glyphicon glyphicon-minus"

      toggle_columns.push(
        <li key={key}>
          <a href="#" className={cls} column={key} onClick={@on_toggle_click}>
            <span className={sel_cls}></span> {title}
          </a>
        </li>
      )

    toggle_columns.push(
      <li key="default">
        <hr/>
        <a href="#" onClick={@on_toggle_click} column="reset">
          <span className="glyphicon glyphicon-repeat"></span>
          <strong> {@props.reset_title or "Reset"}</strong>
        </a>
      </li>
    )

    return toggle_columns

  render: ->
    if not @props.show
      return null

    <div className="popover bottom"
         onMouseLeave={@on_mouse_leave}
         style={@get_style()}>
      <div className="arrow"></div>
      <h3 className="popover-title">
        {@props.title}
      </h3>
      <div className="popover-content">
        <ul className="list-unstyled">
          {@render_toggle_columns()}
        </ul>
      </div>
    </div>


export default TableContextMenu
