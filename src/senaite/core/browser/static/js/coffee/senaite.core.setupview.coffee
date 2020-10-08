### Please use this command to compile this file into the parent directory:
    coffee --no-header -w -o ../ -c senaite.core.setupview.coffee
###

# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "*** DOMContentLoaded: --> Loading Controller"
  window.setupview_controller = new SetupViewController()

class SetupViewController

  constructor: ->

    @on_search = @on_search.bind this
    @on_keypress = @on_keypress.bind this

    searchbox = document.getElementById "searchbox"
    searchbox.addEventListener "input", @on_search
    searchbox.addEventListener "keypress", @on_keypress

    @first = null
    @items = @get_items()

  hide_tile: (tile) ->
      tile.classList.add "d-none"

  show_tile: (tile) ->
      tile.classList.remove "d-none"

  get_tiles: ->
    return document.querySelectorAll("div.tilewrapper")

  get_items: ->
    nodes = document.querySelectorAll("div.tilewrapper span.title")
    items = []
    nodes.forEach (el) ->
      title = el.innerText.toLowerCase()
      items.push {title: title, el: el}
    return items

  show_all: ->
    tiles = @get_tiles()
    tiles.forEach (tile) =>
      @show_tile tile

  filter_items: (value) ->
    # console.debug "SetupViewController::filter_items:value=", value
    @first = null
    if not value
      return @show_all()
    @items.forEach (item) =>
      el = item.el
      tile = el.closest "div.tilewrapper"
      title = item.title
      rx = RegExp(value, "gi");

      if title.match rx
        @show_tile tile
        # remember the first matching tile
        if @first is null
          @first = tile
      else
        @hide_tile tile

  navigate: (tile) ->
    if @first is null
      return
    url = @first.querySelector("a").getAttribute("href")
    return unless url
    location.href = url

  on_search: (event) ->
    target = event.currentTarget
    value = target.value.toLowerCase()
    @filter_items value

  on_keypress: (event) ->
    code = event.keyCode
    return unless code is 13
    @navigate()
