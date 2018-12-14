import React from "react"


class Checkbox extends React.Component

  ###*
   * Checkbox Field for the Listing Table
   *
   * A checkbox field is identified by the column type "checkbox" in the listing
   * view, e.g.  `self.columns = {"Hidden": {"type": "checkbox"}, ... }`
   *
  ###
  constructor: (props) ->
    super(props)

    # bind event handler to the current context
    @on_change = @on_change.bind @

  ###*
   * Event handler when the value changed of the checkbox
   * @param event {object} ReactJS event object
  ###
  on_change: (event) ->
    el = event.currentTarget
    # Extract the UID attribute
    uid = el.getAttribute("uid")
    # Extract the column_key attribute
    name = el.getAttribute("column_key") or el.name
    # Extract the checked status
    checked = el.checked

    console.debug "Checkbox::on_change: checked=#{checked}"

    # Call the *update* field handler
    if @props.update_editable_field
      @props.update_editable_field uid, name, checked, @props.item

    # Call the *save* field handler (no blur event here necessary)
    if @props.save_editable_field
      @props.save_editable_field uid, name, checked, @props.item


  render: ->
    <span className="form-group">
      {@props.before and <span className="before_field" dangerouslySetInnerHTML={{__html: @props.before}}></span>}
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
            onChange={@props.onChange or @on_change}
            {...@props.attrs}/>
      {@props.after and <span className="after_field" dangerouslySetInnerHTML={{__html: @props.after}}></span>}
    </span>


export default Checkbox
