import $ from "jquery";
import I18N from "./i18n.js";

document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE JS LOADED ***");

  // global variables for backward compatibility
  window.portal_url = document.querySelector("body").dataset.portalUrl

  var _t = null;
  window._t = (msgid, keywords) => {
    if (_t === null) {
      var i18n = new I18N();
      i18n.loadCatalog("senaite.core")
      _t = i18n.MessageFactory("senaite.core")
    }
    return _t(msgid, keywords);
  }

  $("#sidebar-header").on("click", function () {
    $("#sidebar").toggleClass("minimized");
  });

});
