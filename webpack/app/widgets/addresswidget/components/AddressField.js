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

  is_visible() {
    let visible = true;
    if (this.is_location_selector()) {
      visible = this.props.locations.length > 0;
    }
    return visible;
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
    if (!this.is_visible()) {
      return (
        <input type="hidden"
          id={this.props.id}
          name={this.props.name}
          value={this.props.value} />
      )
    }
    return (
      <div class="form-group form-row mb-2">
        <div class="col input-group input-group-sm">
          <div class="input-group-prepend">
            <label class="input-group-text"
              for={this.props.id}>
              {this.props.label}
            </label>
          </div>
          {this.render_element()}
        </div>
      </div>
    );
  }
}

export default AddressField;
