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

export default Site
