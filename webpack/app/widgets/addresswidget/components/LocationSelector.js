import React from "react";
import ReactDOM from "react-dom";


class LocationSelector extends React.Component {

  constructor(props) {
    super(props);
  }

  render_options() {
    let options = [];
    console.debug("Locations: ",this.props.locations);
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
        ref={this._ref}
        id={this.props.id}
        uid={this.props.uid}
        name={this.props.name}
        value={this.props.value}
        onChange={this.props.onChange}>
        {this.render_options()}
      </select>
    );
  }
}

export default LocationSelector;
