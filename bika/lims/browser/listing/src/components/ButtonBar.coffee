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

  buildCustomTransitions: ->
    buttons = []

    review_state_item = @props.review_state_item
    custom_transitions = review_state_item.custom_transitions or []

    for key, value of custom_transitions
      cls = "btn btn-default btn-sm"
      buttons.push(
        <li key={value.id}>
          <Button onClick={@handleClick}
                  action={value.url}
                  id={value.id}
                  title={value.title}
                  className={cls}/>
        </li>
      )

    return buttons

  render: ->
    <ul className={@props.className}>
      {@buildCustomTransitions()}
    </ul>


export default ButtonBar
