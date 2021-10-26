import React from "react";
import ReactDOM from "react-dom";


class References extends React.Component {

  constructor(props) {
    super(props);

    this.on_deselect = this.on_deselect.bind(this);
  }

  get_selected_uids() {
    return this.props.uids || [];
  }

  get_item_by_uid() {
    return this.props.items || {};
  }

  get_display_link(uid) {
    let item = this.props.items[uid];
    let display_field = this.props.display_field;
    let display_value = item[display_field] || uid;
    return <a href={item.url} target="_blank">{display_value}</a>
  }

  build_selected_items() {
    let items = [];
    let selected_uids = this.get_selected_uids();

    for (let uid of selected_uids) {
      items.push(
        <div uid={uid} className="reference">
          <div className="p-1 mb-1 bg-light border rounded d-inline-block">
            {this.get_display_link(uid)}
            <i uid={uid}
               onClick={this.on_deselect}
               style={{cursor: "pointer"}}
               className="fas fa-times-circle pl-2"></i>
          </div>

        </div>
      );
    }
    return items
  }

  on_deselect(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let uid = target.getAttribute("uid");
    console.debug("References::on_deselect: Remove UID", uid);
    if (this.props.on_deselect) {
      this.props.on_deselect(uid);
    }
  }

  render() {
    return (
      <div className="uidreferencewidget-references">
        <div className="selected-items">
          {this.build_selected_items()}
        </div>
        {/* submitted in form */}
        <textarea
          className="d-none"
          name={this.props.name}
          value={this.props.uids.join("\n")}
        />
      </div>
    );
  }
}

export default References;
