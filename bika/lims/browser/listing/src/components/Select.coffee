import React from "react"


class Select extends React.Component
  ###
   * The select component renders a single select field
  ###

  constructor: (props) ->
    super(props)
    # bind event handler to the current context
    @on_change = @on_change.bind @

  on_change: (event) ->
    ###
     * Event handler when the selection changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "Select::on_change: value=#{value}"

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

  render_field: ->
    ###
     * Render the field
    ###
    field = []

    if @props.disabled
      field.push (
        <input key="field_hidden"
               type="hidden"
               name={@props.name}
               value={@props.value}/>
      )

    field.push (
      <select key="field"
              name={@props.name}
              value={@props.value}
              title={@props.title}
              disabled={@props.disabled}
              onChange={@on_change}
              className={@props.className}>
        {@build_options()}
      </select>
    )

    return field

  render: ->
    @render_field()


export default Select
