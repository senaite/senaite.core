import React from "react"


class Button extends React.Component
  ###
   * The button component renders a single button
  ###

  render: ->
    ###
     * Render the Button component
    ###
    <button id={@props.id}
            name={@props.name}
            url={@props.url}
            onClick={@props.onClick}
            className={@props.className}
            {...@props.attrs}>
      <span dangerouslySetInnerHTML={{__html: @props.title}}></span>
      {@props.badge and
        <span className="badge"
              style={{marginLeft: "0.25em"}}>
          {@props.badge}
        </span>
      }
    </button>


export default Button
