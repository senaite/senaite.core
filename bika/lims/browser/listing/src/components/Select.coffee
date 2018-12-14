import React from "react"


class Select extends React.Component

  ###*
   * Select Field for the Listing Table
   *
   * A select field is identified by the column type "choices" in the listing
   * view, e.g.  `self.columns = {"Result": {"type": "choices"}, ... }`
   *
  ###
  constructor: (props) ->
    super(props)
    # remember the initial value
    @value = props.defaultValue or ""

    # bind event handler to the current context
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  ###*
   * Event handler when the mouse left the select field
   * @param event {object} ReactJS event object
  ###
  on_blur: (event) ->
    el = event.currentTarget
    # Extract the UID attribute
    uid = el.getAttribute("uid")
    # Extract the column_key attribute
    name = el.getAttribute("column_key") or el.name
    # Extract the value of the numeric field
    value = el.value

    console.debug "Select::on_blur: value=#{value}"

    # Call the *save* field handler with the UID, name, value
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @props.item

  ###*
   * Event handler when the value changed of the select field
   * @param event {object} ReactJS event object
  ###
  on_change: (event) ->
    el = event.currentTarget
    # Extract the UID attribute
    uid = el.getAttribute("uid")
    # Extract the column_key attribute
    name = el.getAttribute("column_key") or el.name
    # Extract the value of the numeric field
    value = el.value

    # Only propagate for new values
    if value == @value
      return

    console.debug "Select::on_change: value=#{value}"

    # store the new value
    @value = value

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @props.item

  ###*
   * Select options builder
   * @param options {array} list of option objects, e.g.:
   *                        {"ResultText": ..., "ResultValue": ...}
  ###
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
        </option>)

    return options

  render: ->
    <span className="form-group">
      {@props.before and <span className="before_field" dangerouslySetInnerHTML={{__html: @props.before}}></span>}
      <select key={@props.name}
              uid={@props.uid}
              name={@props.name}
              defaultValue={@props.defaultValue}
              column_key={@props.column_key}
              title={@props.title}
              disabled={@props.disabled}
              onBlur={@props.onBlur or @on_blur}
              onChange={@props.onChange or @on_change}
              required={@props.required}
              className={@props.className}
              {...@props.attrs}>
        {@build_options()}
      </select>
      {@props.after and <span className="after_field" dangerouslySetInnerHTML={{__html: @props.after}}></span>}
    </span>


export default Select
