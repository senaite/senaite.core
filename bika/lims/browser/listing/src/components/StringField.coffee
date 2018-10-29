import React from "react"


class StringField extends React.Component
  ###
   * The numeric field component renders a field where only numbers are allowed
  ###

  constructor: (props) ->
    super(props)
    # bind event handler to the current context
    @on_change = @on_change.bind @

  on_change: (event) ->
    ###
     * Event handler when the input changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "StringField::on_change: value=#{value}"

    # propagate event
    if @props.onChange then @props.onChange event

  render: ->
    <input type="text"
           name={@props.name}
           defaultValue={@props.value}
           disabled={@props.disabled}
           className={@props.className or "form-control input-sm"}
           placeholder={@props.placeholder}
           onChange={@on_change} />


export default StringField
