import React from "react";
import "./Avatar.css";

// palette for the deterministic avatar background color
const COLORS = [
  "#5b8def", "#22b8cf", "#51cf66", "#fab005",
  "#ff6b6b", "#cc5de8", "#20c997", "#ff922b",
];


/**
 * Return the initials (max 2 letters) for a name or label
 */
export const get_initials = (text) => {
  if (!text) {
    return "?";
  }
  let parts = text.trim().split(/\s+/);
  if (parts.length === 1) {
    return parts[0].slice(0, 2).toUpperCase();
  }
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
};


/**
 * Return a deterministic color from the palette for the given seed
 */
export const get_color = (seed) => {
  let value = seed || "";
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = (hash * 31 + value.charCodeAt(i)) >>> 0;
  }
  return COLORS[hash % COLORS.length];
};


/**
 * Reusable round avatar showing the initials of a user/label, with a
 * deterministic background color derived from the seed.
 *
 * Props:
 *   name       label used to compute the initials and the title
 *   seed       value the color is derived from (defaults to `name`)
 *   size       diameter in pixels (default: 34)
 *   className  additional CSS class(es) to append
 */
class Avatar extends React.Component {

  render() {
    let label = this.props.name || this.props.seed || "";
    let seed = this.props.seed || label;
    let size = this.props.size || 34;
    let css_class = "senaite-avatar";
    if (this.props.className) {
      css_class = `${css_class} ${this.props.className}`;
    }
    let style = {
      backgroundColor: get_color(seed),
      width: `${size}px`,
      height: `${size}px`,
      fontSize: `${Math.round(size * 0.4)}px`,
    };
    return (
      <div className={css_class} title={label} style={style}>
        {get_initials(label)}
      </div>
    );
  }
}

export default Avatar;
