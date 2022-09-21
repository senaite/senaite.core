import $ from "jquery";
import I18N from "./components/i18n.js";
import {i18n, _t, _p} from "./i18n-wrapper.js"
import EditForm from "./components/editform.js"
import Site from "./components/site.js"
import Sidebar from "./components/sidebar.js"
import UIDReferenceWidgetController from "./widgets/uidreferencewidget/widget.js"
import AddressWidgetController from "./widgets/addresswidget/widget.js"


document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE CORE JS LOADED ***");

  // Initialize i18n message factories
  window.i18n = new I18N();
  window._t = _t;
  window._p = _p;

  // BBB: set global `portal_url` variable
  window.portal_url = document.body.dataset.portalUrl

  // TinyMCE
  tinymce.init({
    height: 300,
    paste_data_images: true,
    selector: "textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text'],textarea.richTextWidget",
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    content_css : "/++plone++senaite.core.static/bundles/main.css",
  })
  // /TinyMCE

  // Initialize Site
  window.site = new Site();

  // Initialize Sidebar
  window.sidebar = new Sidebar({
    "el": "sidebar",
  });

  // Ajax Edit Form Handler
  var form = new EditForm({
    form_selectors: [
      "form[name='edit_form']",
      "form.senaite-ajax-form",
    ],
    field_selectors: [
      "input[type='text']",
      "input[type='number']",
      "input[type='checkbox']",
      "input[type='radio']",
      "input[type='file']",
      "select",
      "textarea",
    ]
  })

  // Init Tooltips
  $(function () {
    $("[data-toggle='tooltip']").tooltip();
    $("select.selectpicker").selectpicker();
  });

  // Widgets
  window.widgets = {};
  // Referencewidgets
  var ref_widgets = document.getElementsByClassName("senaite-uidreference-widget-input");
  for (let widget of ref_widgets) {
    let id = widget.dataset.id;
    let controller = ReactDOM.render(<UIDReferenceWidgetController root_el={widget} />, widget);
    window.widgets[id] = controller;
  }
  // AddressWidget
  var address_widgets = document.getElementsByClassName("senaite-address-widget-input");
  for (let widget of address_widgets) {
    let id = widget.dataset.id;
    let controller = ReactDOM.render(<AddressWidgetController root_el={widget} />, widget);
    window.widgets[id] = controller;
  }

  // Workflow Menu Update for Ajax Transitions
  // https://github.com/senaite/senaite.app.listing/pull/87
  document.body.addEventListener("listing:submit", (event) => {
    let menu = document.getElementById("plone-contentmenu-workflow");
    // return immediately if no workflow menu is present
    if (menu === null ) {
      return false;
    }
    // get the base url from the `data-base-url` attribute
    let base_url = document.body.dataset.baseUrl;
    if (base_url === undefined) {
      // fallback to the current location URL
      base_url = location.href.split("#")[0].split("?")[0];
    }
    const request = new Request(base_url + "/menu/workflow_menu");
    fetch(request)
      .then((response) => {
        // we might get a 404 e.g. for WS /manage_results, but this is actually
        // desired. Otherwise, we would update the WF menu of the WS ...
        if (response.ok) {
          return response.text();
        }
      })
      .then((html) => {
        if (!html) {
          return;
        }
        let parser = new DOMParser();
        let doc = parser.parseFromString(html, "text/html");
        let el = doc.body.firstChild;
        menu.replaceWith(el);
      })
  });

});
