import React from "react"
import ReactDOM from "react-dom"

import AddressWidgetAPI from "./api.js"
import Address from "./components/Address.js"


class AddressWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Root input HTML element
    let el = props.root_el;

    this.state = {};

    // Data keys located at the root element
    // -> initial values are set from the widget class
    const data_keys = [
      "id",
      "uid",
      "name",
      "items",
      "geography",
      "portal_url",
    ];

    // Query data keys and set state with parsed JSON value
    for (let key of data_keys) {
      let value = el.dataset[key];
      this.state[key] = this.parse_json(value);
    }

    // Initialize communication API with the API URL
    this.api = new AddressWidgetAPI({
      portal_url: this.state.portal_url,
    });

    // Bind callbacks to current context
    this.update_states = this.update_states.bind(this);
    this.update_districts = this.update_districts.bind(this);

    return this;
  }

  parse_json(value) {
    try {
      return JSON.parse(value);
    } catch (error) {
      console.error(`Could not parse "${value}" to JSON`);
    }
  }

  /**
   * Fetch and update states for the given country
   */
  update_states(country) {
    let states = this.state.geography[country];
    if (states != null && states.constructor == Object) {
      // Nothing to do. States are up-to-date
      return;
    }
    let self = this;
    let promise = this.api.fetch_states(country);
    promise.then(function(data){
      // Store a dict with states names as keys and null as values
      let states = Object.assign({}, ...data.map((x) => ({[x[2]]: null})));

      // Create a copy instead of modifying the existing dict from state var
      let geo = {...self.state.geography};

      geo[country] = states;
      self.setState({geography: geo});
    });
    return promise;

  }

  /**
   * Fetch and update districts for the given country and state
   */
  update_districts(country, country_state) {
    console.debug(this.state);
    let districts = this.state.geography[country][country_state];
    if (Array.isArray(districts)) {
      // Nothing to do. Districts are up-to-date
      return;
    }

    let self = this;
    let promise = this.api.fetch_districts(country, country_state);
    promise.then(function(data){
      // Only interested on district names
      let districts = data.map((x) => x[2])

      // Create a copy instead of modifying the existing dict from state var
      let geo = {...self.state.geography};

      // Store the list of districts
      geo[country][country_state] = districts
      self.setState({geography: geo});
    });
    return promise;
  }

  render_items() {
    let html_items = [];
    let items = this.state.items;
    for (let item of items) {
      html_items.push(
        <Address
          id={this.state.id}
          uid={this.state.uid}
          name={this.state.name}
          type={item["type"]}
          country={item["country"]}
          country_state={item["state"]}
          district={item["district"]}
          city={item["city"]}
          zip={item["zip"]}
          address={item["address"]}
          geography={this.state.geography}
          on_country_change={this.update_states}
          on_country_state_change={this.update_districts}
        />
      );
    }
    return html_items;
  }

  render() {
    return (
        <div className="addresswidget">
          {this.render_items()}
        </div>
    );
  }
}

export default AddressWidgetController;
