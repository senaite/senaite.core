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

    /**
     * set an input field value (if the field exists)
     * @param {object} field input field
     * @param {string} value the value the should get set on the field
     */
    set_field(field, value) {
      if (!field) return;
      field.value = value;
    }

    /**
      * generate a full date w/o TZ from the date and time inputs
      * @param {object} date the date input field
      * @param {object} time the time input field
      * @param {object} hidden hidden field that contains the full date for from submission
    */
    update_date(date, time, input) {
      // console.debug("DateTimeWidget::update_date");
      let ds = date ? date.value : "";
      let ts = time ? time.value : "";

      // set the values of the fields
      this.set_field(date, ds);
      this.set_field(time, ts);

      if (ds && ts) {
        // set date and time
        this.set_field(input, `${ds} ${ts}`);
      } else if (ds) {
        // set date only
        this.set_field(input, `${ds}`);
      } else {
        this.set_field(input, "");
      }
    }

    /**
     * event handler for `change` event
     *
     * collect the date/time and hidden input of the field
     * and set the full date for form submission.
     *
     * Fires when the date/time changes
     * https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/date
     */
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
