import React from "react"


class TableRemarksRow extends React.Component
  ###
   * The table remarks row component renders Remarks for Analyses, Duplicate
   * Analyses and Reference Analyses
  ###

  constructor: (props) ->
    super(props)
    @types_with_remarks = ["Analysis", "DuplicateAnalysis", "ReferenceAnalysis"]

  has_remarks: ->
    ###
     * Checks if the remarks field exists
    ###
    item = @props.item
    if item.portal_type not in @types_with_remarks
      return no
    if not item.Remarks
      return no
    return yes

  can_edit: ->
    ###
     * Checks if the Remarks field is in the list of editable fields
    ###
    item = @props.item
    allow_edit = item.allow_edit or []
    return "Remarks" in allow_edit

  render_remarks_field: ->
    ###
     * Render the remarks field
    ###
    item = @props.item
    uid = item.uid
    name = "Remarks.#{uid}:records"
    value = item.Remarks
    display = if @has_remarks() then "block" else "none"
    style =
      display: @has_remarks() and "block" or "none"
      paddingTop: ".5em"
      paddingBottom: ".5em"
      paddingLeft: "2em"

    if not @can_edit()
      field = (
        <span className=""
              dangerouslySetInnerHTML={{__html: item.Remarks}}/>
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
