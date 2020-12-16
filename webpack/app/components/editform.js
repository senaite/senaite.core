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
    this.on_input = this.on_input.bind(this);
    this.on_blur = this.on_blur.bind(this);
    // init form
    this.init_forms();
    this.changed = {};
  }

  /**
   * Initialize all form elements
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

  setup_form(form) {
    console.debug(`EditForm::setup_form(${form})`);
    this.submit(form, {}, "initialized");
  }

  watch_form(form) {
    console.debug(`EditForm::watch_form(${form})`);
    let fields = this.get_form_fields(form);
    for (const field of fields) {
        console.debug(`[Watching field ${field.name}]`);
        field.addEventListener("input", this.on_input);
        field.addEventListener("blur", this.on_blur);
    }
    form.addEventListener("modified", this.on_modified);
  }

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

  set_change_flag(el, flag) {
    let name = el.name;
    this.changed[name] = flag;
  }

  toggle_field_visibility(field, toggle) {
    let parent = field.closest(".field");
    let css_class = "d-none";
    if (toggle === false) {
      parent.classList.add(css_class);
    } else {
      parent.classList.remove(css_class);
    }
  }

  update_form(form, data) {
    console.info("*** UPDATE FORM ***", data)
    let hide = data.hide || [];
    let show = data.show || [];
    let update = data.update || {}

    for (const selector of hide) {
      let el = form.querySelector(`[data-fieldname='${selector}']`);
      if (!el) continue;
      this.toggle_field_visibility(el, false);
    }

    for (const selector of show) {
      let el = form.querySelector(`[data-fieldname='${selector}']`);
      if (!el) continue;
      this.toggle_field_visibility(el, true);
    }

    for (const [key, value] of Object.entries(update)) {
      console.log(`Update ${key} -> ${value}`);
      let el = form.querySelector(`[data-fieldname='${key}']`);
      if (!el) continue;
      let input = el.querySelector(`[name='${key}']`);
      if (!input) continue;
      input.value = value;
    }
  }

  notify_change(form, field) {
    let data = {
      name: field.name,
      value: field.value,
    }
    this.submit(form, data, "modified");
  }

  get_form_data(form) {
    let data = {};
    let form_data = new FormData(form);
    form_data.forEach(function(value, key) {
      data[key] = value;
    });
    return data;
  }

  submit(form, data, endpoint) {
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

    let request = new Request(ajax_url, init);

    fetch(request)
      .then((response) => {
        if (!response.ok) {
          return Promise.reject(response);
        }
        return response.json();
      })
      .then((data) => {
        this.update_form(form, data);
      })
      .catch((error) => {
        console.error(error);
      });
  }

  on_modified(event) {
    console.info(`Field '${event.detail.name}' changed value to '${event.detail.value}'`);
    let form = event.detail.form;
    let field = event.detail.field;
    this.notify_change(form, field);
  }

  on_input(event) {
    let el = event.currentTarget;
    this.set_change_flag(el, true);
  }

  on_blur(event) {
    let el = event.currentTarget;
    let name = el.name;
    let value = el.value;
    if (this.changed[name]) {
      let event = new CustomEvent("modified", {
        detail: {
          field: el,
          name: name,
          value: value,
          form: el.form
        }
      });
      // dispatch the event on the element
      el.form.dispatchEvent(event);
      // set back the change flag
      this.set_change_flag(el, false)
    }
  }

}

export default EditForm;
