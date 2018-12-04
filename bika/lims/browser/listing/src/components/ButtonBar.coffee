import React from "react"

import Button from "./Button.coffee"


class ButtonBar extends React.Component

  constructor: (props) ->
    super(props)

    # Bind eventhandlers to local context
    @on_ajax_save_button_click = @on_ajax_save_button_click.bind @
    @on_transition_button_click = @on_transition_button_click.bind @

    @css_mapping =
      # default buttons
      "reassign": "btn-default"
      # blue buttons
      "assign": "btn-default"
      "receive": "btn-primary"
      # green buttons
      "activate": "btn-success"
      "prepublish": "btn-success"
      "publish": "btn-success"
      "republish": "btn-success"
      "submit": "btn-success"
      # orange buttons
      "unassign": "btn-warning"
      # red buttons
      "cancel": "btn-danger"
      "deactivate": "btn-danger"
      "invalidate": "btn-danger"
      "reject": "btn-danger"
      "retract": "btn-danger"

  get_button_css: (id) ->
    # calculate the button CSS
    cls = "btn btn-default btn-sm"

    # append additional button styles
    additional_cls = @css_mapping[id]
    if additional_cls
      cls += " #{additional_cls}"

    return cls

  on_ajax_save_button_click: (event) ->
    # prevent form submit, because we want to handle that explicitly
    event.preventDefault()

    # call the parent event handler to save
    if @props.on_ajax_save_button_click
      @props.on_ajax_save_button_click()

  on_transition_button_click: (event) ->
    # prevent form submit, because we want to handle that explicitly
    event.preventDefault()

    # extract the action ID
    el = event.currentTarget

    # extract the transition action and the url of the button
    action = el.getAttribute "id"
    url = el.getAttribute "url"

    # call the parent event handler to perform the transition
    if @props.on_transition_button_click
      @props.on_transition_button_click action, url

  build_buttons: ->
    buttons = []

    # Add a clear button if the select column is rendered
    if @props.show_select_column
      if @props.transitions.length > 0
        buttons.push(
          <li key="clear">
            <button className="btn btn-default btn-sm"
                    onClick={@on_transition_button_click}
                    id="clear_selection">
              <span className="glyphicon glyphicon-ban-circle"></span>
            </button>
          </li>)

    # Add an Ajax save button
    if @props.show_ajax_save
      buttons.push(
        <li key="ajax-save">
          <button className="btn btn-primary btn-sm"
                  onClick={@on_ajax_save_button_click}
                  title={@props.ajax_save_button_title}
                  id="ajax_save_selection">
            {@props.ajax_save_button_title} <span className="glyphicon glyphicon-floppy-open"></span>
          </button>
        </li>)

    # build the transition buttons
    for transition in @props.transitions

      id = transition.id
      url = transition.url
      title = transition.title
      cls = @get_button_css id
      btn_id = "#{id}_transition"

      buttons.push(
        <li key={transition.id}>
          <Button
            id={btn_id}
            title={title}
            url={url}
            className={cls}
            badge={@props.selected_uids.length}
            onClick={@on_transition_button_click}/>
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
