import React from "react";

import Avatar from "../../components/Avatar.js";
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
    this.on_delete = this.on_delete.bind(this);
  }

  on_delete() {
    this.props.on_delete(this.props.record.id);
  }

  /**
   * Build the placeholder note shown in place of a deleted remark
   */
  deleted_note() {
    let record = this.props.record;
    let i18n = this.props.i18n || {};
    let template = i18n.deleted_note || "deleted by {user} at {time}";
    return template
      .replace("{user}", record.deleted_by)
      .replace("{time}", record.deleted);
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

    let css_class = record.is_deleted ? "remark remark-deleted" : "remark";

    return (
      <div className={css_class}>
        <Avatar seed={record.user_id} name={author}/>
        <div className="remark-body">
          <div className="remark-meta">
            <span className="remark-author">{author}</span>
            <span className="remark-time">{record.created}</span>
            {record.edited && !record.is_deleted &&
              <span className="remark-edited-badge">
                {i18n.edited || "edited"} · {record.modified}
              </span>}
            {record.is_deleted &&
              <span className="remark-deleted-note">
                -- {this.deleted_note()} --
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
            {record.can_delete &&
              <button
                type="button"
                className="remark-action remark-action-delete"
                onClick={this.on_delete}>
                {i18n.delete || "Delete"}
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
