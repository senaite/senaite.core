import React from "react"


class MultiSelect extends React.Component

  constructor: (props) ->
    super(props)
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  on_blur: (event) ->
    el = event.currentTarget
    checked = el.checked
    console.debug "MultiSelect::on_blur: value=#{checked}"

    # propagate event
    if @props.onBlur then @props.onBlur event

  on_change: (event) ->
    el = event.currentTarget
    checked = el.checked
    console.debug "MultiSelect::on_change: value=#{checked}"

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
      selected = option.selected or no
      options.push(
        <li key={value}>
          <input type="checkbox"
                 defaultChecked={selected}
                 uid={@props.uid}
                 name={@props.name}
                 value={value}
                 onChange={@on_change}
                 onBlur={@on_blur}
                 column_key={@props.column_key}
                 {...@props.attrs}/> {title}
        </li>
      )

    return options
  render: ->
    <div className="multiselect">
      <ul className="list-unstyled">
        {@build_options()}
      </ul>
    </div>


export default MultiSelect
