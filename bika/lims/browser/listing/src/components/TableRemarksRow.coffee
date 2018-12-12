import React from "react"
import RemarksField from "./RemarksField.coffee"


class TableRemarksRow extends React.Component

  constructor: (props) ->
    super(props)

  render: ->
    <tr className={@props.className}>
      <td style={{padding: 0; borderTop: 0}}></td>
      <td style={{padding: 0; borderTop: 0}}
          colSpan={@props.colspan - 1}>
        <RemarksField {...@props} />
      </td>
    </tr>

export default TableRemarksRow
