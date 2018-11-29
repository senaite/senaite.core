import React from "react"


class TableRemarksRow extends React.Component

  constructor: (props) ->
    super(props)
    # Bind events
    @on_remarks_field_blur = @on_remarks_field_blur.bind @

  on_remarks_field_blur: (event) ->
    el = event.currentTarget
    uid = el.getAttribute("uid")
    name = el.getAttribute("column_key") or el.name
    value = el.value
    console.debug "TableCell:on_remarks_field_blur: value=#{value}"

    # Call the *save* field handler
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @props.item

  can_edit: ->
    item = @props.item
    column_key = @props.column_key
    allow_edit = item.allow_edit or []
    return column_key in allow_edit

  get_column_title: ->
    columns = @props.columns
    column_key = @props.column_key
    column = columns[column_key]
    title = column.title
    if (typeof _ == "function") then title = _(title)
    return title or ""

  render_remarks_field: ->
    item = @props.item
    uid = item.uid
    column_key = @props.column_key
    name = "#{column_key}.#{uid}:records"
    value = item[column_key] or ""
    # show the remarks if the row is selected or if a value was set
    show = @props.selected or value.length > 0

    style =
      display: if show then "block" else "none"

    if not @can_edit()
      field = (
        <span className=""
              dangerouslySetInnerHTML={{__html: value}}/>)
    else
      field = (
        <textarea
          className="form-control"
          uid={@props.uid}
          column_key={@props.column_key}
          style={{width: "100%"}}
          rows="2"
          name={name}
          onBlur={@on_remarks_field_blur}
          defaultValue={value}>
        </textarea>)

    return (
      <div key={item.uid}
           style={style}
           className="remarks text-muted">
        <div className="text-info">
          <span className="glyphicon glyphicon-hand-right"/> {@get_column_title()}:
        </div>
        {field}
      </div>)

  render: ->
    <tr className={@props.className}>
      <td style={{padding: 0; borderTop: 0}}></td>
      <td style={{padding: 0; borderTop: 0}}
          colSpan={@props.colspan - 1}>
        {@render_remarks_field()}
      </td>
    </tr>

export default TableRemarksRow
