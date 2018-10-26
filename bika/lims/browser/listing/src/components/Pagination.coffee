import React from "react"


class Pagination extends React.Component

  constructor: (props) ->
    super(props)

    @state =
      pagesize: @props.pagesize

    @onShowMoreClick = @onShowMoreClick.bind @
    @onPageSizeChange = @onPageSizeChange.bind @
    @pagesizeInput = React.createRef()

  onShowMoreClick: (event) ->
    event.preventDefault()

    pagesize = parseInt @pagesizeInput.current.value
    if not pagesize or pagesize < 1
      pagesize = 1

    @props.onShowMore pagesize

  onPageSizeChange: (event) ->
    pagesize = parseInt @pagesizeInput.current.value

    if not pagesize or pagesize < 1
      pagesize = 1
      @pagesizeInput.current.value = pagesize

    @setState pagesize: pagesize

    if event.which == 13
      event.preventDefault()
      @props.onShowMore pagesize

  render: ->
    <div id={@props.id} className={@props.className}>
      <div className="input-group input-group-sm">
        <span className="input-group-addon">
          {@props.count} / {@props.total}
        </span>
        <input type="text"
               defaultValue={@state.pagesize}
               onChange={@onPageSizeChange}
               onKeyPress={@onPageSizeChange}
               ref={@pagesizeInput}
               disabled={@props.count >= @props.total}
               className="form-control"/>
        <span className="input-group-btn">
          <button className="btn btn-default"
                  disabled={@props.count >= @props.total}
                  onClick={@onShowMoreClick}>
            <span>Show </span>
            <span className="">
              {@state.pagesize}
            </span>
            <span> more</span>
          </button>
        </span>
      </div>
    </div>


export default Pagination
