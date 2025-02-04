import $ from "jquery";
import I18N from "./components/i18n.js";
import {i18n, _t, _p} from "./i18n-wrapper.js"
import EditForm from "./components/editform.js"
import Site from "./components/site.js"
import Sidebar from "./components/sidebar.js"


document.addEventListener("DOMContentLoaded", () => {
  console.info("*** SENAITE CORE JS LOADED ***");

  // Initialize i18n message factories
  window.i18n = new I18N();
  window._t = _t;
  window._p = _p;

  // BBB: set global `portal_url` variable
  window.portal_url = document.body.dataset.portalUrl

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

  // Reload the whole view if the status of the view's context has changed
  // due to the transition submission of some items from the listing
  document.body.addEventListener("listing:after_transition_event", (event) => {

    // skip site reload for multi_results view
    let multi_results_templates = ["template-multi_results", "template-multi_results_classic"];
    let body_class_list = document.body.classList;
    for (let class_name of multi_results_templates) {
      if (body_class_list.contains(class_name)) {
        return;
      }
    }

    // get the old workflow state of the view context
    let old_workflow_state = document.body.dataset.reviewState;

    // get the new workflow state of the view context
    // https://github.com/senaite/senaite.app.listing/pull/92
    let config = event.detail.config;
    let new_workflow_state = config.view_context_state;

    // reload the entire page if workflow state of the view context changed
    if (old_workflow_state != new_workflow_state) {
      location.reload();
    }
  });


  // BBB: create form Bootstrap navigation tabs for all fieldsets that are
  //      located in a form with the CSS class "enableFormTabbing"
  document.querySelectorAll("form.enableFormTabbing").forEach(function (form) {
      let fieldsets = form.querySelectorAll("fieldset");
      if (fieldsets.length === 0) return;

      let nav = document.createElement("ul");
      nav.className = "nav nav-tabs";
      nav.setAttribute("role", "tablist");

      let tabContent = document.createElement("div");
      tabContent.className = "tab-content";

      fieldsets.forEach((fieldset, index) => {
        let legend = fieldset.querySelector("legend");
        let tabId = "tab-" + index;

        let li = document.createElement("li");
        li.className = "nav-item";

        let a = document.createElement("a");
        a.className = "nav-link" + (index === 0 ? " active" : "");
        a.setAttribute("data-toggle", "tab");
        a.href = "#" + tabId;
        a.setAttribute("role", "tab");
        a.innerText = legend ? legend.innerText : "Tab " + (index + 1);

        // remove the legend
        legend.remove();

        li.appendChild(a);
        nav.appendChild(li);

        let tabPane = document.createElement("div");
        tabPane.className = "tab-pane fade" + (index === 0 ? " show active" : "");
        tabPane.id = tabId;
        tabPane.setAttribute("role", "tabpanel");
        fieldset.parentNode.insertBefore(tabPane, fieldset);
        tabPane.appendChild(fieldset);

        tabContent.appendChild(tabPane);
      });

      form.insertBefore(nav, form.firstChild);
      form.insertBefore(tabContent, form.firstChild.nextSibling);
    });

});
