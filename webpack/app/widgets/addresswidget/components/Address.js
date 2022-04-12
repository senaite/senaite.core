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
      address: props.address,
      address_type: props.address_type,
    }

    // Event handlers
    this.on_country_change = this.on_country_change.bind(this);
    this.on_subdivision1_change = this.on_subdivision1_change.bind(this);
    this.on_subdivision2_change = this.on_subdivision2_change.bind(this);
    this.on_city_change = this.on_city_change.bind(this);
    this.on_zip_change = this.on_zip_change.bind(this);
    this.on_address_change = this.on_address_change.bind(this);
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
    let value = event.currentTarget.value;
    console.debug(`Address::on_subdivision2_change: ${value}`);
    if (this.props.on_subdivision2_change) {
      this.props.on_subdivision2_change(value);
    }
    this.setState({subdivision2: value});
  }

  /** Event triggered when the value for the address field changes
   */
  on_address_change(event) {
    let value = event.currentTarget.value;
    this.setState({address: value});
  }

  /** Event triggered when the value for the zip field changes
   */
  on_zip_change(event) {
    let value = event.currentTarget.value;
    this.setState({zip: value});
  }

  /** Event triggered when the value for the city field changes
   */
  on_city_change(event) {
    let value = event.currentTarget.value;
    this.setState({city: value});
  }

  get_input_id(subfield) {
    let id = this.props.id;
    let index = this.props.index;
    return `${id}-${index}-${subfield}`
  }

  get_input_name(subfield) {
    let name = this.props.name;
    let index = this.props.index;
    return `${name}.${index}.${subfield}`
  }

  render() {
    return (
      <div>
        <div class="form-row mb-2">

          <div class="col input-group input-group-sm flex-nowrap d-inline-flex w-auto">
            <div class="input-group-prepend">
              <label class="input-group-text"
                for={this.get_input_id("country")}>
                {this.props.labels.country}
              </label>
            </div>
            <LocationSelector
              id={this.get_input_id("country")}
              name={this.get_input_name("country")}
              uid={this.props.uid}
              value={this.state.country}
              placeholder="Select country ..."
              locations={this.get_countries()}
              onChange={this.on_country_change} />
          </div>

          <div class="col input-group input-group-sm flex-nowrap d-inline-flex w-auto">
            <div class="input-group-prepend">
              <label class="input-group-text"
                for={this.get_input_id("subdivision1")}>
                {this.props.labels.subdivision1}
              </label>
            </div>
            <LocationSelector
              id={this.get_input_id("subdivision1")}
              name={this.get_input_name("subdivision1")}
              uid={this.props.uid}
              value={this.state.subdivision1}
              locations={this.get_subdivisions1()}
              onChange={this.on_subdivision1_change} />
          </div>

          <div class="col input-group input-group-sm flex-nowrap d-inline-flex w-auto">
            <div class="input-group-prepend">
              <label class="input-group-text"
                for={this.get_input_id("subdivision2")}>
                {this.props.labels.subdivision2}
              </label>
            </div>
            <LocationSelector
              id={this.get_input_id("subdivision2")}
              name={this.get_input_name("subdivision2")}
              uid={this.props.uid}
              value={this.state.subdivision2}
              locations={this.get_subdivisions2()}
              onChange={this.on_subdivision2_change} />
          </div>
        </div>

        <div class="form-row mb-2">
          <div class="col input-group input-group-sm flex-nowrap d-inline-flex w-auto">
            <div class="input-group-prepend">
              <label class="input-group-text"
                for={this.get_input_id("city")}>
                {this.props.labels.city}
              </label>
            </div>
            <input type="text"
              id={this.get_input_id("city")}
              name={this.get_input_name("city")}
              uid={this.props.uid}
              value={this.state.city}
              onChange={this.on_city_change} />
          </div>

          <div class="col input-group input-group-sm flex-nowrap d-inline-flex w-auto">
            <div class="input-group-prepend">
              <label class="input-group-text"
                for={this.get_input_id("zip")}>
                {this.props.labels.zip}
              </label>
            </div>
            <input type="text"
              id={this.get_input_id("zip")}
              name={this.get_input_name("zip")}
              uid={this.props.uid}
              value={this.state.zip}
              onChange={this.on_zip_change} />
          </div>

          <div class="col input-group input-group-sm flex-nowrap d-inline-flex w-auto">
            <div class="input-group-prepend">
              <label class="input-group-text"
                for={this.get_input_id("address")}>
                {this.props.labels.address}
              </label>
            </div>
            <input type="text"
              id={this.get_input_id("address")}
              name={this.get_input_name("address")}
              uid={this.props.uid}
              value={this.state.address}
              onChange={this.on_address_change} />
          </div>

          <input type="hidden"
            id={this.get_input_id("type")}
            name={this.get_input_name("type")}
            value={this.state.address_type} />

        </div>
      </div>
    );
  }

}

export default Address;