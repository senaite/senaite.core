import React from "react";
import ReactDOM from "react-dom";
import tinymce from "tinymce";

import QuerySelectWidgetController from "./widgets/queryselect/widget.js"
import AddressWidgetController from "./widgets/addresswidget/widget.js"
import intlTelInput from "intl-tel-input";
import "intl-tel-input/build/css/intlTelInput.css";

document.addEventListener("DOMContentLoaded", () => {
  console.info("*** SENAITE CORE WIDGETS JS LOADED ***");

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

  // UIDReferenceWidget
  let ref_widgets = document.getElementsByClassName("senaite-uidreference-widget-input");
  for (let widget of ref_widgets) {
    ReactDOM.render(<QuerySelectWidgetController root_class="uidreferencefield" root_el={widget} />, widget);
  }

  // QuerySelectWidget
  let queryselect_widgets = document.getElementsByClassName("senaite-queryselect-widget-input");
  for (let widget of queryselect_widgets) {
    ReactDOM.render(<QuerySelectWidgetController root_class="queryselectfield" root_el={widget} />, widget);
  }

  // AddressWidget
  let address_widgets = document.getElementsByClassName("senaite-address-widget-input");
  for (let widget of address_widgets) {
    ReactDOM.render(<AddressWidgetController root_el={widget} />, widget);
  }

  // PhoneWidget
  // https://github.com/jackocnr/intl-tel-input#readme
  let phone_widgets = document.getElementsByClassName("senaite-phone-widget-input");
  let error_codes = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];
  let init_phone_input = (el) => {
    let id = el.dataset.intlTelInputId;
    let initial_country = el.dataset.initial_country;
    let preferred_countries = JSON.parse(el.dataset.preferred_countries);
    let iti = intlTelInput(el, {
      initialCountry: initial_country,
      preferredCountries: preferred_countries,
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
