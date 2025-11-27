import {
  render_address_widget,
  render_phone_widget,
  render_queryselect_widget,
  render_selectother_widget,
  render_tinymce_widget,
  render_uidreference_widget,
  render_multiupload_widget,
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
  },
  // Multi-Upload Widget
  {
    selector: ".multiuploadfield",
    renderer: (el) => {
      return render_multiupload_widget(el);
    },
  }
]

/** Initialize all widgets below a certain root element
  * */
const render_all_widgets = (root_element) => {
  const allWaits = [];

  WIDGETS.forEach((cfg) => {
    const root = root_element instanceof(Node) ? root_element : document;
    const elements = root.querySelectorAll(cfg.selector);
    const renderer = cfg.renderer;

    elements.forEach((element) => {
      if (!renderer) {
        throw new Error("Widget renderer required");
      }

      const ref = renderer(element);
      const widget_id = element.id || element.dataset.id || null;

      // workaround to get the controller instance in ReactJS 19
      if (widget_id) {
        // Create a promise for each widget's controller to be available
        const waitForRef = () =>
          new Promise((resolve) => {
            const check = () => {
              if (ref.current) {
                window.senaite.core.widgets[widget_id] = ref.current;
                resolve();
              } else {
                requestAnimationFrame(check);
              }
            };
            check();
          });
        allWaits.push(waitForRef());
      } else {
        console.warn("Element has no ID set! Controller can not be accessed for ", element);
      }
    });
  });

  // Once all widgets are initialized, fire the custom event
  Promise.all(allWaits).then(() => {
    const event = new CustomEvent("senaite.core.widgets:loaded", {
      detail: window.senaite.core.widgets,
    });
    console.debug("All widgets loaded, dispatching event:", event);
    document.dispatchEvent(event);
  });
};

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
