import React from "react"
import Button from "./Button.coffee"


class FilterBar extends React.Component

  constructor: (props) ->
    super(props)
    @state =
      active: props.review_state or "default"
    @handleClick = @handleClick.bind @

  handleClick: (event) ->
    el = event.currentTarget
    id = el.id
    console.info "Button #{id} clicked..."
    @setState
      active: id
    @props.onClick id

  buildButtons: ->
    buttons = []

    for key, value of @props.review_states
      cls = "btn btn-default btn-sm"

      if (value.id == @state.active)
        cls += " active"

      buttons.push(
        <li key={value.id}>
          <Button onClick={this.handleClick}
                  id={value.id}
                  title={value.title}
                  className={cls}/>
        </li>
      )

    return buttons

  render: ->
    <ul className={@props.className}>
      {@buildButtons()}
    </ul>


export default FilterBar
