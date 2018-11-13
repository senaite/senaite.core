import React from "react"


class Select extends React.Component
  ###
   * The select component renders a single select field
  ###

  constructor: (props) ->
    super(props)

    # remember the initial value
    @value = props.defaultValue or ""
    @changed = no

    # bind event handler to the current context
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  on_blur: (event) ->
    ###
     * Event handler when the input for blur event
    ###
    el = event.currentTarget
    value = el.value

    # Only propagate for new values
    if not @changed
      return

    # reset the change flag
    @changed = no

    console.debug "Select::on_blur: value=#{value}"

    # propagate event
    if @props.onBlur then @props.onBlur event

  on_change: (event) ->
    ###
     * Event handler when the selection changed
    ###
    el = event.currentTarget
    value = el.value

    # Only propagate for new values
    if value == @value
      return

    console.debug "Select::on_change: value=#{value}"

    # store the new value
    @value = value

    # set the change flag
    @changed = yes

    # propagate event to the parent event handler
    if @props.onChange then @props.onChange event

  build_options: ->
    ###
     * Build the select options from the given options
    ###
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
