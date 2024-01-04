import React from "react";
import {_t} from "../../i18n-wrapper.js"
import "./SearchResults.css"


/** Renders the search results in a table popup
 *
 */
class SearchResults extends React.Component {

  constructor(props) {
    super(props);

    // bind event handlers
    this.on_select = this.on_select.bind(this);
    this.on_page = this.on_page.bind(this);
    this.on_prev_page = this.on_prev_page.bind(this);
    this.on_next_page = this.on_next_page.bind(this);
    this.on_close = this.on_close.bind(this);
    this.on_mouse_over = this.on_mouse_over.bind(this);
  }

  /*
   * Return the key where a value is located in a result record
   */
  get_value_key() {
    return this.props.value_key || "uid";
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
    return columns.map((column) => {
      return column.label
    });
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
    let results = this.get_results();
    let searchterm = this.props.searchterm;
    let allow_user_value = this.props.allow_user_value;

    // allow to select the typed in value
    if (searchterm.length > 0 && allow_user_value) {
      return true;
    }
    return results.length > 0;
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
   * Returns the value of a result object (JSON API record)
   *
   * @returns {String} value of the result
   */
  get_result_value(result) {
    let value_key = this.get_value_key();
    return result[value_key];
  }

  /*
   * Checks whether the value is already in the list of selected values
   *
   * @returns {Boolean} true if the value is already selected, false otherwise
   */
  is_value_selected(value) {
    return this.props.values.indexOf(value) > -1;
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
    let searchterm = this.props.searchterm;
    let allow_user_value = this.props.allow_user_value;

    // Build columns for the search results
    results.forEach((result, index) => {
      let value = this.get_result_value(result);
      let cursor = value ? "pointer" : "not-allowed";
      let title = value ? "" : _t("Missing key");
      rows.push(
        <tr value={value}
            index={index}
            title={title}
            style={{cursor:cursor}}
            className={this.props.focused == index ? "table-active": ""}
            onMouseOver={this.on_mouse_over}
            onClick={this.on_select}>
          {this.build_columns(result)}
        </tr>
      );
    });

    // Add additional row to select the typed in searchterm
    if (allow_user_value && searchterm.length > 0) {
      let index = results.length + 1;
      rows.push(
        <tr value={searchterm}
            index={index}
            title={searchterm}
            style={{cursor: "pointer"}}
            className={this.props.focused == index ? "table-active": ""}
            onMouseOver={this.on_mouse_over}
            onClick={this.on_select}>
          <td className="font-italic text-secondary" colspan={this.props.columns.length}>
            {_t("Select")}: <span className="text-info">{searchterm}</span>
          </td>
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
    let value = this.get_result_value(result);
    let used = this.props.values.indexOf(value) > -1;
    columns.push(
      <td>{used && <i className="fas fa-link text-success"></i>}</td>
    );
    return columns;
  }

  /*
   * Highlight any found match of the searchterm in the text
   *
   * @returns {String} highlighted text
   */
  highlight(text, searchterm) {
    if (searchterm.length == 0) return text;
    try {
      let rx = new RegExp(searchterm, "gi");
      text = text.replaceAll(rx, (m) => {
        return "<span class='font-weight-bold text-info'>"+m+"</span>";
      });
    } catch (error) {
      // pass
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

    let total = this.props.pages;
    let current = this.props.page;
    let padding = this.props.padding;

    let first_page = current - padding > 0 ? current - padding : 1;
    let last_page = current + padding < total ? current + padding : total;

    let crop_before = first_page === 1 ? false : true;
    let crop_after = last_page < total ? true : false;

    for (let page=first_page; page <= last_page; page++) {
      let cls = ["page-item"];
      if (current === page) cls.push("active");

      // crop before the current page
      if (page == first_page && crop_before) {
        // link to first page
        pages.push(
          <li>
            <button className="page-link" page={1} onClick={this.on_page}>1</button>
          </li>
        );
        // placeholder
        pages.push(
          <li>
            <div className="page-link">...</div>
          </li>
        );
        crop_before = false;
      }

      pages.push(
        <li className={cls.join(" ")}>
          <button className="page-link" page={page} onClick={this.on_page}>
            {page}
          </button>
        </li>
      );

      // crop after the current page
      if (page === last_page && crop_after) {
        // placeholder
        pages.push(
          <li>
            <div className="page-link">...</div>
          </li>
        );
        // link to last page
        pages.push(
          <li>
            <button className="page-link" page={total} onClick={this.on_page}>
              {total}
            </button>
          </li>
        );
        crop_after = false;
      }

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
        <i className="fas fa-window-close"></i>
      </button>
    )
  }

  /*
   * Event handler when a result was selected
   */
  on_select(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let value = target.getAttribute("value")
    if (value === null) {
      console.warn("SearchResults::on_select:missing_value!");
      return;
    }
    console.debug("SearchResults::on_select:event=", event);
    if (this.props.on_select) {
      this.props.on_select(value);
    }
  }

  /*
   * Event handler when a page was clicked
   */
  on_page(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let page = target.getAttribute("page")
    console.debug("SearchResults::on_page:event=", event);
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
    console.debug("SearchResults::on_prev_page:event=", event);
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
    console.debug("SearchResults::on_next_page:event=", event);
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
    console.debug("SearchResults::on_close:event=", event);
    if (this.props.on_clear) {
      this.props.on_clear();
    }
  }

  /*
   * Event handler when the mouse is over a row
   */
  on_mouse_over(event) {
    event.preventDefault();
    console.debug("SearchResults::on_mouse_over:event=", event);
    let target = event.currentTarget;
    let index = target.getAttribute("index");
    if (index !== null && this.props.on_mouse_over) {
      this.props.on_mouse_over(index);
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
          {this.props.loading && <span className="spinner-border text-info spinner-border-sm" role="status" aria-hidden="true"></span>}
          {this.build_close_button()}
        </div>
        <table className="table table-sm table-hover small queryselectwidget-results-table">
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

export default SearchResults;
