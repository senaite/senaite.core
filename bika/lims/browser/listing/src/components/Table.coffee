import React from "react"
import TableHeaderRow from "./TableHeaderRow.coffee"
import TableRows from "./TableRows.coffee"


class Table extends React.Component

  constructor: (props) ->
    super(props)
    # Bind event handler to local context
    @on_select_checkbox_checked = @on_select_checkbox_checked.bind @

  on_select_checkbox_checked: (event) ->
    el = event.currentTarget
    uid = el.value
    checked = el.checked

    # notify parent event handler with the extracted values
    if @props.on_select_checkbox_checked
      # @param {string} uid: UID of the selected folderitem
      # @param {boolean} checked: true/false depending on the select status
      @props.on_select_checkbox_checked uid, checked

  render: ->
    <table id={@props.id}
           className={@props.className}>
      <thead>
        <TableHeaderRow
          {...@props}
          on_select_checkbox_checked={@on_select_checkbox_checked}
          />
        </thead>
      <tbody>
        <TableRows
          {...@props}
          on_select_checkbox_checked={@on_select_checkbox_checked}
          />
      </tbody>
    </table>


export default Table
