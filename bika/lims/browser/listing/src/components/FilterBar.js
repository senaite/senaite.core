import React from "react";

import Button from "./Button.js";


class FilterBar extends React.Component {
  /** Filter Bar
   */

  constructor(props) {
    super(props);
    this.state = {
      active: "default",
    };
  }

  handleClick = (event) => {
    let button = event.target;
    let button_id = button.id;
    console.info("Button " + button_id + " clicked...");
    this.setState({active: button_id});
    this.props.onClick(event);
  }

  buildButtons() {
    let buttons = [];
    for (let [key, value] of Object.entries(this.props.review_states)) {
      let cls = "btn btn-default btn-sm";
      if (value.id == this.state.active) {
        cls += " active";
      }
      buttons.push(
        <li key={value.id}>
          <Button onClick={this.handleClick}
                  id={value.id}
                  title={value.title}
                  className={cls}/>
        </li>
      );
    }
    return buttons;
  }

  render() {
    return (
      <ul className={this.props.className}>
        {this.buildButtons()}
      </ul>
    );
  }
}

export default FilterBar;
