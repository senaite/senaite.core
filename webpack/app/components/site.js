
/* Please use this command to compile this file into the parent `js` directory:
    coffee --no-header -w -o ../ -c site.coffee
 */
var Site,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

Site = (function() {

  /**
   * Creates a new instance of Site
   */
  function Site() {
    this.set_cookie = bind(this.set_cookie, this);
    this.read_cookie = bind(this.read_cookie, this);
    this.authenticator = bind(this.authenticator, this);
    // console.debug("Site::init");
  }


  /**
   * Returns the authenticator value
   */

  Site.prototype.authenticator = function() {
    var auth, url_params;
    auth = $("input[name='_authenticator']").val();
    if (!auth) {
      url_params = new URLSearchParams(window.location.search);
      auth = url_params.get("_authenticator");
    }
    return auth;
  };


  /**
   * Reads a cookie value
   * @param {name} the name of the cookie
   */

  Site.prototype.read_cookie = function(name) {
    var c, ca, i;
    // console.debug("Site::read_cookie:" + name);
    name = name + '=';
    ca = document.cookie.split(';');
    i = 0;
    while (i < ca.length) {
      c = ca[i];
      while (c.charAt(0) === ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) === 0) {
        return c.substring(name.length, c.length);
      }
      i++;
    }
    return null;
  };


  /**
   * Sets a cookie value
   * @param {name} the name of the cookie
   * @param {value} the value of the cookie
   */

  Site.prototype.set_cookie = function(name, value) {
    var d, expires;
    // console.debug("Site::set_cookie:name=" + name + ", value=" + value);
    d = new Date;
    d.setTime(d.getTime() + 1 * 24 * 60 * 60 * 1000);
    expires = 'expires=' + d.toUTCString();
    document.cookie = name + '=' + value + ';' + expires + ';path=/';
  };

  return Site;

})();

export default Site;
