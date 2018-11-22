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
        return <span className="glyphicon glyphicon-remove"></span>
    else
      return (
        <span className={@props.className}
              dangerouslySetInnerHTML={{__html: @props.formatted_value}}>
        </span>
      )


export default ReadonlyField
