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

  is_textarea() {
    return this.props.type === "textarea";
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
    }

    if (this.is_textarea()) {
      return (
        <textarea
          id={this.props.id}
          cols={this.props.cols}
          rows={this.props.rows}
          name={this.props.name}
          value={this.props.value}
          className={this.props.className}
          style={{ resize: "both" }}
          onChange={this.props.onChange}></textarea>
      )
    }

    return (
      <input type="text"
        id={this.props.id}
        name={this.props.name}
        value={this.props.value}
        className={this.props.className}
        onChange={this.props.onChange} />
    )
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
      <div className="form-group row">
        <div className="col-sm-4">
          {this.props.label}
        </div>
        <div className="col-sm-8">
          {this.render_element()}
        </div>
      </div>
    );
  }
}

export default AddressField;
