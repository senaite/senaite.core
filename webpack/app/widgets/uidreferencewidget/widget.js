import React from "react"
import ReactDOM from "react-dom"

import References from "./components/References.js"
import ReferenceField from "./components/ReferenceField.js"


class UIDReferenceWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Internal state
    this.state = {
      "results": []
    }

    // root input HTML element
    let el = props.root_el;

    // data keys located at the root element
    const data_keys = [
      "id",
      "name",
      "uids",
      "items",
      "catalog",
      "query",
      "columns",
      "display_field",
      "limit",
      "multi_valued",
      "disabled",
      "readonly",
    ]

    // query data keys and set state with parsed JSON value
    for (let key of data_keys) {
      let value = el.dataset[key];
      this.state[key] = this.parse_json(value);
    }

    this.deselect = this.deselect.bind(this);
    this.on_esc = this.on_esc.bind(this);

    // dev only
    window.widget = this;

    return this
  }

  componentDidMount() {
    document.addEventListener("keydown", this.on_esc, false);
  }

  componentWillUnmount() {
    document.removeEventListener("keydown", this.on_esc, false);
  }

  /*
   * JSON parse the given value
   */
  parse_json(value) {
    try {
      return JSON.parse(value)
    } catch (error) {
      console.warn(`Could not parse "${value}" to JSON`);
    }
  }

  deselect(uid) {
    console.debug("ReferenceWidgetController::deselect:uid:", uid);
    let uids = [].concat(this.state.uids);
    let pos = uids.indexOf(uid);
    if (pos > -1) {
      uids.splice(pos, 1);
    }
    this.setState({uids: uids});
    this.clear_results();
  }

  clear_results() {
    this.setState({results: []})
  }

  on_esc(event){
    if(event.keyCode === 27) {
    }
  }


  render() {
    return (
        <div className="uidreferencewidget">
          <References
            uids={this.state.uids}
            items={this.state.items}
            display_field={this.state.display_field}
            name={this.state.name}
            on_deselect={this.deselect}
          />
          <ReferenceField
            className="form-control"
            name="uidreference-search"
          />
        </div>
    );
  }
}

export default UIDReferenceWidgetController;
