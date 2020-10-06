/* Sidebar
 *
 */

import $ from "jquery";

'use strict';


class Sidebar{

  constructor(config) {

    this.config = Object.assign({
      "el": "sidebar",
      "toggle_el": "sidebar-header",
      "storage_key": "sidebar-toggle",
      "timeout": 1000,
    }, config);

    // Timer ID
    this.tid = null;

    // Bind "this" context when called
    this.maximize = this.maximize.bind(this);
    this.minimize = this.minimize.bind(this);
    this.on_click = this.on_click.bind(this);
    this.on_mouseenter = this.on_mouseenter.bind(this)
    this.on_mouseleave = this.on_mouseleave.bind(this);

    // toggle button handler
    this.toggle_el = document.getElementById(this.config.toggle_el);
    this.toggle_el.addEventListener("click", this.on_click);

    // sidebar view/hide handler
    this.el = document.getElementById(this.config.el);
    this.el.addEventListener("mouseenter", this.on_mouseenter);
    this.el.addEventListener("mouseleave", this.on_mouseleave);

    if (this.is_toggled()) {
      this.el.classList.remove("minimized");
      this.el.classList.add("toggled");
    }

    return this;
  }

  is_toggled() {
    return window.localStorage.getItem(this.config.storage_key) == "true";
  }

  toggle(toggle=false) {
    window.localStorage.setItem(this.config.storage_key, toggle);
    if (toggle) {
      this.el.classList.add("toggled")
      this.maximize();
    } else {
      this.el.classList.remove("toggled")
      this.minimize();
    }
  }

  minimize() {
    this.el.classList.add("minimized");
  }

  maximize() {
    this.el.classList.remove("minimized");
  }

  on_click(event) {
    // console.debug("Sidebar::on_click:event=", event)
    clearTimeout(this.tid);
    this.toggle(!this.is_toggled());
  }

  on_mouseenter(event) {
    // console.debug("Sidebar::on_mouseenter:event=", event)
    clearTimeout(this.tid);
    if (this.is_toggled()) return
    this.tid = setTimeout(this.maximize, this.config.timeout);
  }

  on_mouseleave(event) {
    // console.debug("Sidebar::on_mouseleave:event=", event)
    clearTimeout(this.tid);
    if (this.is_toggled()) return
    this.minimize();
    // console.debug("Clearing sidebar timeout", this.tid);
  }
}

export default Sidebar;
