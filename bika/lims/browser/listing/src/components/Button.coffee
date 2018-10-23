import React from "react"


class Button extends React.Component

  render: ->
    ###
     * Render the Button component
    ###
    <button id={@props.id}
            dangerouslySetInnerHTML={{__html: @props.title}}
            onClick={@props.onClick}
            className={@props.className}>
    </button>


export default Button
