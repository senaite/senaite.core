import React from "react"


class CalculatedField extends React.Component

  ###*
   * Calculated Field for the Listing Table
   *
   * Basically like a *disabled* numeric field, but with a controlled value
   *
  ###
  constructor: (props) ->
    super(props)
  render: ->
    <span className="form-group">
      {@props.before and <span className="before_field" dangerouslySetInnerHTML={{__html: @props.before}}></span>}
      <input type="text"
             size={@props.size or 5}
             uid={@props.uid}
             name={@props.name}
             value={@props.value or ""}
             column_key={@props.column_key}
             title={@props.title}
             disabled={yes}
             required={@props.required}
             className={@props.className}
             placeholder={@props.placeholder}
             {...@props.attrs}/>
      {@props.after and <span className="after_field" dangerouslySetInnerHTML={{__html: @props.after}}></span>}
    </span>


export default CalculatedField
