import React from "react"


class RemarksField extends React.Component

  ###*
   * Collapsible Remarks Field for the Listing Table
   *
   * A remarks field is identified by the column type "remarks" in the listing
   * view, e.g.  `self.columns = {"Remarks": {"type": "remarks"}, ... }`
   *
  ###
  constructor: (props) ->
    super(props)
    # Bind events to local context
    @on_blur = @on_blur.bind @
    @on_change = @on_change.bind @

  ###*
   * Event handler when the mouse left the textarea
   * @param event {object} ReactJS event object
  ###
  on_blur: (event) ->
    el = event.currentTarget
    # Extract the UID attribute
    uid = el.getAttribute("uid")
    # Extract the column_key (usually `Remarks`)
    name = el.getAttribute("column_key") or el.name
    # Extract the value of the textarea
    value = el.value
    console.debug "RemarksField:on_blur: value=#{value}"

    # Call the *save* field handler with the UID, name, value
    if @props.save_editable_field
      @props.save_editable_field uid, name, value, @props.item

  ###*
   * Event handler when the value changed of the textarea
   * @param event {object} ReactJS event object
  ###
  on_change: (event) ->
    el = event.currentTarget
    # Extract the UID attribute
    uid = el.getAttribute("uid")
    # Extract the column_key (usually `Remarks`)
    name = el.getAttribute("column_key") or el.name
    # Extract the value of the textarea
    value = el.value
    console.debug "RemarksField:on_change: value=#{value}"

    # Call the *update* field handler with the UID, name, value
    if @props.update_editable_field
      @props.update_editable_field uid, name, value, @props.item

  ###*
   * Check if the remarks field is editable or not
   * @param item {object} the folderitem containing the {"Remarks": "..."} data
   * @param column_key {string} the current rendered column key (usually `Remarks`)
  ###
  can_edit: ->
    item = @props.item
    column_key = @props.column_key
    allow_edit = item.allow_edit or []
    return column_key in allow_edit

  ###*
   * Get the title of the column object, e.g.: self.columns = {"Remarks": {"title": "..."}}
   * @param columns {object} as defined in the browser listing view
   * @param column {object} the remarks column definition
  ###
  get_column_title: ->
    columns = @props.columns
    column_key = @props.column_key
    column = columns[column_key]
    title = column.title or "Remarks"
    if (typeof _ == "function") then title = _(title)
    return title

  ###*
   * Compute the inline CSS style for the field
   * @param uid {string} UID of the folderitem
   * @param expanded_remarks {array} list of expanded remarks fields
  ###
  get_style: ->
    uid = @props.uid
    # show if the remarks are expanded or if a remark is set
    show = uid in @props.expanded_remarks or @props.value.length > 0
    style =
      display: if show then "block" else "none"
    return style

  ###*
   * Render the editable/readonly remarks field
   * @param uid {string} UID of the folderitem
   * @param column_key {string} the current rendered column key (usually `Remarks`)
   * @param item {object} the folderitem containing the {"Remarks": "..."} data
  ###
  render_remarks_field: ->
    uid = @props.uid
    column_key = @props.column_key
    name = "#{column_key}.#{uid}:records"
    value = @props.value

    if not @can_edit()
      field = (
        <span className="remarksfield"
              dangerouslySetInnerHTML={{__html: value}}/>)
    else
      field = (
        <textarea
          className="remarksfield form-control"
          uid={uid}
          column_key={column_key}
          style={{width: "100%"}}
          rows={@props.rows or 2}
          name={name}
          onBlur={@props.onBlur or @on_blur}
          onChange={@props.onChange or @on_change}
          defaultValue={value}
          {...@props.attrs}>
        </textarea>)

    return field

  render: ->
    if not @props.uid
      return null
    <div style={@get_style()}
         className="remarks text-muted">
      {@props.before and <span className="before_field" dangerouslySetInnerHTML={{__html: @props.before}}></span>}
      <div className="text-info">
        <span className="glyphicon glyphicon-hand-right"/> {@get_column_title()}:
      </div>
      {@render_remarks_field()}
      {@props.after and <span className="after_field" dangerouslySetInnerHTML={{__html: @props.after}}></span>}
    </div>


export default RemarksField
