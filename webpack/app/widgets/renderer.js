import React from "react";
import ReactDOM from "react-dom/client";
import tinymce from "tinymce";
import intlTelInput from "intl-tel-input";
import "intl-tel-input/build/css/intlTelInput.css";

import QuerySelectWidgetController from "./queryselect/widget.js";
import AddressWidgetController from "./addresswidget/widget.js";
import SelectOtherWidgetController from "./selectother/widget.js";
import MultiUploadWidgetController from "./multiupload/widget.js";

// Helper to render React components safely using createRoot
const safeRender = (Component, el, props = {}) => {
  if (!el._reactRoot) {
    el._reactRoot = ReactDOM.createRoot(el);
  }
  const ref = React.createRef();
  el._reactRoot.render(<Component {...props} ref={ref} root_el={el} />);

  // Return ref immediately, dereference it later
  return ref;
};

// Query Select Widget
export const render_queryselect_widget = (el) => {
  const ref = safeRender(QuerySelectWidgetController, el, {
    root_class: "queryselectfield",
  });
  return ref;
};

// UID Reference Widget
export const render_uidreference_widget = (el) => {
  const ref = safeRender(QuerySelectWidgetController, el, {
    root_class: "uidreferencefield",
  });
  return ref;
};

// Address Widget
export const render_address_widget = (el) => {
  const ref = safeRender(AddressWidgetController, el, {
    root_class: "address",
  });
  return ref;
};

// TinyMCE Widget
export const render_tinymce_widget = (el) => {
  return tinymce.init({
    height: 300,
    paste_data_images: true,
    target: el,
    plugins: ["paste", "link", "fullscreen", "table", "code"],
    content_css: "/++plone++senaite.core.static/bundles/senaite.core.css",
    promotion: false,
    branding: false,
    license_key: "gpl",
  });
};
(window.tinymce = window.tinymce || {}).util = window.tinymce.util || {};
(window.tinymce.util.XHR = window.tinymce.util.XHR || {})._send = window.tinymce.util.XHR._send || function () {};

// Phone Widget
export const render_phone_widget = (el) => {
  let initial_country = el.dataset.initial_country;
  let preferred_countries = JSON.parse(el.dataset.preferred_countries);
  let error_codes = [
    "Invalid number",
    "Invalid country code",
    "Too short",
    "Too long",
    "Invalid number",
  ];

  let iti = intlTelInput(el, {
    initialCountry: initial_country,
    preferredCountries: preferred_countries,
    // avoid that the dropdown is cropped in records widget
    dropdownContainer: document.body,
    // https://github.com/jackocnr/intl-tel-input?tab=readme-ov-file#getting-started-using-a-bundler-eg-webpack
    loadUtils: () => import("intl-tel-input/utils"),
  });

  // prevent duplicate listener by checking a flag
  if (!el.dataset.intlTelInputAttached) {
    el.addEventListener("blur", () => {
      console.debug("Input value:", el.value);
      console.debug("Selected country:", iti.getSelectedCountryData());
      console.debug("Is valid:", iti.isValidNumber());
      console.debug("Formatted number:", iti.getNumber());

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

      // store formatted number in hidden field
      let name = el.dataset.name;
      let hidden = document.querySelector(`input[name="${name}"]`);
      if (hidden) {
        hidden.value = number;
      }
    });

    // mark as attached
    el.dataset.intlTelInputAttached = "true";
  }

  return iti;
};

// SelectOther Widget
export const render_selectother_widget = (el) => {
  const ref = safeRender(SelectOtherWidgetController, el, {
    root_class: "selectotherfield",
  });
  return ref;
};

// Multi-Upload Widget
export const render_multiupload_widget = (el) => {
  const ref = safeRender(MultiUploadWidgetController, el, {
    root_class: "multiuploadfield",
  });
  return ref;
};
