import $ from "jquery";
import I18N from "./components/i18n.js";
import {i18n, _t, _p} from "./i18n-wrapper.js"
import Site from "./components/site.js"
import Sidebar from "./components/sidebar.js"


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


  // Tooltips
  $(function () {
    $("[data-toggle='tooltip']").tooltip()
  })
  // /Tooltips

  // Auto LogOff
  var logoff = document.body.dataset.autoLogoff || 0;
  var logged = document.body.classList.contains("userrole-authenticated");
  // Max value for setTimeout is a 32 bit integer
  const max_timeout = 2**31 - 1;
  if (logoff > 0 && logged) {
    var logoff_ms = logoff * 60 * 1000;
    if (logoff_ms > max_timeout) {
      console.warn(`Setting logoff_ms to max value ${max_timeout}ms`);
      logoff_ms = max_timeout;
    }
    setTimeout(function() {
      location.href = window.portal_url + "/logout";
    }, logoff_ms);
  }
  // /Auto LogOff


  // Ajax EDIT
  var form = document.querySelector("form[name='edit_form']")
  var changed = {};

  var ajax_edit = function(name, value) {
    let view_url = document.body.dataset.viewUrl;
    let ajax_url = `${view_url}/ajax_edit`;
    let form_data = new FormData(form);
    var data = {};

    form_data.forEach(function(value, key) {
      data[key] = value;
    });

    let init = {
      method: "POST",
      credentials: "include",
      body: JSON.stringify({
        name: name,
        value: value,
        formdata: data
      }),
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": document.querySelector("#protect-script").dataset.token
      },
    }
    let request = new Request(ajax_url, init);
    fetch(request)
      .then(function(response) {
        if (!response.ok) {
          return Promise.reject(response);
        }
        return response.json();
      })
      .then(function(data) {
        let node = document.createElement("html");
        node.innerHTML = data.html;

        debugger

        // let event = new Event("DOMContentLoaded");
        // node.innerHTML = html;
        // let root = document.querySelector("html");
        // root.replaceWith(document.adoptNode(node));
        // document.dispatchEvent(event);
      })
      .catch(function(error) {
        console.error(error);
      });
  }

  var on_blur = function(event) {
    let field = event.currentTarget;
    let name = field.name;
    let value = field.value;
    if (changed[name] == 1) {
      console.info(`FIELD "${name}" changed`);
      ajax_edit(name, value)
      delete changed[field];
    }
  }

  var on_edit = function(event) {
    let field = event.currentTarget;
    let name = field.name;
    changed[name] = 1;
  }

  if (form) {
    let input_fields = form.querySelectorAll("input");
    input_fields.forEach(function(el, index) {
      if (["text", "number"].indexOf(el.type) > -1) {
        el.addEventListener("input", on_edit);
        el.addEventListener("blur", on_blur);
      }
    });
  }

});
