import React from "react"


class Pagination extends React.Component
  ###
   * The pagination component renders table paging controls
  ###

  constructor: (props) ->
    super(props)

    @state =
      pagesize: @props.pagesize

    # bind event handler to local context
    @on_show_more_click = @on_show_more_click.bind @
    @on_pagesize_change = @on_pagesize_change.bind @

    # create element references
    @pagesize_input = React.createRef()
    @show_more_button = React.createRef()

  on_show_more_click: (event) ->
    ###
     * Event handler when the "Show more" button was clicked
    ###

    # prevent form submission
    event.preventDefault()

    # parse the value of the pagesize input field
    pagesize = parseInt @pagesize_input.current.value

    # minimum pagesize is 1
    if not pagesize or pagesize < 1
      pagesize = 1

    # call the parent event handler
    @props.onShowMore pagesize

  on_pagesize_change: (event) ->
    ###
     * Event handler when a manual pagesize was entered
    ###

    pagesize = @get_pagesize_input_value()

    # set the pagesize to the local state
    @setState pagesize: pagesize

    # handle enter keypress
    if event.which == 13
      # prevent form submission
      event.preventDefault()

      # call the parent event listener
      @props.onShowMore pagesize

  get_pagesize_input_value: ->
    ###
     * Fetch the value of the pagesize input field
    ###

    pagesize = parseInt @pagesize_input.current.value

    if not pagesize or pagesize < 1
      # minimum pagesize is 1
      pagesize = 1
      # write sanitized value back to the field
      @pagesize_input.current.value = pagesize

    return pagesize

  render: ->
    if @props.count >= @props.total
      <div className="text-right">
        {@props.count} / {@props.total}
      </div>
    else
      <div id={@props.id} className={@props.className}>
        <div className="input-group input-group-sm">
          <span className="input-group-addon">
            {@props.count} / {@props.total}
          </span>
          <input type="text"
                 defaultValue={@state.pagesize}
                 onChange={@on_pagesize_change}
                 onKeyPress={@on_pagesize_change}
                 ref={@pagesize_input}
                 disabled={@props.count >= @props.total}
                 className="form-control"/>
          <span className="input-group-btn">
            <button className="btn btn-default"
                    disabled={@props.count >= @props.total}
                    ref={@show_more_button}
                    onClick={@on_show_more_click}>
              <span>{@props.show_more_button_title or "Show more"}</span>
            </button>
          </span>
        </div>
      </div>


export default Pagination
