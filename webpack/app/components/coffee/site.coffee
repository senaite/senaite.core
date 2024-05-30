### Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c site.coffee
###

class Site

  ###*
  # Creates a new instance of Site
  ###
  constructor: ()->
    console.debug "Site::init"

  ###*
  # Returns the authenticator value
  ###
  authenticator: =>
    auth =  $("input[name='_authenticator']").val()
    if not auth
      url_params = new URLSearchParams window.location.search
      auth = url_params.get "_authenticator"
    return auth

  ###*
  # Reads a cookie value
  # @param {name} the name of the cookie
  ###
  read_cookie: (name) =>
    console.debug "Site::read_cookie:#{name}"
    name = name + '='
    ca = document.cookie.split ';'
    i = 0
    while i < ca.length
      c = ca[i]
      while c.charAt(0) == ' '
        c = c.substring(1)
      if c.indexOf(name) == 0
        return c.substring(name.length, c.length)
      i++
    return null

  ###*
  # Sets a cookie value
  # @param {name} the name of the cookie
  # @param {value} the value of the cookie
  ###
  set_cookie: (name, value) =>
    console.debug "Site::set_cookie:name=#{name}, value=#{value}"
    d = new Date
    d.setTime d.getTime() + 1 * 24 * 60 * 60 * 1000
    expires = 'expires=' + d.toUTCString()
    document.cookie = name + '=' + value + ';' + expires + ';path=/'
    return


  ###*
  # Add a notification message
  # @param {title} the title of the notification
  # @param {message} the message of the notification
  ###
  add_notification: (title,  message, options) ->
    options ?= {}
    options = Object.assign
      animation: yes
      autohide: yes
      delay: 5000
    , options

    el = document.createElement("div")
    el.innerHTML = "
      <div class='toast bg-white' style='width:300px' role='alert'
           data-animation='#{options.animation}'
           data-autohide='#{options.autohide}'
           data-delay='#{options.delay}'>
        <div class='toast-header'>
          <strong class='mr-auto'>#{title}</strong>
          <button type='button' class='ml-2 mb-1 close' data-dismiss='toast' aria-label='Close'>
            <span aria-hidden='true'>&times;</span>
          </button>
        </div>
        <div class='toast-body'>
          #{_t(message)}
        </div>
      </div>"

    el = el.firstElementChild
    parent = document.querySelector(".toast-container")
    if not parent
      parent = document.createElement("div");
      parent.innerHTML = "
        <div style='position: fixed; top: 0px; right: 0px; width=100%; z-index:100'>
          <div class='toast-container' style='position: absolute; top: 10px; right: 10px;'>
          </div>
        </div>"
      wrapper = document.querySelector(".container-fluid")
      wrapper.appendChild(parent)
      parent = parent.querySelector(".toast-container")

    parent.appendChild(el)
    return $(el).toast("show")


export default Site
