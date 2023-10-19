import React from "react";
import "./SelectedValues.css"


class SelectedValues extends React.Component {

  constructor(props) {
    super(props);

    this.on_change = this.on_change.bind(this);
    this.on_deselect = this.on_deselect.bind(this);
  }

  componentDidMount() {
    this.init_confirmation();
  }

  componentDidUpdate() {
    this.init_confirmation();
  }

  get_selected_values() {
    return this.props.values || [];
  }

  init_confirmation() {
    $("[data-toggle=confirmation]").confirmation({
      rootSelector: "[data-toggle=confirmation]",
      btnOkLabel: _t("Yes"),
      btnOkClass: "btn btn-outline-primary",
      btnOkIconClass: "fas fa-check-circle mr-1",
      btnCancelLabel: _t("No"),
      btnCancelClass: "btn btn-outline-secondary",
      btnCancelIconClass: "fas fa-circle mr-1",
      container: "body",
      singleton: true
    });
  }

  /*
   * Simple template interpolation that replaces ${...} placeholders
   * with any found value from the context object.
   *
   * https://stackoverflow.com/questions/29182244/convert-a-string-to-a-template-string
   */
  interpolate(template, context) {
    for(let [key, value] of Object.entries(context)) {
      template = template.replace(new RegExp('\\$\\{' + key + '\\}', 'g'), value)
    }
    return template;
  }

  render_display_template(value) {
    let template = this.props.display_template;
    if (!template) return value;
    let context = this.props.records[value];
    // return the raw value if there is no replacement data
    let broken_ref = `<span title='broken reference ${value}' class='text-danger'>${value}</span>`;
    if (!context) return broken_ref;
    if (typeof context === 'object' && Object.keys(context).length === 0) return broken_ref;
    return this.interpolate(template, context);
  }

  build_selected_items() {
    let items = [];
    let selected_values = this.get_selected_values();
    let readonly = this.props.readonly;

    for (let value of selected_values) {
      let context = this.props.records[value] || {};
      let review_state = context.review_state || "default";
      items.push(
        <li value={value} className="d-inline-block">
          <div className="d-flex flex-nowrap p-1 mb-1 mr-1 bg-light border rounded field-validation">
            <span className={"state-" + review_state}
                  dangerouslySetInnerHTML={{__html: this.render_display_template(value)}}></span>
            {!readonly &&
            <button value={value}
                    data-toggle="confirmation"
                    data-title={_t("Unlink reference?")}
                    className="btn btn-sm p-0 ml-2"
                    onClick={this.on_deselect}>
              <i className="fas fa-times-circle"></i>
            </button>}
          </div>

        </li>
      );
    }
    return items
  }

  /*
   * Callback when the textarea field was changed
   * Note: This will be useful when the field is used in the sample add form
   */
  on_change(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let value = target.value;
    let values = value.split("\n");
    // filter out empties
    values = values.filter(x => x);
    // set new values directly
    if (this.props.set_values) {
      this.props.set_values(values);
    }
  }

  on_deselect(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let value = target.getAttribute("value");
    console.debug("SelectedValues::on_deselect: Remove value", value);
    if (this.props.on_deselect) {
      this.props.on_deselect(value);
    }
  }

  render() {
    return (
      <div className="queryselectwidget-selected-values">
        <ul className="list-unstyled d-table-row">
          {this.build_selected_items()}
        </ul>
        {/* submitted in form */}
        <textarea
          className="d-none queryselectwidget-value"
          onChange={this.on_change}
          name={this.props.name}
          value={this.props.values.join("\n")}
        />
      </div>
    );
  }
}

export default SelectedValues;
