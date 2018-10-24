import React from "react"
import TableRow from "./TableRow.coffee"
import TableHeaderRow from "./TableHeaderRow.coffee"


class Table extends React.Component

  constructor: (props) ->
    super(props)
    @onSelect = @onSelect.bind @

  onSelect: (event) ->
    ###
     * Event handler when row was selected over the select checkbox
    ###
    el = event.currentTarget
    uid = el.value
    checked = el.checked
    @props.onSelect uid, checked

  buildFolderItems: ->
    rows = []

    for index, item of @props.folderitems
      rows.push(
        <TableRow className={item.state_class}
                  onSelect={@onSelect}
                  key={index}
                  item={item}
                  review_states={this.props.review_states}
                  selected_uids={@props.selected_uids}
                  columns={this.props.columns}/>
      )
    return rows

  render: ->
    <table id={@props.id}
            className={@props.className}>
      <thead>
        <TableHeaderRow sort_on={this.props.sort_on}
                        onSelect={@onSelect}
                        sort_order={this.props.sort_order}
                        onSort={this.props.onSort}
                        columns={this.props.columns}/>
      </thead>
      <tbody>
        {@buildFolderItems()}
      </tbody>
      <tfoot>
      </tfoot>
    </table>


export default Table
