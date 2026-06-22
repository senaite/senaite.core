import React from "react";

import RemarkItem from "./RemarkItem.js";

// number of remarks shown before the "show more" toggle kicks in
const COLLAPSE_AFTER = 3;


/**
 * List of remarks, newest first. Collapses the list beyond COLLAPSE_AFTER
 * entries behind a show more/less toggle.
 */
class RemarksList extends React.Component {

  constructor(props) {
    super(props);
    this.state = {expanded: false};
    this.toggle = this.toggle.bind(this);
  }

  toggle() {
    this.setState((state) => ({expanded: !state.expanded}));
  }

  render() {
    let remarks = this.props.remarks || [];
    let i18n = this.props.i18n || {};

    if (remarks.length === 0) {
      return (
        <div className="remarks-empty text-muted small">
          {i18n.no_remarks || ""}
        </div>
      );
    }

    let collapsed = !this.state.expanded && remarks.length > COLLAPSE_AFTER;
    let visible = collapsed ? remarks.slice(0, COLLAPSE_AFTER) : remarks;

    return (
      <div className="remarks-history">
        {visible.map((record) => (
          <RemarkItem
            key={record.id}
            record={record}
            editing={this.props.editing_id === record.id}
            submitting={this.props.submitting}
            i18n={i18n}
            on_start_edit={this.props.on_start_edit}
            on_cancel_edit={this.props.on_cancel_edit}
            on_edit={this.props.on_edit}/>
        ))}
        {remarks.length > COLLAPSE_AFTER &&
          <button
            type="button"
            className="remarks-toggle btn btn-link btn-sm p-0"
            onClick={this.toggle}>
            {this.state.expanded
              ? (i18n.show_less || "Show less")
              : (i18n.show_more || "Show more")}
          </button>}
      </div>
    );
  }
}

export default RemarksList;
