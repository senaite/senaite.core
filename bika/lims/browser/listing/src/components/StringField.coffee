import React from "react"


class StringField extends React.Component

  constructor: (props) ->
    super(props)

    # remember the initial value
    @value = props.defaultValue or ""
    @changed = no

    # bind event handler to the current context
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  on_blur: (event) ->
    el = event.currentTarget
    value = el.value

    # Only propagate for new values
    if not @changed
      return

    # reset the change flag
    @changed = no

    console.debug "StringField::on_blur: value=#{value}"

    # propagate event
    if @props.onBlur then @props.onBlur event

  on_change: (event) ->
    el = event.currentTarget
    value = el.value

    # Only propagate for new values
    if value == @value
      return

    console.debug "StringField::on_change: value=#{value}"

    # store the new value
    @value = value

    # set the change flag
    @changed = yes

    # propagate event
    if @props.onChange then @props.onChange event

  render: ->
    <input type="text"
           uid={@props.uid}
           name={@props.name}
           defaultValue={@props.value}
           column_key={@props.column_key}
           disabled={@props.disabled}
           className={@props.className or "form-control input-sm"}
           placeholder={@props.placeholder}
           onBlur={@on_blur}
           onChange={@on_change}
           {...@props.attrs}/>


export default StringField
