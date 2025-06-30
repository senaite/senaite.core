/**
 * Site View Controller
 *
 * This controller is *always* loaded, i.e. for all templates.
 */
window.SiteView = class SiteView {
  constructor() {
    this.load = this.load.bind(this);
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.get_portal_url = this.get_portal_url.bind(this);
    this.get_authenticator = this.get_authenticator.bind(this);
    this.log = this.log.bind(this);
    this.readCookie = this.readCookie.bind(this);
    this.read_cookie = this.read_cookie.bind(this);
    this.setCookie = this.setCookie.bind(this);
    this.set_cookie = this.set_cookie.bind(this);
    this.notify_in_panel = this.notify_in_panel.bind(this);
    this.on_at_integer_field_keyup = this.on_at_integer_field_keyup.bind(this);
    this.on_at_float_field_keyup = this.on_at_float_field_keyup.bind(this);
    this.on_numeric_field_input = this.on_numeric_field_input.bind(this);
    this.on_numeric_field_keypress = this.on_numeric_field_keypress.bind(this);
    this.on_overlay_panel_click = this.on_overlay_panel_click.bind(this);
  }

  load() {
    console.debug("SiteView::load");
    this.bind_eventhandler();
    this.allowed_keys = [8, 9, 13, 35, 36, 37, 39, 46, 44, 60, 62, 45, 69, 101, 61];
  }

  bind_eventhandler() {
    console.debug("SiteView::bind_eventhandler");

    $(document).on("keypress", ".numeric", this.on_numeric_field_keypress);
    $(document).on("input", ".numeric", this.on_numeric_field_input);

    // Integer and float fields using attribute checks instead of problematic selectors
    $(document).on("keyup", "input", (e) => {
      const name = e.target.name || "";
      if (name.includes(":int")) this.on_at_integer_field_keyup(e);
      if (name.includes(":float")) this.on_at_float_field_keyup(e);
    });

    $(document).on("click", "a.overlay_panel", this.on_overlay_panel_click);

    $(document).on({
      ajaxStart: () => $("body").addClass("loading"),
      ajaxStop: () => $("body").removeClass("loading"),
      ajaxError: () => $("body").removeClass("loading")
    });
  }

  get_portal_url() {
    return window.portal_url;
  }

  get_authenticator() {
    console.warn("SiteView::get_authenticator is deprecated. Use site.authenticator()");
    return window.site.authenticator();
  }

  log(message) {
    console.debug(`SiteView::log: ${message}`);
    return senaite.core.globals.log(message);
  }

  readCookie(cname) {
    console.warn("Use read_cookie instead");
    return this.read_cookie(cname);
  }

  read_cookie(cname) {
    const nameEQ = `${cname}=`;
    const ca = document.cookie.split(';');
    for (let c of ca) {
      c = c.trim();
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length);
    }
    return null;
  }

  setCookie(cname, cvalue) {
    console.warn("Use set_cookie instead");
    return this.set_cookie(cname, cvalue);
  }

  set_cookie(cname, cvalue) {
    document.cookie = `${cname}=${cvalue}; path=/`;
  }

  notify_in_panel(data, mode) {
    console.debug(`notify_in_panel: ${mode} = ${data}`);
    $('#panel-notification').remove();
    const html = `
      <div id="panel-notification" style="display:none">
        <div class="${mode}-notification-item">${data}</div>
      </div>`;
    $('div#viewlet-above-content-title').append(html);
    $('#panel-notification').fadeIn('slow', () => {
      setTimeout(() => {
        $('#panel-notification').fadeOut('slow');
      }, 3000);
    });
  }

  on_at_integer_field_keyup(e) {
    const $el = $(e.currentTarget);
    const cleanVal = $el.val().replace(/\D/g, '');
    if ($el.val() !== cleanVal) {
      $el.val(cleanVal);
    }
  }

  on_at_float_field_keyup(e) {
    const $el = $(e.currentTarget);
    const cleanVal = $el.val().replace(/[^-.\d]/g, '');
    if ($el.val() !== cleanVal) {
      $el.val(cleanVal);
    }
  }

  on_numeric_field_keypress(e) {
    const key = e.which || e.keyCode;
    const char = String.fromCharCode(key);
    const $el = $(e.currentTarget);
    const value = $el.val();

    const isDigit = key >= 48 && key <= 57;
    const isComma = char === ',';
    const isDot = char === '.';
    const isAllowed = this.allowed_keys.includes(key);

    // Allow digits and control keys
    if (isDigit || isAllowed) return;

    // Allow one comma or one dot (handled later)
    if ((isComma || isDot) && !value.includes('.')) return;

    // Block everything else
    e.preventDefault();
  }

  on_numeric_field_input(e) {
    const $el = $(e.currentTarget);
    let val = $el.val();

    // Replace comma with dot
    val = val.replace(',', '.');

    // Remove all but the first dot
    const firstDotIndex = val.indexOf('.');
    if (firstDotIndex !== -1) {
      val = val.slice(0, firstDotIndex + 1) + val.slice(firstDotIndex + 1).replace(/\./g, '');
    }

    // Optional: strip non-numeric characters
    val = val.replace(/[^0-9.]/g, '');

    $el.val(val);
  }

  on_overlay_panel_click(e) {
    e.preventDefault();
    const $el = $(e.currentTarget);

    if (typeof $el.prepOverlay === 'function') {
      $el.prepOverlay({
        subtype: 'ajax',
        width: '80%',
        filter: '#content>*:not(div#portal-column-content)',
        config: {
          closeOnClick: true,
          closeOnEsc: true,
          onBeforeLoad: function () {
            this.getOverlay().draggable();
          },
          onLoad: function () {
            document.dispatchEvent(new Event("DOMContentLoaded"));
          }
        }
      });
      $el.click();
    } else {
      console.warn('prepOverlay not available. Consider updating or replacing it.');
    }
  }
};
