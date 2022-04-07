import React from "react";
import ReactDOM from "react-dom";

import LocationSelector from "./LocationSelector.js";


class Address extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      country: props.country,
      country_state: props.country_state,
      district: props.district,
      city: props.city,
      zip: props.zip,
      address: props.address
    }

    // Event handlers
    this.on_country_change = this.on_country_change.bind(this);
    this.on_country_state_change = this.on_country_state_change.bind(this);
    this.on_district_change = this.on_district_change.bind(this);
  }

  /**
   * Returns the list of countries, sorted alphabetically
   */
  get_countries() {
    let countries = this.props.geography;
    return Object.keys(countries).sort();
  }

  /**
   * Returns the list of states for the current country, sorted alphabetically
   */
  get_states() {
    let country = this.state.country;
    let states = this.props.geography[country];
    if (states != null && states.constructor == Object) {
      return Object.keys(states).sort();
    }
    return [];
  }

  /**
   * Returns the list of districts for the current country and state, sorted
   * alphabetically
   */
  get_districts() {
    let country = this.state.country;
    let country_state = this.state.country_state;
    let states = this.props.geography[country];
    if (states != null && states.constructor == Object && country_state in states) {
      let districts = states[country_state];
      if (Array.isArray(districts)) {
        return districts.sort();
      }
    }
    return [];
  }

  on_country_change(event) {
    event.preventDefault();
    let value = event.currentTarget.value;
    console.debug("Address::on_country_change:value: ", value);
    if (this.props.on_country_change) {
      this.props.on_country_change(value);
    }
    this.setState({
      country: value,
      country_state: "",
    });
  }

  on_country_state_change(event) {
    event.preventDefault();
    let value = event.currentTarget.value;
    console.debug("Address::on_country_state_change:value: ", value);
    if (this.props.on_country_state_change) {
      let country = this.state.country
      this.props.on_country_state_change(country, value);
    }
    this.setState({country_state: value});
  }

  on_district_change(event) {
    event.preventDefault();
    let value = event.currentTarget.value;
    console.debug("Address::on_district_change:value: ", value);
    if (this.props.on_district_change) {
      this.props.on_district_change(value);
    }
    this.setState({district: value});
  }

  render() {
    return (
      <div className="addresswidget-address">
        <strong>{this.props.type}</strong>
        <div className="input-group">

          <input type="text"
            class="text-widget textline-field"
            id={this.props.id + ":address:records"}
            name={this.props.name + ":address:records"}
            value={this.props.address}/>

          <input type="text"
            class="text-widget textline-field"
            id={this.props.id + ":zip:records"}
            name={this.props.name + ":zip:records"}
            value={this.props.zip}/>

          <input type="text"
            class="text-widget textline-field"
            id={this.props.id + ":city:records"}
            name={this.props.name + ":city:records"}
            value={this.props.city}/>

          <LocationSelector
            id={this.props.id + ":country:records"}
            name={this.props.name + ":country:records"}
            uid={this.props.uid}
            value={this.state.country}
            locations={this.get_countries()}
            onChange={this.on_country_change}
          />

          <LocationSelector
            id={this.props.id + ":state:records"}
            name={this.props.name + ":state:records"}
            uid={this.props.uid}
            value={this.state.country_state}
            locations={this.get_states()}
            onChange={this.on_country_state_change}
          />

          <LocationSelector
            id={this.props.id + ":district:records"}
            name={this.props.name + ":district:records"}
            uid={this.props.uid}
            value={this.state.district}
            locations={this.get_districts()}
            onChange={this.on_district_change}
          />
        </div>
      </div>
    );
  }

}

export default Address;