import React from "react";

import RemarksAPI from "./api.js";
import Avatar from "../components/Avatar.js";
import RemarksList from "./components/RemarksList.js";
import RemarkEditor from "./components/RemarkEditor.js";
import "./remarks.css";

// abort an in-flight request after this many milliseconds
const REQUEST_TIMEOUT = 30000;

// localStorage key + event for the (global) sort direction preference
const SORT_KEY = "senaite.core.remarks.sort";
const SORT_EVENT = "senaite.core.remarks:sort_changed";


class RemarksWidgetController extends React.Component {

  constructor(props) {
    super(props);

    // Root HTML element
    let el = props.root_el;

    // Data keys located at the root element (JSON encoded)
    const data_keys = [
      "id",
      "uid",
      "fieldname",
      "portal_url",
      "remarks",
      "can_add",
      "can_manage",
      "current_user_id",
      "i18n",
    ];

    this.data = {};
    for (let key of data_keys) {
      this.data[key] = this.parse_json(el.dataset[key]);
    }

    this.state = {
      remarks: this.data.remarks || [],
      // id of the remark being edited, or null
      editing_id: null,
      // in-flight guard: disables submit while a request is pending
      submitting: false,
      // increments after each successful add to reset the add editor
      add_token: 0,
      // sort direction, shared across all remarks widgets (localStorage)
      sort: this.read_sort(),
      error: null,
    };

    // controller of the current in-flight request
    this.controller = null;

    this.api = new RemarksAPI({portal_url: this.data.portal_url});

    this.handle_add = this.handle_add.bind(this);
    this.handle_edit = this.handle_edit.bind(this);
    this.handle_delete = this.handle_delete.bind(this);
    this.start_edit = this.start_edit.bind(this);
    this.cancel_edit = this.cancel_edit.bind(this);
    this.toggle_sort = this.toggle_sort.bind(this);
    this.on_sort_changed = this.on_sort_changed.bind(this);

    return this;
  }

  componentDidMount() {
    // keep all mounted remarks widgets in sync when the sort changes
    window.addEventListener(SORT_EVENT, this.on_sort_changed);
  }

  componentWillUnmount() {
    window.removeEventListener(SORT_EVENT, this.on_sort_changed);
  }

  parse_json(value) {
    try {
      return JSON.parse(value);
    } catch (error) {
      console.error(`Could not parse "${value}" to JSON`);
      return null;
    }
  }

  /**
   * Return a translated label by key
   */
  translate(key) {
    let i18n = this.data.i18n || {};
    return i18n[key] || key;
  }

  /**
   * Read the persisted (global) sort direction, defaulting to "desc"
   */
  read_sort() {
    try {
      return localStorage.getItem(SORT_KEY) === "asc" ? "asc" : "desc";
    } catch (error) {
      return "desc";
    }
  }

  /**
   * Toggle the sort direction and broadcast it to all remarks widgets
   */
  toggle_sort() {
    let sort = this.state.sort === "desc" ? "asc" : "desc";
    try {
      localStorage.setItem(SORT_KEY, sort);
    } catch (error) {
      // ignore storage errors (private mode etc.)
    }
    this.setState({sort: sort});
    window.dispatchEvent(new CustomEvent(SORT_EVENT, {detail: {sort: sort}}));
  }

  on_sort_changed(event) {
    let sort = event.detail && event.detail.sort;
    if (sort && sort !== this.state.sort) {
      this.setState({sort: sort});
    }
  }

  /**
   * Abort any in-flight request and start a fresh one. Returns the timeout
   * handle that bounds the new request.
   */
  begin_request() {
    if (this.controller) {
      // abort the prior request (race guard)
      this.controller.abort();
    }
    this.controller = new AbortController();
    let controller = this.controller;
    return setTimeout(() => controller.abort(), REQUEST_TIMEOUT);
  }

  end_request(timeout) {
    clearTimeout(timeout);
    this.controller = null;
  }

  on_error(error, timeout) {
    clearTimeout(timeout);
    this.controller = null;
    if (error && error.name === "AbortError") {
      // superseded or timed out: just release the guard
      this.setState({submitting: false});
      return;
    }
    console.error("RemarksWidget: request failed", error);
    this.setState({submitting: false, error: this.translate("error")});
  }

