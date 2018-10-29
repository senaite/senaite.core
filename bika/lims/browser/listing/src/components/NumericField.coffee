import React from "react"


class NumericField extends React.Component
  ###
   * The numeric field component renders a field where only numbers are allowed
  ###

  constructor: (props) ->
    super(props)
    # bind event handler to the current context
    @on_change = @on_change.bind @

    @allowed_keys = [
      8,    # backspace
      9,    # tab
      13,   # enter
      35,   # end
      36,   # home
      37,   # left arrow
      39,   # right arrow
      46,   # delete - We don't support the del key in Opera because del == . == 46.
      44,   # ,
      60,   # <
      62,   # >
      45,   # -
      69,   # E
      101,  # e,
      61    # =
    ]

  on_change: (event) ->
    ###
     * Event handler when the input changed
    ###
    el = event.currentTarget
    value = el.value
    console.debug "NumericField::on_change: value=#{value}"

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

    field.push(
      <input key="field"
             type="text"
             name={@props.name}
             defaultValue={@props.defaultValue}
             title={@props.title}
             size={@props.size or "5"}
             disabled={@props.disabled}
             className={@props.className}
             placeholder={@props.placeholder}
             onChange={@on_change} />
    )

    return field

  render: ->
    @render_field()


export default NumericField
