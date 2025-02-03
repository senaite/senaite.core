import {
  render_address_widget,
  render_phone_widget,
  render_queryselect_widget,
  render_selectother_widget,
  render_tinymce_widget,
  render_uidreference_widget,
} from "./widgets/renderer.js"

// Provide widget controllers in a global namespace
window.senaite = window.senaite || {};
window.senaite.core = window.senaite.core || {};
window.senaite.core.widgets = window.senaite.core.widgets || {};


// Widget Renderers
const WIDGETS = [
  // Query Select Widget
  {
    selector: ".senaite-queryselect-widget-input",
    renderer: (el) => {
      return render_queryselect_widget(el);
    },
  },
  // UID Reference Widget
  {
    selector: ".senaite-uidreference-widget-input",
    renderer: (el) => {
      return render_uidreference_widget(el);
    },
  },
  // Address Widget
  {
    selector: ".senaite-address-widget-input",
    renderer: (el) => {
      return render_address_widget(el);
    },
  },
  // Phone Widget
  {
    selector: ".senaite-phone-widget-input",
    renderer: (el) => {
      return render_phone_widget(el);
    },
  },
  // TinyMCE Widget
  {
    selector: "textarea.mce_editable,div.ArchetypesRichWidget textarea,textarea[name='form.widgets.IRichTextBehavior.text'],textarea.richTextWidget",
    renderer: (el) => {
      return render_tinymce_widget(el);
    },
  },
  // SelectOther Widget
  {
    selector: ".senaite-selectother-widget-input",
    renderer: (el) => {
      return render_selectother_widget(el);
    },
  }
]

/** Initialize all widgets below a certain root element
  * */
const render_all_widgets = (root_element) => {
  WIDGETS.forEach((cfg) => {
    let root = root_element instanceof(Node) ? root_element : document;
    let elements = root.querySelectorAll(cfg.selector);
    let renderer = cfg.renderer;
    elements.forEach((element) => {
      if (renderer) {
        let controller = renderer(element);
        if (element.id) {
          // use the ID attribute as the primary identifier
          window.senaite.core.widgets[element.id] = controller;
        } else if (element.dataset.id) {
          // check if we have a `data-id` set that we can use
          window.senaite.core.widgets[JSON.parse(element.dataset.id)] = controller;
        } else {
          console.warn("Element has no ID set! Controller can not be accessed for ", element)
        }
      } else {
        throw new Error("Widget renderer required");
      }
    });
  });
}

// Initialize all widgets when the document is ready
document.addEventListener("DOMContentLoaded", () => {
  console.info("*** SENAITE CORE WIDGETS JS LOADED ***");

  // Render all (visble) widgets on the current page
  render_all_widgets();

  // DataGrid event handler when a new row was added
  document.body.addEventListener("datagrid:row_added", (event) => {
    // We need to initialize all widgets within the new row, otherwise they
    // won't be functional
    render_all_widgets(event.detail.row);
  });

});
