import React from "react"


class NumericField extends React.Component

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

    console.debug "NumericField::on_blur: value=#{value}"

    # propagate event
    if @props.onBlur then @props.onBlur event

  on_change: (event) ->
    el = event.currentTarget
    value = el.value

    if /[^-.\d]/g.test value
      el.value = value.replace /[^.\d]/g, ""

    # Only propagate for new values
    if value == @value
      return

    console.debug "NumericField::on_change: value=#{value}"

    # store the new value
    @value = value

    # set the change flag
    @changed = yes

    # propagate event
    if @props.onChange then @props.onChange event

  render: ->
    <span className="form-group">
      {@props.before and <span dangerouslySetInnerHTML={{__html: @props.before}}></span>}
      <input type="text"
            size={@props.size or 5}
            uid={@props.uid}
            name={@props.name}
            defaultValue={@props.defaultValue or ""}
            column_key={@props.column_key}
            title={@props.title}
            disabled={@props.disabled}
            required={@props.required}
            className={@props.className}
            placeholder={@props.placeholder}
            onBlur={@on_blur}
            onChange={@on_change}/>
      {@props.after and <span dangerouslySetInnerHTML={{__html: @props.after}}></span>}
    </span>


export default NumericField
