import React from "react";
import ReactDOM from "react-dom/client";
// https://www.tiny.cloud/docs/tinymce/6
import tinymce from "tinymce";
// https://github.com/jackocnr/intl-tel-input#readme
import intlTelInput from "intl-tel-input";
import "intl-tel-input/build/css/intlTelInput.css";
// Custom ReactJS controlled widgets
import QuerySelectWidgetController from "./queryselect/widget.js"
import AddressWidgetController from "./addresswidget/widget.js"
import SelectOtherWidgetController from "./selectother/widget.js"

// Helper to render React components safely using createRoot
const safeRender = (Component, el, props = {}) => {
  if (!el._reactRoot) {
    el._reactRoot = ReactDOM.createRoot(el);
  }
  return el._reactRoot.render(<Component {...props} root_el={el} />);
};

// Query Select Widget
export const render_queryselect_widget = (el) => {
  return safeRender(QuerySelectWidgetController, el, { root_class: "queryselectfield" });
}

// UID Reference Widget
export const render_uidreference_widget = (el) => {
  return safeRender(QuerySelectWidgetController, el, { root_class: "uidreferencefield" });
}

// Address Widget
export const render_address_widget = (el) => {
  return safeRender(AddressWidgetController, el, { root_class: "address" });
}

// TinyMCE Widget
export const render_tinymce_widget = (el) => {
  return tinymce.init({
    height: 300,
    paste_data_images: true,
    target: el,
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    // NOTE: CSS file must match configuration of entry point in webpack.config.js
    content_css: "/++plone++senaite.core.static/bundles/senaite.core.css",
    promotion: false,
    branding: false,
    license_key: "gpl",
  });
};
// Fixture to skip plone.protect patching
(window.tinymce = window.tinymce || {}).util = window.tinymce.util || {};
(window.tinymce.util.XHR = window.tinymce.util.XHR || {})._send = window.tinymce.util.XHR._send || function () {};

// Phone Widget
export const render_phone_widget = (el) => {
  let id = el.dataset.intlTelInputId;
  let initial_country = el.dataset.initial_country;
  let preferred_countries = JSON.parse(el.dataset.preferred_countries);
  let error_codes = ["Invalid number", "Invalid country code", "Too short", "Too long", "Invalid number"];
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
  return iti;
}

// SelectOther Widget
export const render_selectother_widget = (el) => {
  return safeRender(SelectOtherWidgetController, el, { root_class: "selectotherfield" });
}
