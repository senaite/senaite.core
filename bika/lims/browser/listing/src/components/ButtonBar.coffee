import React from "react"
import Button from "./Button.coffee"


class ButtonBar extends React.Component

  constructor: (props) ->
    super(props)
    @handleClick = @handleClick.bind @

  handleClick: (event) ->
    el = event.currentTarget
    id = el.id
    console.info "Button #{id} clicked..."
    @props.onClick id

  buildButtons: ->
    buttons = []

    # Insert a clear button
    if @props.transitions.length > 0
      buttons.push(
        <li key="clear">
          <button className="btn btn-default btn-sm"
                  onClick={@handleClick}
                  id="clear_selection">
            <span className="glyphicon glyphicon-ban-circle"></span>
          </button>
        </li>
      )

    for transition in @props.transitions
      buttons.push(
        <li key={transition.id}>
          <Button className="btn btn-default btn-sm"
                  onClick={@handleClick}
                  id={transition.id}
                  badge={@props.selected_uids.length}
                  title={transition.title}/>
        </li>
      )

    return buttons

  render: ->
    if @props.selected_uids.length == 0
      return null

    <ul className={@props.className}>
      {@buildButtons()}
    </ul>


export default ButtonBar
