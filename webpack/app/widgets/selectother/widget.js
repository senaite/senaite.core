import React from "react"
import ReactDOM from "react-dom"

class SelectOtherWidgetController extends React.Component{

  constructor(props) {
    super(props);

    // Root input HTML element
    this.root_el = props.root_el;

    this.state = {};

    // Data keys located at the root element
    // -> initial values are set from the widget class
    const data_keys = [
      "id",
      "name",
      "choices",
      "option",
      "option_other",
      "other",
    ];

    // Query data keys and set state with parsed JSON value
    for (let key of data_keys) {
      let value = this.root_el.dataset[key];
      if (value === undefined) {
        continue;
      }
      this.state[key] = this.parse_json(value);
    }

    // Bind callbacks to current context
    this.on_option_change = this.on_option_change.bind(this);
    this.on_other_change = this.on_other_change.bind(this);

    return this;
  }

  /*
   * JSON parse the given value
   *
   * @param {String} value: The JSON value to parse
   */
  parse_json(value) {
    try {
      return JSON.parse(value);
    } catch (error) {
      console.error(`Could not parse "${value}" to JSON`);
    }
  }

  /**
   * Event triggered when the user selects an option from the selection list.
   * If the selection option is other than `__other__`, the state variable
   * `other` is flushed
   */
  on_option_change(event) {
    let value = event.target.value;
    if (value != this.state.option_other) {
      this.setState({other: ""});
    }
    this.setState({option: value});
  }

  on_other_change(event) {
    this.setState({other: event.target.value});
  }

  /*
   * Checks if the text field for manual entry of should be rendered
   * @returns {Boolean} true/false if the search field is rendered
   */
  show_other_field() {
    return this.state.option === this.state.option_other;
  }

  render_options() {
    let options = [];
    for (let choice of this.state.choices) {
      if (choice[0] == this.state.option) {
        options.push(
          <option value={choice[0]} selected>{choice[1]}</option>
        );
      } else {
        options.push(
          <option value={choice[0]}>{choice[1]}</option>
        );
      }
    }
    return options;
  }

  render() {
    return (
      <div className={this.props.root_class}>
        <div className="form-inline">
        <select
          id={this.state.id}
          name={this.state.name}
          className="form-control mb-2 mr-sm-2"
          onChange={this.on_option_change}>
          {this.render_options()}
        </select>
        {this.show_other_field() &&
        <input type="text"
          id={this.state.id}
          name={this.state.name}
          className="form-control mb-2"
          value={this.state.other}
          onChange={this.on_other_change} />}
        </div>
      </div>
    );
  }
}

export default SelectOtherWidgetController;
