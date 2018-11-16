import React from "react"


class HiddenField extends React.Component
  ###
   * The hidden field component renders a hidden field
  ###

  constructor: (props) ->
    super(props)

  render: ->
    <input type="hidden"
           name={@props.name}
           item_key={@props.item_key}
           value={@props.value}
           className={@props.className} />


export default HiddenField
