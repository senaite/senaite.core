import React from "react";
import ReactDOM from "react-dom";


class ReferenceResults extends React.Component {

  constructor(props) {
    super(props);

    // bind event handlers
    this.on_select = this.on_select.bind(this);
    this.on_page = this.on_page.bind(this);
    this.on_prev_page = this.on_prev_page.bind(this);
    this.on_next_page = this.on_next_page.bind(this);
    this.on_close = this.on_close.bind(this);
  }

  /*
   * Return the header columns config
   *
   * @returns {Array} of column config objects
   */
  get_columns() {
    return this.props.columns || [];
  }

  /*
   * Return only the (field-)names of the columns config
   *
   * @returns {Array} of column names
   */
  get_column_names() {
    let columns = this.get_columns();
    return columns.map((column) => {
      return column.name;
    });
  }

  /*
   * Return only the labels of the columns config
   *
   * @returns {Array} of column labels
   */
  get_column_labels() {
    let columns = this.get_columns();
    return columns.map((column) => { return column.label });
  }

  /*
   * Return the search results
   *
   * @returns {Array} of result objects (items of `senaite.jsonapi` response)
   */
  get_results() {
    return this.props.results || [];
  }

  /*
   * Checks if results are available
   *
   * @returns {Boolean} true if there are results, false otherwise
   */
  has_results() {
    return this.get_results().length > 0;
  }

  /*
   * Returns the style object for the dropdown table
   *
   * @returns {Object} of ReactJS CSS styles
   */
  get_style() {
    return {
      minWidth: this.props.width || "400px",
      backgroundColor: "white",
      zIndex: 999999
    }
  }

  /*
   * Returns the UID of a result object
   *
   * @returns {String} UID of the result
   */
  get_result_uid(result) {
    return result.uid || "NO UID FOUND!";
  }

  /*
   * Checks wehter the UID is already in the list of selected UIDs
   *
   * @returns {Boolean} true if the UID is already selected, false otherwise
   */
  is_uid_selected(uid) {
    return this.props.uids.indexOf(uid) > -1;
  }

  /*
   * Build Header <th></th> columns
   *
   * @returns {Array} of <th>...</th> columns
   */
  build_header_columns() {
    let columns = [];
    for (let column of this.get_columns()) {
      let label = column.label || column.title;
      let width = column.width || "auto";
      let align = column.align || "left";
      columns.push(
        <th className="border-top-0" width={width} align={align}>
          {_t(label)}
        </th>
      );
    }
    // Append additional column for usage state
    columns.push(
      <th className="border-top-0" width="1"></th>
    )
    return columns;
  }

  /*
   * Build table <tr></tr> rows
   *
   * @returns {Array} of <tr>...</tr> rows
   */
  build_rows() {
    let rows = [];
    let results = this.get_results();
    for (let result of results) {
      let uid = this.get_result_uid(result);
      rows.push(
        <tr uid={uid}
            onClick={this.on_select}>
          {this.build_columns(result)}
        </tr>
      );
    }
    return rows
  }

  /*
   * Build Header <td></td> columns
   *
   * @returns {Array} of <td>...</td> columns
   */
  build_columns(result) {
    let columns = []
    let searchterm = this.props.searchterm || "";
    for (let name of this.get_column_names()) {
      let value = result[name];
      let highlighted = this.highlight(value, searchterm);
      columns.push(
        <td dangerouslySetInnerHTML={{__html: highlighted}}></td>
      );
    }
    let uid = result.uid;
    let used = this.props.uids.indexOf(uid) > -1;
    columns.push(
      <td>{used && <i class="fas fa-link text-success"></i>}</td>
    );
    return columns;
  }

  /*
   * Highlight any found match of the searchterm in the text
   *
   * @returns {String} highlighted text
   */
  highlight(text, searchterm) {
    let rx = new RegExp(searchterm, "gi");
    let match = text.match(rx);
    if (match) {
      text = text.replace(match, "<span class='font-weight-bold text-info'>"+match+"</span>");
    }
    return text
  }

