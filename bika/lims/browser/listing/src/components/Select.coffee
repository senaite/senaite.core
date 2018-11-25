import React from "react"


class Select extends React.Component

  constructor: (props) ->
    super(props)
    # remember the initial value
    @value = props.defaultValue or ""
    # bind event handler to the current context
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  on_blur: (event) ->
    el = event.currentTarget
    value = el.value
    console.debug "Select::on_blur: value=#{value}"
    # propagate event
    if @props.onBlur then @props.onBlur event

  on_change: (event) ->
    el = event.currentTarget
    value = el.value
    # Only propagate for new values
    if value == @value
      return
    console.debug "Select::on_change: value=#{value}"
    # store the new value
    @value = value
    # propagate event to the parent event handler
    if @props.onChange then @props.onChange event

  build_options: ->
    options = []

    sorted_options = @props.options.sort (a, b) ->
      text_a = a.ResultText
      text_b = b.ResultText
      if text_a > text_b then return 1
      if text_a < text_b then return -1
      return 0

    for option in sorted_options
      value = option.ResultValue
      title = option.ResultText
      options.push(
        <option key={value}
                value={value}>
          {title}
        </option>
      )

    return options

  render: ->
    <select key={@props.name}
            name={@props.name}
            item_key={@props.item_key}
            defaultValue={@props.defaultValue}
            title={@props.title}
            disabled={@props.disabled}
            onBlur={@on_blur}
            onChange={@on_change}
            required={@props.required}
            className={@props.className}>
      {@build_options()}
    </select>


export default Select
