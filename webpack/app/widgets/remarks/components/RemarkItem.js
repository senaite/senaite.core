import React from "react";

import Avatar from "../../components/Avatar.js";
import RemarkEditor from "./RemarkEditor.js";
import VersionHistory from "./VersionHistory.js";


/**
 * A single remark entry rendered as a comment.
 *
 * Renders one of three states: the inline editor (`editing`), a deleted
 * placeholder (`record.is_deleted`) or the normal remark with its
 * edit / history / delete affordances. Deletion is confirmed inline (no
 * browser alert).
 */
class RemarkItem extends React.Component {

  constructor(props) {
    super(props);
    this.state = {
      show_history: false,
      confirming_delete: false,
    };
    this.toggle_history = this.toggle_history.bind(this);
    this.on_edit = this.on_edit.bind(this);
    this.on_start_edit = this.on_start_edit.bind(this);
    this.open_delete = this.open_delete.bind(this);
    this.cancel_delete = this.cancel_delete.bind(this);
    this.confirm_delete = this.confirm_delete.bind(this);
  }

  /**
   * Return a translated label, falling back to the given default
   */
  translate(key, fallback) {
    let i18n = this.props.i18n || {};
    return i18n[key] || fallback;
  }

  on_edit(value) {
    this.props.on_edit(this.props.record.id, value);
  }

  on_start_edit() {
    this.props.on_start_edit(this.props.record.id);
  }

  toggle_history() {
    this.setState((state) => ({show_history: !state.show_history}));
  }

  open_delete() {
    this.setState({confirming_delete: true});
  }

  cancel_delete() {
    this.setState({confirming_delete: false});
  }

  confirm_delete() {
    this.setState({confirming_delete: false});
    this.props.on_delete(this.props.record.id);
  }

  /**
   * Build the "-- deleted by <user> at <time> --" placeholder
   */
  deleted_note() {
    let record = this.props.record;
    let template = this.translate(
      "deleted_note", "deleted by {user} at {time}");
    return template
      .replace("{user}", record.deleted_by)
      .replace("{time}", record.deleted);
  }

  /**
   * Meta line with author and timestamp, plus an optional trailing element
   */
  render_meta(extra) {
    let record = this.props.record;
    let author = record.user_name || record.user_id;
    return (
      <div className="remark-meta">
        <span className="remark-author">{author}</span>
        <span className="remark-time">{record.created}</span>
        {extra}
      </div>
    );
  }

  render_actions() {
    let record = this.props.record;
    let has_versions = (record.versions || []).length > 0;

    if (this.state.confirming_delete) {
      return (
        <div className="remark-actions remark-confirm">
          <span className="remark-confirm-text">
            {this.translate("confirm_delete", "Delete this remark?")}
          </span>
          <button
            type="button"
            className="remark-action remark-confirm-yes"
            disabled={this.props.submitting}
            onClick={this.confirm_delete}>
            {this.translate("delete", "Delete")}
          </button>
          <button
            type="button"
            className="remark-action remark-confirm-no"
            onClick={this.cancel_delete}>
            {this.translate("cancel", "Cancel")}
          </button>
        </div>
      );
    }

    return (
      <div className="remark-actions">
        {record.can_edit &&
          <button
            type="button"
            className="remark-action"
            onClick={this.on_start_edit}>
            {this.translate("edit", "Edit")}
          </button>}
        {has_versions &&
          <button
            type="button"
            className="remark-action"
            onClick={this.toggle_history}>
            {this.state.show_history
              ? this.translate("hide_history", "Hide history")
              : this.translate("show_history", "Show history")}
          </button>}
        {record.can_delete &&
          <button
            type="button"
            className="remark-action remark-action-delete"
            onClick={this.open_delete}>
            {this.translate("delete", "Delete")}
          </button>}
      </div>
    );
  }

  render_editing() {
    let record = this.props.record;
    let author = record.user_name || record.user_id;
    return (
      <div className="remark remark-editing">
        <Avatar seed={record.user_id} name={author}/>
        <div className="remark-body">
          <RemarkEditor
            mode="edit"
            value={record.content_text}
            submitting={this.props.submitting}
            label_save={this.translate("save", "Save")}
            label_cancel={this.translate("cancel", "Cancel")}
            on_save={this.on_edit}
            on_cancel={this.props.on_cancel_edit}/>
        </div>
      </div>
    );
  }

  render_deleted() {
    let record = this.props.record;
    let author = record.user_name || record.user_id;
    return (
      <div className="remark remark-deleted">
        <Avatar seed={record.user_id} name={author}/>
        <div className="remark-body">
          {this.render_meta()}
          <div className="remark-deleted-note">-- {this.deleted_note()} --</div>
        </div>
      </div>
    );
  }

  render_remark() {
    let record = this.props.record;
    let author = record.user_name || record.user_id;
    let edited_badge = record.edited && (
      <span className="remark-edited-badge">
        {this.translate("edited", "edited")} · {record.modified}
      </span>
    );
    return (
      <div className="remark">
        <Avatar seed={record.user_id} name={author}/>
        <div className="remark-body">
          {this.render_meta(edited_badge)}
          <div
            className="remark-content"
            dangerouslySetInnerHTML={{__html: record.content_html}}>
          </div>
          {this.render_actions()}
          {this.state.show_history &&
            <VersionHistory versions={record.versions} i18n={this.props.i18n}/>}
        </div>
      </div>
    );
  }

  render() {
    if (this.props.record.is_deleted) {
      return this.render_deleted();
    }
    if (this.props.editing) {
      return this.render_editing();
    }
    return this.render_remark();
  }
}

export default RemarkItem;
