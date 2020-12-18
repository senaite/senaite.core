/* SENAITE Edit Form Handler
 *
 * This code handles field changes in edit forms and updates others according to
 * the changes with the help of adapters.
 *
 */

class EditForm{

  constructor(config) {
    this.config = Object.assign({
      "form_selectors": [],
      "field_selectors": []
    }, config);
    // bind event handlers
    this.on_modified = this.on_modified.bind(this);
    this.on_blur = this.on_blur.bind(this);
    this.on_click = this.on_click.bind(this);
    this.on_change = this.on_change.bind(this);
    // init form
    this.init_forms();
  }

  /**
   * Initialize all form elements given by the config
   */
  init_forms() {
    let selectors = this.config.form_selectors;
    for (const selector of selectors) {
      let form = document.querySelector(selector);
      if (form && form.tagName === "FORM") {
        this.setup_form(form);
        this.watch_form(form);
      }
    }
  }

  /**
   * Trigger `initialized` event on the form element
   */
  setup_form(form) {
    console.debug(`EditForm::setup_form(${form})`);
    this.ajax_send(form, {}, "initialized");
  }

  /**
   * Bind event handlers on form fields to monitor changes
   */
  watch_form(form) {
    console.debug(`EditForm::watch_form(${form})`);
    let fields = this.get_form_fields(form);
    for (const field of fields) {
      if (this.is_input(field) || this.is_textarea(field) || this.is_select(field)) {
        // bind change event
        field.addEventListener("change", this.on_change);
      }
      else if (this.is_radio(field) || this.is_checkbox(field)) {
        // bind click event
        field.addEventListener("click", this.on_click);
      } else {
        // bind blur event
        field.addEventListener("blur", this.on_blur);
      }
    }
    form.addEventListener("modified", this.on_modified);
  }

  /**
   * Return form fields for the given selectors of the config
   */
  get_form_fields(form) {
    console.debug(`EditForm::get_form_fields(${form})`);
    let fields = [];
    let selectors = this.config.field_selectors;
    for (const selector of selectors) {
      let nodes = form.querySelectorAll(selector);
      fields = fields.concat(...nodes.values())
    }
    return fields
  }

  /**
   * Checks if the element is a textarea field
   */
  is_textarea(el) {
    return el.tagName == "TEXTAREA";
  }

  /**
   * Checks if the element is a select field
   */
  is_select(el) {
    return el.tagName == "SELECT";
  }

  /**
   * Checks if the element is an input field
   */
  is_input(el) {
    return el.tagName === "INPUT";
  }

  /**
   * Checks if the element is an input[type='text'] field
   */
  is_text(el) {
    return this.is_input(el) && el.type === "text";
  }

  /**
   * Checks if the element is an input[type='checkbox'] field
   */
  is_checkbox(el) {
    return this.is_input(el) && el.type === "checkbox";
  }

  /**
   * Checks if the element is an input[type='radio'] field
   */
  is_radio(el) {
    return this.is_input(el) && el.type === "radio";
  }

  /**
   * Checks if the element is a SENAITE reference field
   */
  is_reference(el) {
    return el.classList.contains("referencewidget");
  }

  /**
   * Checks if the element is a SENAITE single-reference field
   */
  is_single_reference(el) {
    return this.is_reference(el) && el.getAttribute("multivalued") == "0";
  }

  /**
   * Checks if the element is a SENAITE multi-reference field
   */
  is_multi_reference(el) {
    return this.is_reference(el) && el.getAttribute("multivalued") == "1";
  }

  /**
   * toggles the display of the field with the `d-none` class
   */
  toggle_field_visibility(field, toggle) {
    let parent = field.closest(".field");
    let css_class = "d-none";
    if (toggle === false) {
      parent.classList.add(css_class);
    } else {
      parent.classList.remove(css_class);
    }
  }

  /**
   * flush all field errors
   */
  flush_errors(form) {
    let fields_with_errors = document.querySelectorAll(".is-invalid");
    for (const field of fields_with_errors) {
      this.remove_field_error(field);
    }
  }

  /**
   * set field error
   */
  set_field_error(field, message) {
    field.classList.add("is-invalid");
    if (message) {
      let div = document.createElement("div");
      div.className = "invalid-feedback";
      div.innerHTML = message;
      field.parentElement.appendChild(div);
    }
  }

  /**
   * add a status message
   */
  add_statusmessage(message, level="info") {
    let el  = document.createElement("div");
    el.innerHTML = `
      <div class="alert alert-${level} alert-dismissible fade show" role="alert">
        <strong>${level.charAt(0).toUpperCase() + level.slice(1)}</strong>
        ${message}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
    `
    el = el.firstElementChild
    let parent = document.getElementById("viewlet-above-content");
    parent.appendChild(el);
    return el;
  }

  /**
   * remove field error
   */
  remove_field_error(field) {
    field.classList.remove("is-invalid")
    let msg = field.parentElement.querySelector(".invalid-feedback");
    if (msg) {
      msg.remove();
    }
  }

