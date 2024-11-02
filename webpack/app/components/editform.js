/* SENAITE Edit Form Handler
 *
 * This code handles field changes in edit forms and updates others according to
 * the changes with the help of adapters.
 *
 */

// needed for Bootstrap toasts
import $ from "jquery";


class EditForm {

  constructor(config) {
    this.config = Object.assign({
      "form_selectors": [],
      "field_selectors": []
    }, config);

    this.hooked_fields = [];

    // bind event handlers
    this.on_mutated = this.on_mutated.bind(this);
    this.on_modified = this.on_modified.bind(this);
    this.on_submit = this.on_submit.bind(this);
    this.on_blur = this.on_blur.bind(this);
    this.on_click = this.on_click.bind(this);
    this.on_change = this.on_change.bind(this);
    this.on_reference_select = this.on_reference_select.bind(this);
    this.on_reference_deselect = this.on_reference_deselect.bind(this);
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
      this.hook_field(field)
    }
    // observe DOM mutations in form
    this.observe_mutations(form);
    // bind custom form event handlers
    form.addEventListener("modified", this.on_modified);
    form.addEventListener("mutated", this.on_mutated);
    if (form.hasAttribute("ajax-submit")) {
      form.addEventListener("submit", this.on_submit);
    }
  }

  /**
   * Bind event handlers to field
   */
  hook_field(field) {
    // return immediately if the fields is already hooked
    if (this.hooked_fields.indexOf(field) !== -1) {
      // console.debug(`Field '${field.name}' is already hooked`);
      return
    }
    if (this.is_button(field) || this.is_input_button(field)) {
      // bind click event
      field.addEventListener("click", this.on_click);
    }
    else if (this.is_reference(field)) {
      // bind custom events from the ReactJS queryselect widget
      field.addEventListener("select", this.on_reference_select);
      field.addEventListener("deselect", this.on_reference_deselect);
    }
    else if (this.is_text(field) || this.is_textarea(field)) {
      // bind change event
      field.addEventListener("change", this.on_change);
    }
    else if (this.is_select(field)) {
      // bind events for select field
      field.addEventListener("click", this.on_click);
      field.addEventListener("change", this.on_change);
    }
    else if (this.is_radio(field) || this.is_checkbox(field)) {
      // bind click event
      field.addEventListener("click", this.on_click);
    } else {
      // bind blur event
      field.addEventListener("blur", this.on_blur);
    }
    // console.debug(`Hooked field '${field.name}'`);
    // remember hooked fields
    this.hooked_fields = this.hooked_fields.concat(field);
  }

  /**
   * Initialize a DOM mutation observer to rebind dynamic added fields,
   * e.g. for records field etc.
   */
  observe_mutations(form) {
    let observer = new MutationObserver(function(mutations) {
      let event = new CustomEvent("mutated", {
        detail: {
          form: form,
          mutations: mutations
        }
      });
      form.dispatchEvent(event);
    });
    // observe the form with all contained elements
    observer.observe(form, {
      childList: true,
      subtree: true
    });
  }

  /**
   * Handle a single DOM mutation
   */
  handle_mutation(form, mutation) {
    let target = mutation.target;
    let parent = target.closest(".field");
    let added = mutation.addedNodes;
    let removed = mutation.removedNodes;
    let selectors = this.config.field_selectors;
    // handle picklist widget
    if (this.is_multiple_select(target)) {
      return this.notify(form, target, "modified");
    }
    // hook new fields, e.g. when the records field "More" button was clicked
    if (added && target.ELEMENT_NODE) {
      for (const field of target.querySelectorAll(selectors)) {
        this.hook_field(field);
      }
    }
    // notify new added elements, e.g. when a category was expanded or the
    // "show more" button was clicked in listings
    if (added.length > 0) {
      return this.notify_added(form, added, "added")
    }
  }

  /**
   * toggles the submit button
   */
  toggle_submit(form, toggle) {
    let btn = form.querySelector("input[type='submit']");
    btn.disabled = !toggle;
  }

  /**
   * toggles the display of the field with the `d-none` class
   */
  toggle_field_visibility(field, toggle=true) {
    let parent = field.closest(".field");
    let css_class = "d-none";
    if (toggle === false) {
      parent.classList.add(css_class);
    } else {
      parent.classList.remove(css_class);
    }
  }

  /**
   * check if fields have errors
   */
  has_field_errors(form) {
    let fields_with_errors = form.querySelectorAll(".is-invalid");
    if (fields_with_errors.length > 0) {
      return true;
    }
    return false;
  }

  /**
   * set field readonly
   */
  set_field_readonly(field, message=null) {
    field.setAttribute("readonly", "");
    // Only text controls can be made read-only, since for other controls (such
    // as checkboxes and buttons) there is no useful distinction between being
    // read-only and being disabled. We cover other controls like select here.
    field.setAttribute("disabled", "");
    let existing_message = field.parentElement.querySelector("div.message");
    if (existing_message) {
      existing_message.innerHTML = _t(message)
    } else {
      let div = document.createElement("div");
      div.className = "message text-secondary small";
      div.innerHTML = _t(message);
      field.parentElement.appendChild(div);
    }
  }

  /**
   * set field editable
   */
  set_field_editable(field, message=null) {
    field.removeAttribute("readonly");
    // Only text controls can be made read-only, since for other controls (such
    // as checkboxes and buttons) there is no useful distinction between being
    // read-only and being disabled. We cover other controls like select here.
    field.removeAttribute("disabled");
    let existing_message = field.parentElement.querySelector("div.message");
    if (existing_message) {
      existing_message.innerHTML = _t(message)
    } else {
      let div = document.createElement("div");
      div.className = "message text-secondary small";
      div.innerHTML = _t(message);
      field.parentElement.appendChild(div);
    }
  }

  /**
   * set field error
   */
  set_field_error(field, message) {
    field.classList.add("is-invalid");
    let existing_message = field.parentElement.querySelector("div.invalid-feedback");
    if (existing_message) {
      existing_message.innerHTML = _t(message)
    } else {
      let div = document.createElement("div");
      div.className = "invalid-feedback";
      div.innerHTML = _t(message);
      field.parentElement.appendChild(div);
    }
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
   * add a status message
   * @param {string} message the message to display in the alert
   * @param {string} level   one of "info", "success", "warning", "danger"
   * @param {object} options additional options to control the behavior
   *                 - option {string} title: alert title in bold
   *                 - option {string} flush: remove previous alerts
   */
  add_statusmessage(message, level="info", options) {
    options = options || {};
    let el = document.createElement("div");
    let title = options.title || `${level.charAt(0).toUpperCase() + level.slice(1)}`;
    el.innerHTML = `
      <div class="alert alert-${level} alert-dismissible fade show" role="alert">
        <strong>${title}</strong>
        ${_t(message)}
        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
    `
    el = el.firstElementChild
    let parent = document.getElementById("viewlet-above-content");

    // clear put previous alerts
    if (options.flush) {
      for (let el of parent.querySelectorAll(".alert")) {
        el.remove();
      }
    }
    parent.appendChild(el);
    return el;
  }

  /**
   * add a notification message
   */
  add_notification(title, message, options) {
    options = options || {};
    options = Object.assign({
      animation: true,
      autohide: true,
      delay: 5000,
    }, options)
    let el = document.createElement("div");
    el.innerHTML = `
      <div class="toast" style="width:300px" role="alert"
           data-animation="${options.animation}"
           data-autohide="${options.autohide}"
           data-delay="${options.delay}">
        <div class="toast-header">
          <strong class="mr-auto">${title.charAt(0).toUpperCase() + title.slice(1)}</strong>
          <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="toast-body">
          ${_t(message)}
        </div>
      </div>
    `
    el = el.firstElementChild;
    let parent = document.querySelector(".toast-container");
    if (!parent) {
      parent = document.createElement("div");
      parent.innerHTML = `
        <div style="position: fixed; top: 0px; right: 0px; width=100%;">
          <div class="toast-container" style="position: absolute; top: 10px; right: 10px;">
          </div>
        </div>
      `
      let wrapper = document.querySelector(".container-fluid");
      wrapper.appendChild(parent);
      parent = parent.querySelector(".toast-container");
    }
    parent.appendChild(el);
    return el;
  }

  /**
   * update the form with the response from the server
   */
  update_form(form, data) {
    console.info("*** UPDATE FORM ***", data)

    let hide = data.hide || [];
    let show = data.show || [];
    let readonly = data.readonly || [];
    let editable = data.editable || [];
    let errors = data.errors || [];
    let messages = data.messages || [];
    let notifications = data.notifications || [];
    let updates = data.updates || [];
    let html = data.html || [];
    let attributes = data.attributes || [];
    let callbacks = data.callbacks || [];

    // render field errors
    for (const record of errors) {
      let name, error, rest;
      ({name, error, ...rest} = record);
      let el = this.get_form_field_by_name(form, name);
      if (!el) continue;
      if (error) {
        this.set_field_error(el, error);
      } else {
        this.remove_field_error(el);
      }
    }

    // render status messages
    for (const record of messages) {
      let name, error, rest;
      ({message, level, ...rest} = record);
      let level = level || "info";
      let message = message || "";
      this.add_statusmessage(message, level, rest);
    }

    // render notification messages
    for (const record of notifications) {
      let title, message, rest;
      ({title, message, ...rest} = record);
      let el = this.add_notification(title, message, rest);
      $(el).toast("show");
    }

    // hide fields
    for (const record of hide) {
      let name, rest;
      ({name, ...rest} = record);
      let el = this.get_form_field_by_name(form, name);
      if (!el) continue;
      this.toggle_field_visibility(el, false);
    }

    // show fields
    for (const record of show) {
      let name, rest;
      ({name, ...rest} = record);
      let el = this.get_form_field_by_name(form, name);
      if (!el) continue;
      this.toggle_field_visibility(el, true);
    }

    // readonly fields
    for (const record of readonly) {
      let name, message, rest;
      ({name, message, ...rest} = record);
      let el = this.get_form_field_by_name(form, name);
      if (!el) continue;
      this.set_field_readonly(el, message);
    }

    // editable fields
    for (const record of editable) {
      let name, message, rest;
      ({name, message, ...rest} = record);
      let el = this.get_form_field_by_name(form, name);
      if (!el) continue;
      this.set_field_editable(el, message);
    }

    // updated fields
    for (const record of updates) {
      let name, value, rest;
      ({name, value, ...rest} = record);
      let el = this.get_form_field_by_name(form, name);
      if (!el) continue;
      this.set_field_value(el, value);
    }

    // html
    for (const record of html) {
      let selector, html, rest;
      ({selector, html, ...rest} = record);
      let el = form.querySelector(selector);
      if (!el) continue;
      if (rest.append) {
        el.innerHTML = el.innerHTML + html;
      } else {
        el.innerHTML = html;
      }
    }

    // set attribute to an element
    for (const record of attributes) {
      let selector, name, value, rest;
      ({selector, name, value, ...rest} = record);
      let el = form.querySelector(selector);
      if (!el) continue;
      if (value === null) {
        el.removeAttribute(name);
      } else {
        el.addAttribute(name, value);
      }
    }

    // register callbacks
    for (const record of callbacks) {
      let selector, event, name, rest;
      ({selector, event, name, ...rest} = record);
      // register local callback to apply additional data
      let callback = (event) => {
        let data = {
          name: name,
          target: event.currentTarget
        }
        this.ajax_send(form, data, "callback");
      }

      if (selector === "document") {
        document.addEventListener(event, callback);
      } else {
        document.querySelectorAll(selector).forEach((el) => {
          el.addEventListener(event, callback);
        });
      }
    }

    // disallow submit when field errors are present
    if (this.has_field_errors(form)) {
      this.toggle_submit(form, false);
    } else {
      this.toggle_submit(form, true);
    }
  }

  /**
   * return a form field by name
   */
  get_form_field_by_name(form, name) {
    // get the first element that matches the name
    let exact = form.querySelector(`[name='${name}']`);
    let fuzzy = form.querySelector(`[name^='${name}']`);
    let field = exact || fuzzy || null;
    if (field === null) {
      return null;
    }
    return field;
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
    // handle DX add views
    let view_name = this.get_view_name();
    if (view_name.indexOf("++add++") > -1) {
      // inject `form_adapter_name` for named multi adapter lookup
      // see senaite.core.browser.form.ajax.FormView for lookup logic
      data.form_adapter_name = view_name;
    }
    return data;
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
   * returns the name of the field w/o ZPublisher converter
   */
  get_field_name(field) {
    let name = field.name;
    return name.split(":")[0];
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
    } else if (this.is_reference(field)) {
      return field.value.split("\n");
    }
    // return the plain field value
    return field.value;
  }

  /**
   * set the value of the form field
   */
  set_field_value(field, value) {
    // for reference/select fields
    let selected = value.selected || [];
    let options = value.options || [];

    // set reference value
    if (this.is_reference(field)) {
      field.value = selected.join("\n");
    }
    // set select field
    else if (this.is_select(field)) {
      if (selected.length == 0) {
        let old_selected = field.options[field.selected];
        if (old_selected) {
          selected = [old_selected.value];
        }
      }
      // remove all options
      field.options.length = 0;
      // sort options
      options.sort((a, b) => {
        let _a = a.title.toLowerCase();
        let _b = b.title.toLowerCase();
        if (a.value === null) _a = "";
        if (b.value === null) _b = "";
        if (_a < _b) return -1;
        if (_a > _b) return 1;
      });
      // build new options
      for (const option of options) {
        let el = document.createElement("option");
        el.value = option.value;
        el.innerHTML = option.title;
        // select item if the value is in the selected array
        if (selected.indexOf(option.value) !== -1) {
          el.selected = true;
        }
        field.appendChild(el);
      }
      // select first item
      if (selected.length == 0) {
        field.selectedIndex = 0;
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
   * trigger ajax loading events
   */
  loading(toggle=true) {
    let event_type = toggle ? "ajaxStart" : "ajaxStop";
    let event = new CustomEvent(event_type);
    document.dispatchEvent(event);
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
   * notify that DOM Elements were added
   */
  notify_added(form, added, endpoint) {
    let data = {
      added: []
    }
    added.forEach((el) => {
      let record = {};
      if (el.attributes && el.attributes.length > 0) {
        for (let attribute of el.attributes) {
          let name = attribute.name;
          let value = attribute.value;
          record[name] = value;
        }
      }
      if (Object.keys(record).length > 0) {
        data.added.push(record);
      }
    });
    this.ajax_send(form, data, endpoint);
  }

  /**
   * send application/json to the server
   */
  ajax_send(form, data, endpoint) {
    let view_url = document.body.dataset.viewUrl;
    let ajax_url = `${view_url}/ajax_form/${endpoint}`;

    let payload = Object.assign({
      form: this.get_form_data(form)
    }, data)

    console.debug("EditForm::ajax_send --> ", payload)

    let init = {
      method: "POST",
      credentials: "include",
      body: JSON.stringify(payload),
      headers: {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": document.querySelector("#protect-script").dataset.token
      },
    }

    return this.ajax_request(form, ajax_url, init);
  }

  /**
   * send multipart/form-data to the server
   *
   * NOTE: This is used by the import form and hooked by the `ajax-submit="1"` attribute
   *       Therefore, we send here the data as multipart/form-data
   */
  ajax_submit(form, data, endpoint) {
    let view_url = document.body.dataset.viewUrl;
    let ajax_url = `${view_url}/ajax_form/${endpoint}`;

    let payload = new FormData(form);

    // update form data
    for(let [key, value] of Object.entries(data)) {
      payload.set(key, value);
    }

    console.debug("EditForm::ajax_submit --> ", payload)

    let init = {
      method: "POST",
      body: payload,
    }

    return this.ajax_request(form, ajax_url, init);
  }


  /**
   * execute ajax request
   */
  ajax_request(form, url, init) {
    // send ajax request to server
    this.loading(true);
    let request = new Request(url, init);
    return fetch(request)
      .then((response) => {
        if (!response.ok) {
          return Promise.reject(response);
        }
        return response.json();
      })
      .then((data) => {
        console.debug("EditForm::ajax_request --> ", data);
        this.update_form(form, data);
        this.loading(false);
      })
      .catch((error) => {
        console.error(error);
        this.loading(false);
      });
  }


  /**
   * get the current view name from the URL
   */
  get_view_name() {
    let segments = location.pathname.split("/");
    return segments.pop();
  }

  /**
   * Toggle element disable
   */
  toggle_disable(el, toggle) {
    if (el) {
      el.disabled = toggle;
    }
  }

  /**
   * Checks if the element is a textarea field
   */
  is_textarea(el) {
    return el.tagName == "TEXTAREA";
  }

  /**
   * Checks if the elment is a select field
   */
  is_select(el) {
    return el.tagName == "SELECT";
  }

  /**
   * Checks if the element is a multiple select field
   */
  is_multiple_select(el) {
    return this.is_select(el) && el.hasAttribute("multiple");
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
   * Checks if the element is a button field
   */
  is_button(el) {
    return el.tagName === "BUTTON";
  }

  /**
   * Checks if the element is an input[type='button'] field
   */
  is_input_button(el) {
    return this.is_input(el) && el.type === "button";
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
   * Checks if the element is a SENAITE reference field (textarea)
   */
  is_reference(el) {
    if (!this.is_textarea(el)) {
      return false;
    }
    return el.classList.contains("queryselectwidget-value");
  }

  /**
   * Checks if the element is a table row element
   */
  is_table_row(el) {
    return el.tagName === "TR";
  }
  /**
   * event handler for `mutated` event
   */
  on_mutated(event) {
    console.debug("EditForm::on_mutated");
    let form = event.detail.form;
    let mutations = event.detail.mutations;
    // reduce multiple mutations on the same node to one
    let seen = [];
    for (const mutation of mutations) {
      if (seen.indexOf(mutation.target) > -1) {
        continue;
      }
      seen = seen.concat(mutation.target);
      this.handle_mutation(form, mutation);
    }
  }

  /**
   * event handler for `modified` event
   */
  on_modified(event) {
    console.debug("EditForm::on_modified");
    let form = event.detail.form;
    let field = event.detail.field;
    this.notify(form, field, "modified");
  }

  /**
   * event handler for `submit` event
   */
  on_submit(event) {
    console.debug("EditForm::on_submit");
    event.preventDefault();
    let data = {}
    let form = event.currentTarget.closest("form");
    // NOTE: submit input field not included in request form data!
    let submitter = event.submitter;
    if (submitter) {
      data[submitter.name] = submitter.value;
      // disable submit button during ajax call
      this.toggle_disable(submitter, true);
    }
    this.ajax_submit(form, data, "submit")
      .then((response) =>
        // enable submit button after ajax call again
        this.toggle_disable(submitter, false));
  }

  /**
   * event handler for `blur` event
   */
  on_blur(event) {
    console.debug("EditForm::on_blur");
    let el = event.currentTarget;
    this.modified(el);
  }

  /**
   * event handler for `click` event
   */
  on_click(event) {
    console.debug("EditForm::on_click");
    let el = event.currentTarget;
    this.modified(el);
  }

  /**
   * event handler for `change` event
   */
  on_change(event) {
    console.debug("EditForm::on_change");
    let el = event.currentTarget;
    this.modified(el);
  }

  /**
   * event handler for `select` event
   */
  on_reference_select(event) {
    console.debug("EditForm::on_reference_select");
    let el = event.currentTarget;
    // add the selected value to the list
    let selected = el.value.split("\n");
    selected = selected.concat(event.detail.value);
    el.value = selected.join("\n");
    this.modified(el);
  }

  /**
   * event handler for `deselect` event
   */
  on_reference_deselect(event) {
    console.debug("EditForm::on_reference_deselect");
    let el = event.currentTarget;
    // remove the delelected value from the list
    let selected = el.value.split("\n");
    let index = selected.indexOf(event.detail.value);
    if (index > -1) {
      selected.splice(index, 1)
    }
    el.value = selected.join("\n");
    this.modified(el);
  }

}

export default EditForm;
