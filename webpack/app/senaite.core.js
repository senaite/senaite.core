import $ from "jquery";
import {i18n, _t, _p} from "./i18n-wrapper.js"
import Sidebar from "./components/sidebar.js"


document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE CORE JS LOADED ***");

  // Initialize i18n message factories
  window.i18n = i18n;
  window._t = _t;
  window._p = _p;

  // BBB: set global `portal_url` variable
  window.portal_url = document.body.dataset.portalUrl

  // TinyMCE
  tinymce.init({
    height: 300,
    selector: "textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text'],textarea.richTextWidget",
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    content_css : "/++plone++senaite.core.static/bundles/main.css",
  })
  // /TinyMCE


  // Initialize Sidebar
  window.sidebar = new Sidebar({
    "el": "sidebar",
  });


  // Tooltips
  $(function () {
    $("[data-toggle='tooltip']").tooltip()
  })
  // /Tooltips

  // Auto LogOff
  var logoff = document.body.dataset.autoLogoff || 0;
  var logged = document.body.classList.contains('userrole-authenticated');
  if (logoff > 0 && logged) {
    var logoff_ms = logoff * 60 * 1000;
    setTimeout(function() {
      location.href = window.portal_url + "/logout";
    }, logoff_ms);
  }
  // /Auto LogOff

});
