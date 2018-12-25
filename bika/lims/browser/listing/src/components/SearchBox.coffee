import React from "react"


class SearchBox extends React.Component
  ###
   * This component provides a search box
  ###

  constructor: (props) ->
    super(props)

    @on_search_field_keypress = @on_search_field_keypress.bind @
    @on_search_button_click = @on_search_button_click.bind @
    @on_clear_button_click = @on_clear_button_click.bind @

    @search_input_field = React.createRef()

  on_search_field_keypress: (event) ->
    ###
     * Event handler when a keypress was detected in the searchfield
    ###

    # handle enter key
    if event.which == 13
      # prevent form submission on enter
      event.preventDefault()

      # call the parent event handler with the current search value
      value = @get_search_value()
      @props.on_search value

  on_search_button_click: (event) ->
    ###
     * Event handler when the search button was clicked
    ###

    # prevent form submission
    event.preventDefault()

    # call the parent event handler with the current search value
    value = @get_search_value()
    @props.on_search value

  on_clear_button_click: (event) ->
    ###
     * Event handler when the clear button was clicked
    ###

    # prevent form submission
    event.preventDefault()

    # flush the search field value
    @search_input_field.current.value = ""

    # call the parent event handler with the current search value
    @props.on_search ""

  get_search_value: ->
    ###
     * Return the value of the search field
    ###
    value = @search_input_field.current.value
    return value

  render: ->
    if @props.show_search is no
      return null

    <div className="input-group input-group-sm">
      <input type="text"
             className="form-control"
             ref={@search_input_field}
             defaultValue={@props.filter}
             onKeyPress={@on_search_field_keypress}
             placeholder={this.props.placeholder}/>
      <span className="input-group-btn">
        <button className="btn btn-default"
                onClick={@on_clear_button_click}>
          <span className="glyphicon glyphicon-remove"></span>
        </button>
        <button className="btn btn-default"
                onClick={@on_search_button_click}>
          <span className="glyphicon glyphicon-search"></span>
        </button>
      </span>
    </div>

export default SearchBox
