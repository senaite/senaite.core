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
      <option key="novalue" value=''></option>
    );
    if (Array.isArray(locations)) {
      for (let location of locations) {
        options.push(
          <option key={location} value={location}>{location}</option>
        )
      }
    }
    return options;
  }

  render() {
    return (
      <select className="form-control"
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
