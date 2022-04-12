import React from "react";
import ReactDOM from "react-dom";

import LocationSelector from "./LocationSelector.js";


class Address extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      country: props.country,
      subdivision1: props.subdivision1,
      subdivision2: props.subdivision2,
      city: props.city,
      zip: props.zip,
      address: props.address
    }

    // Event handlers
    this.on_country_change = this.on_country_change.bind(this);
    this.on_subdivision1_change = this.on_subdivision1_change.bind(this);
    this.on_subdivision2_change = this.on_subdivision2_change.bind(this);
  }

  /**
   * Returns the list of countries, sorted alphabetically
   */
  get_countries() {
    let countries = this.props.geography;
    return Object.keys(countries).sort();
  }

  /**
   * Returns the list of first-level subdivisions of the current country,
   * sorted alphabetically
   */
  get_subdivisions1() {
    let country = this.state.country;
    let subdivisions = this.props.geography[country];
    if (subdivisions != null && subdivisions.constructor == Object) {
      return Object.keys(subdivisions).sort();
    }
    return [];
  }

  /**
   * Returns the list of subdivisions of the current first-level subdivision,
   * sorted sorted alphabetically
   */
  get_subdivisions2() {
    let country = this.state.country;
    let subdivision1 = this.state.subdivision1;
    let subdivisions = this.props.geography[country];
    if (subdivisions != null
        && subdivisions.constructor == Object
        && subdivision1 in subdivisions) {
      let subdivisions2 = subdivisions[subdivision1];
      if (Array.isArray(subdivisions2)) {
        return subdivisions2.sort();
      }
    }
    return [];
  }

  /** Event triggered when the value for Country selector changes. Updates the
   * selector of subdivisions (e.g. states) with the list of top-level
   * subdivisions for the selected country
   */
  on_country_change(event) {
    event.preventDefault();
    let value = event.currentTarget.value;
    console.debug(`Address::on_country_change: ${value}`);
    if (this.props.on_country_change) {
      this.props.on_country_change(value);
    }
    this.setState({
      country: value,
      subdivision1: "",
    });
  }

  /** Event triggered when the value for the Country first-level subdivision
   * (e.g. state) selector changes. Updates the selector of subdivisions (e.g.
   * districts) for the selected subdivision and country
   */
  on_subdivision1_change(event) {
    event.preventDefault();
    let value = event.currentTarget.value;
    console.debug(`Address::on_subdivision1_change: ${value}`);
    if (this.props.on_subdivision1_change) {
      let country = this.state.country
      this.props.on_subdivision1_change(country, value);
    }
    this.setState({subdivision1: value});
  }

  /** Event triggered when the value for the second-level subdivision (e.g.
   * district) selector changes
   */
  on_subdivision2_change(event) {
    event.preventDefault();
    let value = event.currentTarget.value;
    console.debug(`Address::on_subdivision2_change: ${value}`);
    if (this.props.on_subdivision2_change) {
      this.props.on_subdivision2_change(value);
    }
    this.setState({subdivision2: value});
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
            id={this.props.id + ":subdivision1:records"}
            name={this.props.name + ":subdivision1:records"}
            uid={this.props.uid}
            value={this.state.subdivision1}
            locations={this.get_subdivisions1()}
            onChange={this.on_subdivision1_change}
          />

          <LocationSelector
            id={this.props.id + ":subdivision2:records"}
            name={this.props.name + ":subdivision2:records"}
            uid={this.props.uid}
            value={this.state.subdivision2}
            locations={this.get_subdivisions2()}
            onChange={this.on_subdivision2change}
          />
        </div>
      </div>
    );
  }

}

export default Address;