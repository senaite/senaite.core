import React from "react";

// palette for the deterministic avatar background color
const COLORS = [
  "#5b8def", "#22b8cf", "#51cf66", "#fab005",
  "#ff6b6b", "#cc5de8", "#20c997", "#ff922b",
];


function get_initials(text) {
  if (!text) {
    return "?";
  }
  let parts = text.trim().split(/\s+/);
  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}


function get_color(seed) {
  let value = seed || "";
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
  }
  return COLORS[hash % COLORS.length];
}


/**
 * Round avatar showing the initials of a user, with a deterministic color
 * derived from the seed.
 */
class Avatar extends React.Component {

  render() {
    let label = this.props.name || this.props.seed || "";
    let seed = this.props.seed || label;
    return (
      <div
        className="remark-avatar"
        title={label}
        style={{backgroundColor: get_color(seed)}}>
        {get_initials(label)}
      </div>
    );
  }
}

export default Avatar;
