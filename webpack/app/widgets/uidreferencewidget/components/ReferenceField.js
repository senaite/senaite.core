import React from "react";
import ReactDOM from "react-dom";


class ReferenceField extends React.Component {

  constructor(props) {
    super(props);

    // React reference to the input field
    // https://reactjs.org/docs/react-api.html#reactcreateref
    this.input_field_ref = React.createRef();

    // bind event handlers
    this.on_focus = this.on_focus.bind(this);
    this.on_blur = this.on_blur.bind(this);
    this.on_change = this.on_change.bind(this);
    this.on_keypress = this.on_keypress.bind(this);
  }

  /*
   * Returns the search value from the input field
   */
  get_search_value() {
    return this.input_field_ref.current.value
  }

  /*
   * Handler when the search field get focused
   */
  on_focus(event) {
    console.debug("ReferenceField::on_focus");
    if (this.props.on_focus) {
      let value = this.get_search_value();
      this.props.on_focus(value);
    }
  }

  /*
   * Handler when the search field lost focus
   */
  on_blur(event) {
    console.debug("ReferenceField::on_blur");
    if (this.props.on_blur) {
      this.props.on_blur();
    }
  }

  /*
   * Handler when the search value changed
   */
  on_change(event) {
    event.preventDefault();
    let value = this.get_search_value();
    console.debug("ReferenceField::on_change:value: ", value);
    if (this.props.on_search) {
      this.props.on_search(value);
    }
  }

  /*
   * Handler for keypress events in the searh field
   *
   */
  on_keypress(event) {
    // prevent form submission when clicking ENTER
    if (event.which == 13) {
      console.debug("ReferenceField::on_keypress: Catch ENTER key");
      event.preventDefault();
    }
  }

  render() {
    return (
      <div className="uidreferencewidget-search-field">
        <div className="input-group">
          <input type="text"
                 name={this.props.name}
                 className={this.props.className}
                 ref={this.input_field_ref}
                 disabled={this.props.disabled}
                 onKeyPress={this.on_keypress}
                 onChange={this.on_change}
                 onFocus={this.on_focus}
                 onBlur={this.on_blur}
                 placeholder={this.props.placeholder}
                 style={{maxWidth: "160px"}}
          />
          <div class="input-group-append">
            <span class="input-group-text">
              <i class="fas fa-search"></i>
            </span>
          </div>
        </div>
      </div>
    );
  }
}

export default ReferenceField;
