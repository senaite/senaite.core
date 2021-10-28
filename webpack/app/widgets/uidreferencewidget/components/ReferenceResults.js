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
  }

  get_columns() {
    /*
     * Header columns
     */
    return this.props.columns || [];
  }

  get_column_names() {
    /*
     * Header column names
     */
    let columns = this.get_columns();
    return columns.map((column) => {
      return column.name;
    });
  }

  get_column_labels() {
    /*
     * Header column labels
     */
    let columns = this.get_columns();
    return columns.map((column) => { return column.label });
  }

  get_results() {
    /*
     * List of results records
     */
    return this.props.results || [];
  }

  has_results() {
    /*
     * Checks if we have results records
     */
    return this.get_results().length > 0;
  }

  get_style() {
    return {
      minWidth: this.props.width || "400px",
      backgroundColor: "white",
      zIndex: 999999
    }
  }

  get_result_uid(result) {
    return result.uid || "NO UID FOUND!";
  }

  is_uid_selected(uid) {
    return this.props.uids.indexOf(uid) > -1;
  }

  /*
   * Build Header <th></th> columns
   */
  build_header_columns() {
    let columns = [];
    for (let column of this.get_columns()) {
      let label = column.label || column.title;
      let width = column.width || "auto";
      let align = column.align || "left";
      columns.push(
        <th className="border-top-0" width={width} align={align}>
          {label}
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
   * Build table <td></td> columns
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

  highlight(text, searchterm) {
    let rx = new RegExp(searchterm, "gi");
    let match = text.match(rx);
    if (match) {
      text = text.replace(match, "<span class='font-weight-bold text-info'>"+match+"</span>");
    }
    return text
  }

  /*
   * Build table <tr></tr> rows
   */
  build_rows() {
    let rows = [];
    let results = this.get_results();
    for (let result of results) {
      let uid = this.get_result_uid(result);
      // skip selected UIDs
      // if (this.is_uid_selected(uid)) {
      //   continue;
      // }
      rows.push(
        <tr uid={uid}
            onClick={this.on_select}>
          {this.build_columns(result)}
        </tr>
      );
    }
    return rows
  }

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

  on_select(event) {
    event.preventDefault();
    let target = event.currentTarget;
    let uid = target.getAttribute("uid")
    console.debug("ReferenceResults::on_select:event=", event);
    if (this.props.on_select) {
      this.props.on_select(uid);
    }
  }

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

  render() {
    if (!this.has_results()) {
      return null;
    }
    return (
      <div className={this.props.className}
           style={this.get_style()}>
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
