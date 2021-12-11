document.addEventListener("DOMContentLoaded", () => {

  class DateTimeWidget {

    constructor() {
      let datefields = document.querySelectorAll("input[type='date']");
      let timefields = document.querySelectorAll("input[type='time']");

      // bind event handlers
      this.update_date = this.update_date.bind(this);
      this.on_change = this.on_change.bind(this);

      // bind datefields
      datefields.forEach((el, idx) => {
        el.addEventListener("change", this.on_change);
      });

      // bind timefields
      timefields.forEach((el, idx) => {
        el.addEventListener("change", this.on_change);
      });
    }

    get_default_date() {
      // returns the default date
      let dt = new Date();
      let ds = dt.toISOString()
      return ds.substring(0, ds.lastIndexOf("T"))
    }

    set_field(field, value) {
      if (!field) return;
      field.value = value;
    }

    update_date(date, time, input) {
      // console.debug("DateTimeWidget::update_date");
      let ds = date ? date.value : null;
      let ts = time ? time.value : null;

      if (!ds) ds = this.get_default_date();
      if (!ts) ts = "00:00";

      // set the values of the fields
      this.set_field(date, ds);
      this.set_field(time, ts);

      if (date && time) {
        // set date and time
        this.set_field(input, `${ds}T${ts}`);
      } else {
        // set date only
        this.set_field(input, `${ds}`);
      }
    }

    on_change(event) {
      // console.debug("DateTimeWidget::on_change");
      let el = event.currentTarget;
      let target = el.getAttribute("target");

      // for simplicity, we just fetch all the required elements here
      let date = el.parentElement.querySelector("input[type='date']");
      let time = el.parentElement.querySelector("input[type='time']");
      let input = document.querySelector(`input[name='${target}']`);

      // always write the full date to the hidden field
      this.update_date(date, time, input);
    }
  }

  new DateTimeWidget();
});
