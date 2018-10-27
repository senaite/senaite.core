import React from "react"


class Checkbox extends React.Component
  ###
   * The checkbox component renders a single checkbox
  ###

  constructor: (props) ->
    super(props)

  render: ->
    <input type="checkbox"
           name={@props.name}
           value={@props.value}
           checked={@props.checked}
           onChange={@props.onChange}/>


export default Checkbox