  /**
   * Replace the record with the given id by the server response
   */
  reconcile(remark_id, remark) {
    this.setState((state) => ({
      remarks: state.remarks.map(
        (record) => record.id === remark_id ? remark : record),
      submitting: false,
      editing_id: null,
    }));
  }

  handle_add(value) {
    // in-flight guard: ignore while a request is pending
    if (this.state.submitting) {
      return;
    }
    let text = (value || "").trim();
    if (!text) {
      return;
    }

    this.setState({submitting: true, error: null});
    let timeout = this.begin_request();
    let signal = this.controller.signal;

    this.api.add_remark(this.data.uid, this.data.fieldname, text, signal)
      .then((data) => {
        this.end_request(timeout);
        if (!data || !data.success || !data.remark) {
          this.setState({submitting: false, error: this.translate("error")});
          return;
        }
        // prepend the server record (single source of truth, no refetch)
        this.setState((state) => ({
          remarks: [data.remark, ...state.remarks],
          submitting: false,
          editing_id: null,
          add_token: state.add_token + 1,
        }));
      })
      .catch((error) => this.on_error(error, timeout));
  }

  handle_edit(remark_id, value) {
    if (this.state.submitting) {
      return;
    }
    let text = (value || "").trim();
    if (!text) {
      return;
    }

    this.setState({submitting: true, error: null});
    let timeout = this.begin_request();
    let signal = this.controller.signal;

    this.api.edit_remark(
      this.data.uid, this.data.fieldname, remark_id, text, signal)
      .then((data) => {
        this.end_request(timeout);
        if (!data || !data.success || !data.remark) {
          this.setState({submitting: false, error: this.translate("error")});
          return;
        }
        this.reconcile(remark_id, data.remark);
      })
      .catch((error) => this.on_error(error, timeout));
  }

  handle_delete(remark_id) {
    if (this.state.submitting) {
      return;
    }
    if (!window.confirm(this.translate("confirm_delete"))) {
      return;
    }

    this.setState({submitting: true, error: null});
    let timeout = this.begin_request();
    let signal = this.controller.signal;

    this.api.delete_remark(
      this.data.uid, this.data.fieldname, remark_id, signal)
      .then((data) => {
        this.end_request(timeout);
        if (!data || !data.success || !data.remark) {
          this.setState({submitting: false, error: this.translate("error")});
          return;
        }
        this.reconcile(remark_id, data.remark);
      })
      .catch((error) => this.on_error(error, timeout));
  }

  start_edit(remark_id) {
    this.setState({editing_id: remark_id, error: null});
  }

  cancel_edit() {
    this.setState({editing_id: null});
  }

  render() {
    let remarks = this.state.remarks;
    // canonical order is newest first; render reversed for ascending
    let ordered = this.state.sort === "asc"
      ? remarks.slice().reverse()
      : remarks;
    return (
      <div className="senaite-remarks-widget">
        {this.data.can_add &&
          <div className="remarks-composer">
            <Avatar
              seed={this.data.current_user_id}
              name={this.data.current_user_id}/>
            <div className="remark-body">
              <RemarkEditor
                mode="add"
                reset_token={this.state.add_token}
                submitting={this.state.submitting}
                placeholder={this.translate("placeholder")}
                label_save={this.translate("add_remarks")}
                on_save={this.handle_add}/>
              {this.state.error &&
                <div className="remarks-error text-danger small mt-1">
                  {this.state.error}
                </div>}
            </div>
          </div>}
        {remarks.length > 1 &&
          <div className="remarks-sortbar">
            <button
              type="button"
              className="remarks-sort-toggle"
              onClick={this.toggle_sort}>
              {this.state.sort === "desc"
                ? this.translate("sort_newest")
                : this.translate("sort_oldest")}
            </button>
          </div>}
        <RemarksList
          remarks={ordered}
          editing_id={this.state.editing_id}
          submitting={this.state.submitting}
          i18n={this.data.i18n}
          on_start_edit={this.start_edit}
          on_cancel_edit={this.cancel_edit}
          on_edit={this.handle_edit}
          on_delete={this.handle_delete}/>
      </div>
    );
  }
}

export default RemarksWidgetController;
