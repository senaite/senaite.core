import React from 'react';

class Button extends React.Component {

  render() {
    return (
      <button id={this.props.id}
              dangerouslySetInnerHTML={{__html: this.props.title}}
              onClick={this.props.onClick}
              className={this.props.className}>
      </button>
    );
  }
}

export default Button;
