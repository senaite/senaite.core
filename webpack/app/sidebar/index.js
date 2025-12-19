/**
 * SENAITE Sidebar - React Component
 *
 * Entry point for the sidebar React component
 */

import React from "react";
import ReactDOM from "react-dom";
import Sidebar from "./Sidebar";
import "./styles/sidebar.scss";

/**
 * Initialize the sidebar React component
 */
export const initSidebar = () => {
  const sidebarContainer = document.getElementById("sidebar");

  if (!sidebarContainer) {
    console.warn("Sidebar container not found");
    return;
  }

  ReactDOM.render(<Sidebar />, sidebarContainer);
};

export default Sidebar;