  /*
   * Build pagination <li>...</li> items
   *
   * @returns {Array} Pagination JSX
   */
  build_pages() {
    let pages = [];
    for (let page=1; page <= this.props.pages; page++) {
      let cls = ["page-item"];
      if (this.props.page == page) cls.push("active");
      pages.push(
        <li className={cls.join(" ")}>
          <button className="page-link" page={page} onClick={this.on_page}>
            {page}
          </button>
        </li>
      );
    }
    return pages;
  }

  /*
   * Build pagination next button
   *
   * @returns {Array} Next button JSX
   */
  build_next_button() {
    let cls = ["page-item"]
    if (!this.props.next_url) cls.push("disabled")
    return (
      <li className={cls.join(" ")}>
        <button className="page-link" onClick={this.on_next_page}>
          Next
        </button>
      </li>
    )
  }

  /*
   * Build pagination previous button
   *
   * @returns {Array} Previous button JSX
   */
  build_prev_button() {
    let cls = ["page-item"]
    if (!this.props.prev_url) cls.push("disabled")
    return (
      <li className={cls.join(" ")}>
        <button className="page-link" onClick={this.on_prev_page}>
          Previous
        </button>
      </li>
    )
  }

  /*
   * Build results dropdown close button
   *
   * @returns {Array} Close button JSX
   */
  build_close_button() {
    return (
      <button className="btn btn-sm btn-link" onClick={this.on_close}>
        <i class="fas fa-window-close"></i>
      </button>
    )
  }

  /*
   * Event handler when a result was selected
   */
  on_select(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let uid = target.getAttribute("uid")
    console.debug("ReferenceResults::on_select:event=", event);
    if (this.props.on_select) {
      this.props.on_select(uid);
    }
  }

  /*
   * Event handler when a page was clicked
   */
  on_page(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let page = target.getAttribute("page")
    console.debug("ReferenceResults::on_page:event=", event);
    if (page == this.props.page) {
      return;
    }
    if (this.props.on_page) {
      this.props.on_page(page);
    }
  }

  /*
   * Event handler when the pagination previous button was clicked
   */
  on_prev_page(event) {
    event.preventDefault();
    console.debug("ReferenceResults::on_prev_page:event=", event);
    let page = this.props.page;
    if (page < 2) {
      console.warn("No previous pages available!");
      return;
    }
    if (this.props.on_page) {
      this.props.on_page(page - 1);
    }
  }

  /*
   * Event handler when the pagination next button was clicked
   */
  on_next_page(event) {
    event.preventDefault();
    console.debug("ReferenceResults::on_next_page:event=", event);
    let page = this.props.page;
    if (page + 1 > this.props.pages) {
      console.warn("No next pages available!");
      return;
    }
    if (this.props.on_page) {
      this.props.on_page(page + 1);
    }
  }

  /*
   * Event handler when the dropdown close button was clicked
   */
  on_close(event) {
    event.preventDefault();
    console.debug("ReferenceResults::on_close:event=", event);
    if (this.props.on_clear) {
      this.props.on_clear();
    }
  }

  /*
   * Render the reference results selection
   */
  render() {
    if (!this.has_results()) {
      return null;
    }
    return (
      <div className={this.props.className}
           style={this.get_style()}>
        <div style={{position: "absolute", top: 0, right: 0}}>
          {this.build_close_button()}
        </div>
        <table className="table table-sm table-hover small">
          <thead>
            <tr>
              {this.build_header_columns()}
            </tr>
          </thead>
          <tbody>
            {this.build_rows()}
          </tbody>
        </table>
        {this.props.pages > 1 &&
         <nav>
           <ul className="pagination pagination-sm justify-content-center">
             {this.build_prev_button()}
             {this.build_pages()}
             {this.build_next_button()}
           </ul>
         </nav>
        }
      </div>
    );
  }
}

export default ReferenceResults;
