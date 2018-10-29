import React from "react"


class Checkbox extends React.Component
  ###
   * The checkbox component renders a single checkbox
  ###

  constructor: (props) ->
    super(props)
    # bind event handler to the current context
    @on_change = @on_change.bind @

  on_change: (event) ->
    ###
     * Event handler when the checkbox changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "Checkbox::on_change: value=#{value}"

    # propagate event
    if @props.onChange then @props.onChange event

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
      <input key="field"
             type="checkbox"
             name={@props.name}
             value={@props.value}
             title={@props.title}
             disabled={@props.disabled}
             checked={@props.checked}
             defaultChecked={@props.defaultChecked}
             className={@props.className}
             onChange={@on_change}/>
    )

    return field

  render: ->
    @render_field()


export default Checkbox
