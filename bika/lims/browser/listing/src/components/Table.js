import React from "react";

import TableRow from "./TableRow.js";


class Table extends React.Component {
  /** Contents Table
   */

  constructor(props) {
    super(props);
  }

  componentDidMount() {
  }

  buildHeaderColumns() {
    let columns = [];
    for (let [key, value] of Object.entries(this.props.columns)) {
      if (!value.toggle) {
        continue;
      }
      columns.push(
        <th key={key}>{value.title}</th>
      );
    }
    return columns;
  }

  buildFolderItems() {
    /** Build table rows and cell for the given items
     */
    let rows = [];
    for (let [index, item] of Object.entries(this.props.folderitems)) {

      rows.push(
        <TableRow className={item.state_class}
                  key={index}
                  item={item}
                  review_states={this.props.review_states}
                  columns={this.props.columns} />
      );
    }
    return rows;
  }

  render() {
    return (
      <table id={this.props.id}
             className={this.props.className}>
        <thead>
          <tr>
            {this.buildHeaderColumns()}
          </tr>
        </thead>
        <tbody>
          {this.buildFolderItems()}
        </tbody>
        <tfoot>
        </tfoot>
      </table>
    );
  }
}


export default Table;
