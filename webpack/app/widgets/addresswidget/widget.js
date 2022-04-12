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
    this.update_country_subdivisions = this.update_country_subdivisions.bind(this);
    this.update_subdivision_subdivisions = this.update_subdivision_subdivisions.bind(this);

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
   * Fetch and update subdivisions for the given country
   */
  update_country_subdivisions(country) {
    console.debug(`widget::update_country_subdivisions: ${country}`);
    let subdivisions = this.state.geography[country];
    if (subdivisions != null && subdivisions.constructor == Object) {
      // Nothing to do. First-level subdivisions are up-to-date
      return;
    }
    let self = this;
    let promise = this.api.fetch_states(country);
    promise.then(function(data){
      // Store a dict with subdivisions names as keys and null as values
      let subdivisions = Object.assign({}, ...data.map((x) => ({[x[2]]: null})));

      // Create a copy instead of modifying the existing dict from state var
      let geo = {...self.state.geography};

      geo[country] = subdivisions;
      self.setState({geography: geo});
    });
    return promise;

  }

  /**
   * Fetch and update districts for the given country and top-level subdivision
   */
  update_subdivision_subdivisions(country, subdivision) {
    console.debug(`widget::update_subdivision_subdivisions: ${country}, ${subdivision}`);
    let subdivisions = this.state.geography[country][subdivision];
    if (Array.isArray(subdivisions)) {
      // Nothing to do. Subdivisions are up-to-date
      return;
    }

    let self = this;
    let promise = this.api.fetch_districts(country, subdivision);
    promise.then(function(data){
      // Only interested on subdivisions names
      let subdivisions = data.map((x) => x[2])

      // Create a copy instead of modifying the existing dict from state var
      let geo = {...self.state.geography};

      // Store the list of subdivisions
      geo[country][subdivision] = subdivisions
      self.setState({geography: geo});
    });
    return promise;
  }

  render_items() {
    let html_items = [];
    let items = this.state.items;
    for (let item of items) {
      let subdiv1 = item["subdivision1"];
      let subdiv2 = item["subdivision2"];

      // XXX Support for old-address "state" + "district"
      //subdiv1 = subdiv1 ? subdiv1 : item["state"]
      //subdiv2 = subdiv2 ? subdiv2 : item["district"];

      html_items.push(
        <Address
          id={this.state.id}
          uid={this.state.uid}
          name={this.state.name}
          type={item["type"]}
          country={item["country"]}
          subdivision1={subdiv1}
          subdivision2={subdiv2}
          city={item["city"]}
          zip={item["zip"]}
          address={item["address"]}
          geography={this.state.geography}
          on_country_change={this.update_country_subdivisions}
          on_subdivision1_change={this.update_subdivision_subdivisions}
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