  /**
   * update the form with the response from the server
   */
  update_form(form, data) {
    console.info("*** UPDATE FORM ***", data)

    let hide = data.hide || [];
    let show = data.show || [];
    let update = data.update || {};
    let messages = data.messages || [];
    let errors = data.errors || {};

    // flush all field errors
    this.flush_errors();

    // render field errors
    for (const [key, value] of Object.entries(errors)) {
      let el = this.get_form_field_by_name(form, key);
      if (!el) continue;
      this.set_field_error(el, value);
    }

    // render status messages
    for (const item of messages) {
      let level = item.level || "info";
      let message = item.message || "";
      this.add_statusmessage(message, level);
    }

    // hide fields
    for (const selector of hide) {
      let el = this.get_form_field_by_name(form, selector);
      if (!el) continue;
      this.toggle_field_visibility(el, false);
    }

    // show fields
    for (const selector of show) {
      let el = this.get_form_field_by_name(form, selector);
      if (!el) continue;
      this.toggle_field_visibility(el, true);
    }

    // updated fields
    for (const [key, value] of Object.entries(update)) {
      console.log(`Update ${key} -> ${value}`);
      let el = this.get_form_field_by_name(form, key);
      if (!el) continue;
      this.set_field_value(el, value);
    }
  }

  /**
   * return a form field by name
   */
  get_form_field_by_name(form, name) {
    // get the first element that matches the name
    let el = form.querySelector(`[name^='${name}']`);
    if (!el) {
      return null;
    }
    return el;
  }

  /**
   * return a dictionary of all the form values
   */
  get_form_data(form) {
    let data = {};
    let form_data = new FormData(form);
    form_data.forEach(function(value, key) {
      data[key] = value;
    });
    return data;
  }

  /**
   * set the value of the form field
   */
  set_field_value(field, value) {
    // for reference/select fields
    let selected = value.selected || [];
    let options = value.options || [];

    // set reference value
    if (this.is_single_reference(field)) {
      for (const item of selected) {
        field.setAttribute("uid", item.value);
        field.value = item.title;
      }
    }
    // set select field
    else if (this.is_select(field)) {
      // TODO: filtering options first
      for (const item of selected) {
        field.value = item.value;
      }
    }
    // set checkbox value
    else if (this.is_checkbox(field)) {
      field.checked = value;
    }
    // set other field values
    else {
      field.value = value;
    }
  }

  /**
   * return the value of the form field
   */
  get_field_value(field) {
    if (this.is_checkbox(field)) {
      // returns true/false for checkboxes
      return field.checked;
    } else if (this.is_select(field)) {
      // returns a list of selected option
      let selected = field.selectedOptions;
      return Array.prototype.map.call(selected, (option) => option.value)
    } else if (this.is_single_reference(field)) {
      // returns the value of the `uid` attribute
      return field.getAttribute("uid");
    } else if (this.is_multi_reference(field)) {
      // returns the value of the `uid` attribute and splits it on `,`
      let uids = field.getAttribute("uid");
      if (uids.length == 0) return [];
      return uids.split(",");
    }
    // return the plain field value
    return field.value;
  }

  /**
   * returns the name of the field w/o ZPublisher converter
   */
  get_field_name(field) {
    let name = field.name;
    return name.split(":")[0];
  }


  /**
   * notify a field change to the server ajax endpoint
   */
  notify(form, field, endpoint) {
    let data = {
      name: this.get_field_name(field),
      value: this.get_field_value(field),
    }
    this.ajax_send(form, data, endpoint);
  }

  /**
   * send ajax request to the server
   */
  ajax_send(form, data, endpoint) {
    let view_url = document.body.dataset.viewUrl;
    let ajax_url = `${view_url}/ajax_form/${endpoint}`;

    let payload = Object.assign({
      "form": this.get_form_data(form)
    }, data)

    let init = {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(payload),
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": document.querySelector("#protect-script").dataset.token
      },
    }

    // send ajax request to server
    let request = new Request(ajax_url, init);
    fetch(request)
      .then((response) => {
        if (!response.ok) {
          return Promise.reject(response);
        }
        return response.json();
      })
      .then((data) => {
        console.debug("GOT JSON RESPONSE --> ", data);
        this.update_form(form, data);
      })
      .catch((error) => {
        console.error(error);
      });
  }

  /**
   * trigger `modified` event on the form
   */
  modified(el) {
    let event = new CustomEvent("modified", {
      detail: {
        field: el,
        form: el.form
      }
    });
    // dispatch the event on the element
    el.form.dispatchEvent(event);
  }

  /**
   * event handler for `modified` event
   */
  on_modified(event) {
    console.debug("EVENT -> on_modified");
    let form = event.detail.form;
    let field = event.detail.field;
    this.notify(form, field, "modified");
  }

  /**
   * event handler for `blur` event
   */
  on_blur(event) {
    console.debug("EVENT -> on_blur");
    let el = event.currentTarget;
    this.modified(el);
  }

  /**
   * event handler for `click` event
   */
  on_click(event) {
    console.debug("EVENT -> on_click");
    let el = event.currentTarget;
    this.modified(el);
  }

  /**
   * event handler for `change` event
   */
  on_change(event) {
    console.debug("EVENT -> on_change");
    let el = event.currentTarget;
    this.modified(el);
  }

}

export default EditForm;
