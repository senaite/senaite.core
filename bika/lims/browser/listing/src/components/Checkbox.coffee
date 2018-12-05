import React from "react"


class Checkbox extends React.Component

  constructor: (props) ->
    super(props)
    # bind event handler to the current context
    @on_change = @on_change.bind @

  on_change: (event) ->
    el = event.currentTarget
    checked = el.checked
    console.debug "Checkbox::on_change: checked=#{checked}"

    # propagate event
    if @props.onChange then @props.onChange event

  render: ->
    field = []
    field.push (
      <input key={@props.name}
             type="checkbox"
             uid={@props.uid}
             name={@props.name}
             value={@props.value}
             column_key={@props.column_key}
             title={@props.title}
             disabled={@props.disabled}
             checked={@props.checked}
             defaultChecked={@props.defaultChecked}
             className={@props.className}
             onChange={@on_change}/>)
    if @props.render_hidden
      field.push(
        <input key={@props.name + "_hidden"}
               type="hidden"
               name={@props.name}
               value={@props.value}/>)
    return field


export default Checkbox
