import React from "react"


class Button extends React.Component
  ###
   * Button component usable for the listing
  ###

  render: ->
    ###
     * Render the Button component
    ###
    <button id={@props.id}
            name={@props.name}
            onClick={@props.onClick}
            className={@props.className}>
      <span dangerouslySetInnerHTML={{__html: @props.title}}></span>
      {@props.badge and
        <span className="badge"
              style={{marginLeft: "0.25em"}}>
          {@props.badge}
        </span>
      }
    </button>


export default Button
