import React from "react"


class HiddenField extends React.Component
  ###
   * The hidden field component renders a hidden field
  ###

  constructor: (props) ->
    super(props)

  render: ->
    <input type="hidden"
           uid={@props.uid}
           name={@props.name}
           value={@props.value}
           column_key={@props.column_key}
           className={@props.className} />


export default HiddenField
