import React from "react";

import Avatar from "./Avatar.js";
import RemarkEditor from "./RemarkEditor.js";
import VersionHistory from "./VersionHistory.js";


/**
 * A single remark entry rendered as a comment: avatar, author, timestamp,
 * content and the edit/history affordances. Renders the inline editor when
 * `editing`.
 */
class RemarkItem extends React.Component {

  constructor(props) {
    super(props);
    this.state = {show_history: false};
    this.toggle_history = this.toggle_history.bind(this);
    this.on_edit = this.on_edit.bind(this);
    this.on_start_edit = this.on_start_edit.bind(this);
  }

  toggle_history() {
    this.setState((state) => ({show_history: !state.show_history}));
  }

  on_edit(value) {
    this.props.on_edit(this.props.record.id, value);
  }

  on_start_edit() {
    this.props.on_start_edit(this.props.record.id);
  }

  render() {
    let record = this.props.record;
    let i18n = this.props.i18n || {};
    let author = record.user_name || record.user_id;
    let has_versions = (record.versions || []).length > 0;

    if (this.props.editing) {
      return (
        <div className="remark remark-editing">
          <Avatar seed={record.user_id} name={author}/>
          <div className="remark-body">
            <RemarkEditor
              mode="edit"
              value={record.content_text}
              submitting={this.props.submitting}
              label_save={i18n.save || "Save"}
              label_cancel={i18n.cancel || "Cancel"}
              on_save={this.on_edit}
              on_cancel={this.props.on_cancel_edit}/>
          </div>
        </div>
      );
    }

    return (
      <div className="remark">
        <Avatar seed={record.user_id} name={author}/>
        <div className="remark-body">
          <div className="remark-meta">
            <span className="remark-author">{author}</span>
            <span className="remark-time">{record.created}</span>
            {record.edited &&
              <span className="remark-edited-badge">
                {i18n.edited || "edited"} · {record.modified}
              </span>}
          </div>
          <div
            className="remark-content"
            dangerouslySetInnerHTML={{__html: record.content_html}}>
          </div>
          <div className="remark-actions">
            {record.can_edit &&
              <button
                type="button"
                className="remark-action"
                onClick={this.on_start_edit}>
                {i18n.edit || "Edit"}
              </button>}
            {has_versions &&
              <button
                type="button"
                className="remark-action"
                onClick={this.toggle_history}>
                {this.state.show_history
                  ? (i18n.hide_history || "Hide history")
                  : (i18n.show_history || "Show history")}
              </button>}
          </div>
          {this.state.show_history &&
            <VersionHistory versions={record.versions} i18n={i18n}/>}
        </div>
      </div>
    );
  }
}

export default RemarkItem;
