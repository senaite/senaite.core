import React from "react";

/**
 * Sidebar Header Component
 * Displays the toggle button for expanding/collapsing the sidebar
 */
export const SidebarHeader = ({isToggled, onToggle}) => {
  const iconClass = isToggled ? "fa fa-times" : "fa fa-bars";

  return (
    <div id="sidebar-header">
      <button
        type="button"
        onClick={onToggle}
        title="Toggle sidebar (Ctrl/Cmd+B)">
        <i className={`sidebar-toggle-icon ${iconClass}`} />
      </button>
    </div>
  );
};
