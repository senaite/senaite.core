import React from "react"


class MultiSelect extends React.Component

  ###*
   * Multi-Select Field for the Listing Table
   *
   * A multi select field is identified by the column type "multichoices" in the listing
   * view, e.g.  `self.columns = {"Result": {"type": "multichoices"}, ... }`
   *
  ###
  constructor: (props) ->
    super(props)

    # bind event handler to the current context
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  ###*
   * Event handler when the mouse left the select field
   * @param event {object} ReactJS event object
  ###
  on_blur: (event) ->
    el = event.currentTarget
    # Get the parent list wrapper
    ul = el.parentNode.parentNode
    # Extract all checked items
    checked = ul.querySelectorAll("input[type='checkbox']:checked")
    # Extract the UID attribute
    uid = el.getAttribute("uid")
    # Extract the column_key attribute
    name = el.getAttribute("column_key") or el.name
    # Prepare a list of UIDs
    value = (input.value for input in checked)

    console.debug "MultiSelect::on_blur: value=#{value}"

    # Call the *save* field handler with the UID, name, value
    if @props.save_editable_field
      @props.save_editable_field uid, value, checked, @props.item

  ###*
   * Event handler when the value changed of the select field
   * @param event {object} ReactJS event object
  ###
  on_change: (event) ->
    el = event.currentTarget
    # Get the parent list wrapper
    ul = el.parentNode.parentNode
    # Extract all checked items
    checked = ul.querySelectorAll("input[type='checkbox']:checked")
    # Extract the UID attribute
    uid = el.getAttribute("uid")
    # Extract the column_key attribute
    name = el.getAttribute("column_key") or el.name
    # Prepare a list of UIDs
    value = (input.value for input in checked)

    console.debug "MultiSelect::on_change: value=#{value}"

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

    # Sort the items alphabetically
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
                 onChange={@props.onChange or @on_change}
                 onBlur={@props.onBlur or @on_blur}
                 column_key={@props.column_key}
                 {...@props.attrs}/> {title}
        </li>)

    return options

  render: ->
    <div className="multiselect">
      {@props.before and <span className="before_field" dangerouslySetInnerHTML={{__html: @props.before}}></span>}
      <ul className="list-unstyled">
        {@build_options()}
      </ul>
      {@props.after and <span className="after_field" dangerouslySetInnerHTML={{__html: @props.after}}></span>}
    </div>


export default MultiSelect
