import React from "react";
import "./SearchField.css"


/** Input field that triggers a search query
 *
 */
class SearchField extends React.Component {

  constructor(props) {
    super(props);

    this.state = {}

    // React reference to the input field
    // https://reactjs.org/docs/react-api.html#reactcreateref
    this.input_field_ref = React.createRef();

    // bind event handlers
    this.on_focus = this.on_focus.bind(this);
    this.on_blur = this.on_blur.bind(this);
    this.on_change = this.on_change.bind(this);
    this.on_keydown = this.on_keydown.bind(this);
    this.on_keypress = this.on_keypress.bind(this);
    this.on_clear_click = this.on_clear_click.bind(this);
    this.on_search_click = this.on_search_click.bind(this);
  }

  /*
   * Returns the search value from the input field
   */
  get_search_value() {
    return this.input_field_ref.current.value;
  }

  /*
   * Handler when the search field get focused
   */
  on_focus(event) {
    console.debug("SearchField::on_focus");
    if (this.props.on_focus) {
      let value = this.get_search_value() || null;
      this.props.on_focus(value);
    }
  }

  /*
   * Handler when the search field lost focus
   */
  on_blur(event) {
    console.debug("SearchField::on_blur");
    let value = this.get_search_value();
    if (event.relatedTarget !== null || !value) {
      // do not fire blur event if the user clicked e.g. in the results table
      return;
    }
    if (this.props.on_blur) {
      this.props.on_blur(value);
      // clear the input field
      this.input_field_ref.current.value = ""
    }
  }

  /*
   * Handler when the search value changed
   */
  on_change(event) {
    event.preventDefault();
    let value = this.get_search_value();
    console.debug("SearchField::on_change:value: ", value);
    if (this.props.on_search) {
      this.props.on_search(value);
    }
  }

  /*
   * Handler for keydown events in the search field
   *
   */
  on_keydown(event) {
    // backspace
    if (event.which == 8) {
      if (this.get_search_value() == "") {
        this.props.on_clear();
      }
    }

    // down arrow
    if (event.which == 40) {
      if (this.props.on_arrow_key) {
        this.props.on_arrow_key("down");
      }
    }
    // up arrow
    if (event.which == 38) {
      if (this.props.on_arrow_key) {
        this.props.on_arrow_key("up");
      }
    }

    // left arrow
    if (event.which == 37) {
      if (this.props.on_arrow_key) {
        this.props.on_arrow_key("left");
      }
    }

    // right arrow
    if (event.which == 39) {
      if (this.props.on_arrow_key) {
        this.props.on_arrow_key("right");
      }
    }
  }

  /*
   * Handler for keypress events in the search field
   *
   */
  on_keypress(event) {
    if (event.which == 13) {
      console.debug("SearchField::on_keypress:ENTER");
      // prevent form submission when clicking ENTER
      event.preventDefault();
      if (this.props.on_enter) {
        let value = this.get_search_value();
        this.props.on_enter(value);
        // clear the input field
        this.input_field_ref.current.value = ""
      }

    }
  }

  on_clear_click(event) {
    event.preventDefault();
    if (this.props.on_clear) {
      let value = this.get_search_value();
      this.props.on_clear(value);
      // clear the input field
      this.input_field_ref.current.value = ""
    }
  }

  on_search_click(event) {
    event.preventDefault();
    if (this.props.on_search) {
      let value = this.get_search_value();
      this.props.on_search(value);
    }
  }

  render() {
    return (
      <div className={this.props.className}>
        <div className="input-group searchfield">
          <input type="text"
                 autoComplete="off"
                 name={this.props.name}
                 className={this.props.className}
                 ref={this.input_field_ref}
                 disabled={this.props.disabled}
                 onKeyDown={this.on_keydown}
                 onKeyPress={this.on_keypress}
                 onChange={this.on_change}
                 onFocus={this.on_focus}
                 onBlur={this.on_blur}
                 placeholder={this.props.placeholder}
          />
          <div className="input-group-append">
            <button className="btn btn-sm btn-outline-secondary"
                    style={{zIndex: 0}}
                    disabled={this.props.disabled}
                    onClick={this.on_clear_click}>
              <i className="fas fa-times"></i>
            </button>
            <button className="btn btn-sm btn-outline-primary"
                    style={{zIndex: 0}}
                    disabled={this.props.disabled}
                    onClick={this.on_search_click}>
              {!this.props.loading && <i className="fas fa-search"></i>}
              {this.props.loading && <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>}
            </button>
          </div>
        </div>
      </div>
    );
  }
}

export default SearchField;
