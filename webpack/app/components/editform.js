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
        this.watch_form(form);
      }
    }
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

  notify_change(form, field) {
    let view_url = document.body.dataset.viewUrl;
    let ajax_url = `${view_url}/ajax_form/modified`;
    let form_data = new FormData(form);

    let init = {
      method: "POST",
      credentials: "include",
      body: JSON.stringify({
        name: field.name,
        value: field.value,
        formdata: JSON.stringify(form_data)
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
        console.info("*** GOT RESPONSE JSON ***", data)
      })
      .catch(function(error) {
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
