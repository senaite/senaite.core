import React from "react"


class Select extends React.Component
  ###
   * The select component renders a single select field
  ###

  constructor: (props) ->
    super(props)

  on_select: (event) ->
    ###
     * Event handler when the selection changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "Selection changed to #{value}"

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
    <select value={@props.value}
            onChange={@on_select}
            name={@props.name}
            className={@props.className}>
      {@build_options()}
    </select>


export default Select
