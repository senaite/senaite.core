import React from "react"


class TableRemarksRow extends React.Component
  ###
   * The table remarks row component renders a textarea below the parent row
  ###

  constructor: (props) ->
    super(props)

  can_edit: ->
    ###
     * Checks if the Remarks field is in the list of editable fields
    ###
    item = @props.item
    item_key = @props.item_key
    allow_edit = item.allow_edit or []
    return item_key in allow_edit

  render_remarks_field: ->
    ###
     * Render the remarks field
    ###
    item = @props.item
    uid = item.uid
    item_key = @props.item_key
    name = "#{item_key}.#{uid}:records"
    value = item[item_key] or ""
    # show the remarks if the row is selected or if a value was set
    show = @props.selected or value.length > 0

    style =
      display: if show then "block" else "none"
      paddingTop: ".5em"
      paddingBottom: ".5em"
      paddingLeft: "2em"

    if not @can_edit()
      field = (
        <span className=""
              dangerouslySetInnerHTML={{__html: value}}/>
      )
    else
      field = (
        <textarea
          className="form-control"
          style={{width: "100%"}}
          rows="2"
          name={name}
          defaultValue={value}>
        </textarea>
      )

    return (
      <div key={item.uid}
           style={style}
           className="remarks-placeholder">
        <div className="">
          {@props.remarks_row_title or "Remarks"}:
        </div>
        {field}
      </div>
    )

  render: ->
    <tr className={@props.className}>
      <td className="remarks text-muted"
          colSpan={@props.column_count}
          style={{padding: 0; borderTop: 0}}>
        {@render_remarks_field()}
      </td>
    </tr>

export default TableRemarksRow
