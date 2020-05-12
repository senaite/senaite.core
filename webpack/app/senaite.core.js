import $ from "jquery";
import I18N from "./i18n.js";

var _t = null;
window._t = (msgid, keywords) => {
  if (_t === null) {
    window.i18n = new I18N();
    i18n.loadCatalog("plone")
    i18n.loadCatalog("senaite.core")
    _t = i18n.MessageFactory("senaite.core")
  }
  return _t(msgid, keywords);
}


document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE JS LOADED ***");

  // global variables for backward compatibility
  window.portal_url = document.querySelector("body").dataset.portalUrl


  $("#sidebar-header").on("click", function () {
    $("#sidebar").toggleClass("minimized");
  });

});
