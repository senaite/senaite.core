import React from "react"


class Checkbox extends React.Component
  ###
   * The checkbox component renders a single checkbox
  ###

  constructor: (props) ->
    super(props)
    # bind event handler to the current context
    @on_change = @on_change.bind @

  on_change: (event) ->
    ###
     * Event handler when the checkbox changed
    ###
    el = event.currentTarget
    checked = el.checked
    console.debug "Checkbox::on_change: checked=#{checked}"

    # propagate event
    if @props.onChange then @props.onChange event

  render: ->
    <input key={@props.name}
           type="checkbox"
           name={@props.name}
           item_key={@props.item_key}
           title={@props.title}
           disabled={@props.disabled}
           checked={@props.checked}
           defaultChecked={@props.defaultChecked}
           value={@props.value}
           className={@props.className}
           onChange={@on_change}/>


export default Checkbox
