import UIDReferenceWidgetController from "./widgets/uidreferencewidget/widget.js"
import AddressWidgetController from "./widgets/addresswidget/widget.js"
import intlTelInput from "intl-tel-input";
import "intl-tel-input/build/css/intlTelInput.css";

document.addEventListener("DOMContentLoaded", () => {
  console.info("*** SENAITE CORE WIDGETS JS LOADED ***");

  // Widgets
  window.widgets = {};

  // TinyMCE
  let wysiwig_elements = [
    "textarea.mce_editable",
    "div.ArchetypesRichWidget textarea",
    "textarea[name='form.widgets.IRichTextBehavior.text']",
    "textarea.richTextWidget",
  ]
  tinymce.init({
    height: 300,
    paste_data_images: true,
    selector: wysiwig_elements.join(","),
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    // NOTE: CSS file must match configuration of entry point in webpack.config.js
    content_css : "/++plone++senaite.core.static/bundles/senaite.core.css",
  })

  // Referencewidget
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

  // PhoneWidget
  // https://github.com/jackocnr/intl-tel-input#readme
  let phone_widgets = document.getElementsByClassName("senaite-phone-widget-input");
  let error_codes = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];
  let init_phone_input = (el) => {
    let id = el.dataset.intlTelInputId;
    let iti = intlTelInput(el, {
      // avoid that the dropdown is cropped in records widget
      dropdownContainer: document.body,
      // https://github.com/jackocnr/intl-tel-input#utilities-script
      utilsScript: "++plone++senaite.core.static/modules/intl-tel-input/js/utils.js"
    });
    // add event handler only once
    if (id === undefined) {
      el.addEventListener("blur", () => {
        // validation
        let valid = iti.isValidNumber();
        let number = iti.getNumber();
        let field = el.closest(".field");
        if (valid) {
          field.classList.remove("error");
          field.title = "";
        } else {
          field.classList.add("error");
          let error_code = iti.getValidationError();
          let error_msg = error_codes[error_code];
          field.title = error_msg;
        }
        // always set the number (even if validation failed!)
        let name = el.dataset.name;
        let hidden = document.querySelector("input[name='" + name + "']");
        hidden.value = number;
      });
    }
  }
  // initialize all phone widgets
  for (let widget of phone_widgets) {
    init_phone_input(widget);
  }
  // dynamically initialize new phone widgets when used in datagrid fields
  document.body.addEventListener("datagrid:row_added", (event) => {
    let row = event.detail.row;
    let input = row.querySelector(".senaite-phone-widget-input");
    if(input) {
      init_phone_input(input);
    }
  });

});
