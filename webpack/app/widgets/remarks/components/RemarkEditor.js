import React from "react";


/**
 * Textarea editor used both for adding a new remark and for editing an
 * existing one. Owns the textarea value locally; the controller drives the
 * submit guard via the `submitting` prop.
 */
class RemarkEditor extends React.Component {

  constructor(props) {
    super(props);
    this.state = {value: props.value || ""};
    this.on_change = this.on_change.bind(this);
    this.on_save = this.on_save.bind(this);
    this.on_keydown = this.on_keydown.bind(this);
  }

  componentDidUpdate(prev_props) {
    // reset the textarea after a successful add (reset_token changed)
    if (this.props.reset_token !== prev_props.reset_token) {
      this.setState({value: ""});
    }
  }

  on_change(event) {
    this.setState({value: event.target.value});
  }

  on_save() {
    this.props.on_save(this.state.value, this.props.remark_id);
  }

  on_keydown(event) {
    // submit with Ctrl/Cmd + Enter
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      if (!this.props.submitting && this.state.value.trim()) {
        this.on_save();
      }
    }
  }

  render() {
    let submitting = this.props.submitting;
    let disabled = submitting || !this.state.value.trim();
    return (
      <div className="remarks-editor">
        <textarea
          className="form-control remarks-textarea"
          rows="2"
          placeholder={this.props.placeholder || ""}
          value={this.state.value}
          disabled={submitting}
          onChange={this.on_change}
          onKeyDown={this.on_keydown}/>
        <div className="remarks-editor-actions">
          <button
            type="button"
            className="btn btn-primary btn-sm"
            disabled={disabled}
            onClick={this.on_save}>
            {this.props.label_save}
          </button>
          {this.props.on_cancel &&
            <button
              type="button"
              className="btn btn-link btn-sm text-muted"
              disabled={submitting}
              onClick={this.props.on_cancel}>
              {this.props.label_cancel}
            </button>}
        </div>
      </div>
    );
  }
}

export default RemarkEditor;
