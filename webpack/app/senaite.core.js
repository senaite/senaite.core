import $ from "jquery";
import I18N from "./i18n.js";

window.i18n = new I18N();

// SENAITE message factory
var _t = null;
window._t = (msgid, keywords) => {
  if (_t === null) {
    i18n.loadCatalog("senaite.core")
    _t = i18n.MessageFactory("senaite.core")
  }
  return _t(msgid, keywords);
}

// Plone message factory
var _p = null;
window._p = (msgid, keywords) => {
  if (_p === null) {
    i18n.loadCatalog("plone")
    _p = i18n.MessageFactory("plone")
  }
  return _p(msgid, keywords);
}


document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE JS LOADED ***");

  // global variables for backward compatibility
  window.portal_url = document.querySelector("body").dataset.portalUrl

  // Initialize
  tinymce.init({
    selector: '.mce_editable',
    // skin: false,
    plugins: ["paste", "link", "autoresize", "fullscreen", "table"],
  })


  $("#sidebar-header").on("click", function () {
    $("#sidebar").toggleClass("minimized");
  });

});
