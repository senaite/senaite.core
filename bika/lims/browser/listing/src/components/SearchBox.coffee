import React from "react"


class SearchBox extends React.Component

  constructor: (props) ->
    super(props)

    @onSearchInputKeyPress = @onSearchInputKeyPress.bind @
    @onSearchButtonClick = @onSearchButtonClick.bind @
    @onClearButtonClick = @onClearButtonClick.bind @

    @searchInput = React.createRef()

  onSearchInputKeyPress: (event) ->
    event.preventDefault()
    if event.which == 13
      el = event.currentTarget
      console.debug "ENTER KEYPRESS DETECTED: value=#{el.value}"
      @props.onSearch el.value

  onSearchButtonClick: (event) ->
    event.preventDefault()
    value = @searchInput.current.value
    @props.onSearch value

  onClearButtonClick: (event) ->
    event.preventDefault()
    @searchInput.current.value = ""
    @props.onSearch ""

  render: ->
    <div className="input-group input-group-sm">
      <input type="text"
             ref={@searchInput}
             className="form-control"
             defaultValue={@props.filter}
             onKeyPress={@onSearchInputKeyPress}
             placeholder={this.props.placeholder}/>
      <span className="input-group-btn">
        <button className="btn btn-default"
                onClick={@onClearButtonClick}>
          <span className="glyphicon glyphicon-remove"></span>
        </button>
        <button className="btn btn-default"
                onClick={@onSearchButtonClick}>
          <span className="glyphicon glyphicon-search"></span>
        </button>
      </span>
    </div>

export default SearchBox
