import React from "react"
import Button from "./Button.coffee"


class ButtonBar extends React.Component

  constructor: (props) ->
    super(props)
    @handleClick = @handleClick.bind @
    @transition_button_class =
      "cancel": "btn-warning"
      "invalidate": "btn-danger"
      "retract": "btn-danger"
      "deactivate": "btn-danger"
      "republish": "btn-info"
      "prepublish": "btn-info"
      "receive": "btn-primary"
      "publish": "btn-success"

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
      cls = "btn btn-default btn-sm"
      additional_cls = @transition_button_class[transition.id]
      if additional_cls
        cls += " #{additional_cls}"
      buttons.push(
        <li key={transition.id}>
          <Button className={cls}
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
