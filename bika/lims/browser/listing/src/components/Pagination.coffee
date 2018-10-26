import React from "react"


class Pagination extends React.Component

  constructor: (props) ->
    super(props)
    @state =
      pagesize: props.pagesize
    @onShowMoreClick = @onShowMoreClick.bind @
    @onPageSizeChange = @onPageSizeChange.bind @
    @pagesizeInput = React.createRef()

  onShowMoreClick: (event) ->
    event.preventDefault()
    el = event.currentTarget
    pagesize = parseInt @pagesizeInput.current.value
    if not pagesize or pagesize < 0
      pagesize = 0
    items_to_show = pagesize + @props.count
    @props.onShowMore items_to_show

  onPageSizeChange: (event) ->
    event.preventDefault()
    pagesize = parseInt @pagesizeInput.current.value
    if not pagesize or pagesize < 0
      pagesize = 0
      @pagesizeInput.current.value = pagesize
    @setState pagesize: pagesize

    if event.which == 13
      console.debug "Page size changed to #{pagesize}"
      me = this
      items_to_show = pagesize + @props.count
      @setState pagesize: pagesize, ->
        me.props.onShowMore items_to_show

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
