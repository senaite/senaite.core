import React from 'react';


class TableCell extends React.Component {
  /** Contents Table Cell (td)
   */

  constructor(props) {
    super(props);
  }

  componentDidMount() {
  }

  render() {
    return (
      <td className={this.props.className}
          dangerouslySetInnerHTML={{__html: this.props.value}}>
      </td>
    );
  }
}

export default TableCell;
