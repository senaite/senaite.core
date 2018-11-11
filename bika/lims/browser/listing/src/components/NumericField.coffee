import React from "react"


class NumericField extends React.Component
  ###
   * The numeric field component renders a field where only numbers are allowed
  ###

  constructor: (props) ->
    super(props)
    # bind event handler to the current context
    @on_change = @on_change.bind @
    @on_keypress = @on_keypress.bind @

  on_change: (event) ->
    ###
     * Event handler when the input changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "NumericField::on_change: value=#{value}"

    if /[^-.\d]/g.test value
      el.value = value.replace /[^.\d]/g, ""

    # propagate event
    if @props.onChange then @props.onChange event

  on_keypress: (event) ->
    ###
     * Event handler when a key was pressed
    ###
    key = event.key
    console.debug "NumericField::on_keypress: key=#{key}"

  render: ->
    <input type="text"
           name={@props.name}
           defaultValue={@props.defaultValue}
           title={@props.title}
           disabled={@props.disabled}
           className={@props.className}
           placeholder={@props.placeholder}
           onKeyPress={@on_keypress}
           onChange={@on_change} />


export default NumericField
