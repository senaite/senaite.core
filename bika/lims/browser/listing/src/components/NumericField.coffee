import React from "react"


class NumericField extends React.Component

  ###*
   * Numeric Field for the Listing Table
   *
   * A numeric field is identified by the column type "numeric" in the listing
   * view, e.g.  `self.columns = {"Result": {"type": "numeric"}, ... }`
   *
  ###
  constructor: (props) ->
    super(props)

    # remember the initial value
    @value = props.defaultValue or ""
    @changed = no

    # bind event handler to the current context
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  ###*
   * Event handler when the mouse left the numeric field
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
    # Remove any trailing dots
    value = value.replace(/\.*$/, "")
    # Set the sanitized value back to the field
    el.value = value

    # Only propagate for new values
    if not @changed
      return

    # reset the change flag
    @changed = no

    console.debug "NumericField::on_blur: value=#{value}"

    # Call the *save* field handler with the UID, name, value
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @props.item

  ###*
   * Event handler when the value changed of the numeric field
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
    # Convert the value to float
    value = @to_float value
    # Set the float value back to the field
    el.value = value

    # Only propagate for new values
    if value == @value
      return

    # store the new value
    @value = value

    # set the change flag
    @changed = yes

    console.debug "NumericField::on_change: value=#{value}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @props.item

  ###*
   * Float converter
   * @param value {string} a numeric string value
  ###
  to_float: (value) ->
    # Valid -.5; -0.5; -0.555; .5; 0.5; 0.555
    #       -,5; -0,5; -0,555; ,5; 0,5; 0,555
    # Non Valid: -.5.5; 0,5,5; ...;
    value = value.replace /(^-?)(\d*)([\.,]?\d*)(.*)/, "$1$2$3"
    value = value.replace(",", ".")
    return value

  render: ->
    <span className="form-group">
      {@props.before and <span className="before_field" dangerouslySetInnerHTML={{__html: @props.before}}></span>}
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
             onBlur={@props.onBlur or @on_blur}
             onChange={@props.onChange or @on_change}
             {...@props.attrs}/>
      {@props.after and <span className="after_field" dangerouslySetInnerHTML={{__html: @props.after}}></span>}
    </span>


export default NumericField
