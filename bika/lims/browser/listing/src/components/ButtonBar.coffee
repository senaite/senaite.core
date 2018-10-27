import React from "react"

import Button from "./Button.coffee"


class ButtonBar extends React.Component
  ###
   * The button bar component renders the workflow and custom transitions buttons
  ###


  constructor: (props) ->
    super(props)
    @handle_button_click = @handle_button_click.bind @

    @css_mapping =
      "activate": "btn-success"
      "cancel": "btn-warning"
      "deactivate": "btn-danger"
      "default": "btn-default"
      "invalidate": "btn-danger"
      "prepublish": "btn-info"
      "publish": "btn-success"
      "receive": "btn-primary"
      "republish": "btn-info"
      "retract": "btn-danger"

  get_button_css: (id) ->
    ###
     * Get the CSS classes for the button for the given transition id
    ###

    # calculate the button CSS
    cls = "btn btn-default btn-sm"

    additional_cls = @css_mapping[id]
    if additional_cls
      cls += " #{additional_cls}"

    return cls

  handle_button_click: (event) ->
    ###
     * Event handler when a button was clicked
    ###

    # prevent form submit, because we want to handle that explicitly
    event.preventDefault()

    # extract the action ID
    el = event.currentTarget
    id = el.id

    @props.onClick id

  build_buttons: ->
    ###
     * Build the buttons for the selected items in the current state
    ###
    buttons = []

    # Always insert a clear selection button first
    if @props.transitions.length > 0
      buttons.push(
        <li key="clear">
          <button className="btn btn-default btn-sm"
                  onClick={@handle_button_click}
                  id="clear_selection">
            <span className="glyphicon glyphicon-ban-circle"></span>
          </button>
        </li>
      )

    # build the transition buttons
    for transition in @props.transitions

      id = transition.id
      title = transition.title
      cls = @get_button_css id

      buttons.push(
        <li key={transition.id}>
          <Button
            id={id}
            title={title}
            className={cls}
            badge={@props.selected_uids.length}
            onClick={@handle_button_click}/>
        </li>
      )

    return buttons

  render: ->
    if @props.selected_uids.length == 0
      return null

    <ul className={@props.className}>
      {@build_buttons()}
    </ul>


export default ButtonBar
