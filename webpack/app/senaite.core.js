import $ from "jquery";
import {i18n, _t, _p} from "./i18n-wrapper.js"


document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE CORE JS LOADED ***");

  // Initialize i18n message factories
  window.i18n = i18n;
  window._t = _t;
  window._p = _p;

  // BBB: set global `portal_url` variable
  window.portal_url = document.querySelector("body").dataset.portalUrl

  // Initialize TinyMCE
  tinymce.init({
    selector: "textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text']",
    plugins: ["paste", "link", "autoresize", "fullscreen", "table", "code"],
    content_css : "/++plone++senaite.core.static/bundles/main.css",
  })


  // Initialize sidebar toggle
  $("#sidebar-header").on("click", function () {
    $("#sidebar").toggleClass("minimized");
  });

  // Initialize tooltips
  $(function () {
    $("[data-toggle='tooltip']").tooltip()
  })

});
