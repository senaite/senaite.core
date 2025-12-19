import React from "react";

/**
 * Sidebar Header Component
 * Displays the toggle button for expanding/collapsing the sidebar
 */
export const SidebarHeader = ({isToggled, onToggle}) => {
  return (
    <div id="sidebar-header">
      <button
        type="button"
        onClick={onToggle}
        title="Toggle sidebar"
        aria-label="Toggle sidebar"
        aria-expanded={isToggled}
      >
        <i className="sidebar-toggle-icon" />
      </button>
    </div>
  );
};
