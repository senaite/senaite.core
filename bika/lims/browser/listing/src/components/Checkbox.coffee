import React from "react"


class Checkbox extends React.Component

  constructor: (props) ->
    super(props)
    @onSelect = @onSelect.bind @

  onSelect: (event) ->
    event.preventDefault()
    el = event.currentTarget
    el.value
    # propagate change event to parent component
    @props.onSelect event

  render: ->
    <input type="checkbox"
           name={@props.name}
           checked={@props.checked}
           onChange={@onSelect}
           value={@props.value}/>


export default Checkbox
