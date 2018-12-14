import React from "react"


class ReadonlyField extends React.Component

  constructor: (props) ->
    super(props)

  is_boolean_field: ->
    if typeof(@props.value) == "boolean"
      return yes
    return no

  render: ->
    if @is_boolean_field()
      if @props.value
        return <span className="glyphicon glyphicon-ok"></span>
      else
        return <span className="glyphicon glyphicon-minus"></span>
    else
      return (
        <span className={@props.className}>
          {@props.before and <span className="before_field" dangerouslySetInnerHTML={{__html: @props.before}}></span>}
          <span dangerouslySetInnerHTML={{__html: @props.formatted_value}} {...@props.attrs}></span>
          {@props.after and <span className="after_field" dangerouslySetInnerHTML={{__html: @props.after}}></span>}
        </span>
      )


export default ReadonlyField
