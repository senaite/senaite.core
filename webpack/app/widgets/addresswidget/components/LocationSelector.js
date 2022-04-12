import React from "react";
import ReactDOM from "react-dom";


class LocationSelector extends React.Component {

  constructor(props) {
    super(props);
  }

  render_options() {
    let options = [];
    let locations = this.props.locations;
    options.push(
      <option value=''></option>
    );
    if (Array.isArray(locations)) {
      for (let location of locations) {
        options.push(
          <option value={location}>{location}</option>
        )
      }
    }
    return options;
  }

  render() {
    return (
      <select
        id={this.props.id}
        name={this.props.name}
        value={this.props.value}
        onChange={this.props.onChange}>
        {this.render_options()}
      </select>
    );
  }
}

export default LocationSelector;
