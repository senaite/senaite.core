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
      "name",
      "items",
      "portal_url",
      "labels",
      "countries",
      "subdivisions1",
      "subdivisions2",
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
    this.on_country_change = this.on_country_change.bind(this);
    this.on_subdivision1_change = this.on_subdivision1_change.bind(this);

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
   * Event triggered when the user selects a country. Function fetches and
   * updates the geo mapping with the first level subdivisions for the selected
   * country if are not up-to-date yet. It also updates the label for the first
   * level subdivision in accordance.
   */
  on_country_change(country) {
    console.debug(`widget::on_country_change: ${country}`);
    let self = this;
    let promise = this.api.fetch_subdivisions(country);
    promise.then(function(data){

      // Update the label with the type of 1st-level subdivisions
      let labels = {...self.state.labels};
      if (data.length > 0) {
        labels[country]["subdivision1"] = data[0].type;
      }

      // Create a copy instead of modifying the existing dict from state var
      let subdivisions = {...self.state.subdivisions1};

      // Only interested in names, sorted alphabetically
      subdivisions[country] = data.map((x) => x.name).sort();

      // Update current state with the changes
      self.setState({
        subdivisions1: subdivisions,
        labels: labels,
      });
    });
    return promise;
  }

  /**
   * Event triggered when the user selects a first-level subdivision of a
   * country. Function fetches and updates the geo mapping with the second level
   * subdivisions for the selected subdivision if are not up-to-date. It also
   * updates the label for the second level subdivision in accordance.
   */
  on_subdivision1_change(country, subdivision) {
    console.debug(`widget::on_subdivision1_change: ${country}, ${subdivision}`);
    let self = this;
    let promise = this.api.fetch_subdivisions(subdivision);
    promise.then(function(data){

      // Update the label with the type of 1st-level subdivisions
      let labels = {...self.state.labels};
      if (data.length > 0) {
        labels[country]["subdivision2"] = data[0].type;
      }

      // Create a copy instead of modifying the existing dict from state var
      let subdivisions = {...self.state.subdivisions2};

      // Only interested in names, sorted alphabetically
      subdivisions[subdivision] = data.map((x) => x.name).sort();

      // Update current state with the changes
      self.setState({
        subdivisions2: subdivisions,
        labels: labels,
      });
    });
    return promise;
  }

  render_items() {
    let html_items = [];
    let items = this.state.items;
    for (const [index, item] of items.entries()) {
      let section_title = "";
      if (items.length > 1) {
        // Only render the title if more than one address
        section_title = (
          <strong>{this.state.labels[item.type]}</strong>
        )
      }

      html_items.push(
        <div class="mb-2 pt-2">
          {section_title}
          <Address
            id={this.state.id}
            name={this.state.name}
            index={index}
            address_type={item.type}
            country={item.country}
            subdivision1={item.subdivision1}
            subdivision2={item.subdivision2}
            city={item.city}
            zip={item.zip}
            address={item.address}
            labels={this.state.labels}
            countries={this.state.countries}
            subdivisions1={this.state.subdivisions1}
            subdivisions2={this.state.subdivisions2}
            on_country_change={this.on_country_change}
            on_subdivision1_change={this.on_subdivision1_change}
          />
        </div>
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
