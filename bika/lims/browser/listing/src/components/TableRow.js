import React from 'react';

import TableCell from "./TableCell.js";


class Row extends React.Component {
  /** Contents Table Row (tr)
   */

  buildTableCells() {
    /** Build the table cells (td)
     */
    let cells = [];
    let item = this.props.item;

    /* Iterate over the columns to create the cells in the right order */
    for (let [key, column] of Object.entries(this.props.columns)) {

      // Skip hidden columns
      if (!column.toggle) {
        continue;
      }

      let value = item.replace[key] || item[key];
      cells.push(
        <TableCell key={key}
                   className={key}
                   value={value} />
      );
    }
    return cells;
  }

  render() {
    return (
      <tr className={this.props.className}>
        {this.buildTableCells()}
      </tr>
    );
  }
}

export default Row;
