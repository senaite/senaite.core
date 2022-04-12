import React from "react";
import ReactDOM from "react-dom";
import LocationSelector from "./LocationSelector.js";


class AddressField extends React.Component {

  constructor(props) {
    super(props);
  }

  is_location_selector() {
    return Array.isArray(this.props.locations);
  }

  render_element() {
    if (this.is_location_selector()) {
      return (
        <LocationSelector
          id={this.props.id}
          name={this.props.name}
          value={this.props.value}
          locations={this.props.locations}
          onChange={this.props.onChange} />
      )
    } else {
      return (
        <input type="text"
          id={this.props.id}
          name={this.props.name}
          value={this.props.value}
          onChange={this.props.onChange} />
      )
    }
  }

  render() {
    return (
      <div class="col input-group input-group-sm flex-nowrap d-inline-flex w-auto">
        <div class="input-group-prepend">
          <label class="input-group-text"
            for={this.props.id}>
            {this.props.label}
          </label>
        </div>
        {this.render_element()}
      </div>
    );
  }
}

export default AddressField;
