import React from "react"


class TableRemarksRow extends React.Component

  constructor: (props) ->
    super(props)

  can_edit: ->
    item = @props.item
    item_key = @props.item_key
    allow_edit = item.allow_edit or []
    return item_key in allow_edit

  get_column_title: ->
    columns = @props.columns
    item_key = @props.item_key
    column = columns[item_key]
    title = column.title
    if (typeof _ == "function") then title = _(title)
    return title or ""

  render_remarks_field: ->
    item = @props.item
    uid = item.uid
    item_key = @props.item_key
    name = "#{item_key}.#{uid}:records"
    value = item[item_key] or ""
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
          style={{width: "100%"}}
          rows="2"
          name={name}
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
