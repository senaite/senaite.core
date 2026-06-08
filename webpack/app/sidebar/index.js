/**
 * SENAITE Sidebar - React Component
 *
 * Entry point for the sidebar React component
 */

import React from "react";
import {createRoot} from "react-dom/client";
import Sidebar from "./Sidebar";
import "./styles/sidebar.scss";

/**
 * Sidebar API object for backwards compatibility
 * Provides access to the sidebar component and common operations
 */
export const SidebarAPI = {
  component: null,
  container: null,

  /**
   * Get the sidebar DOM element
   */
  getElement() {
    return document.getElementById("sidebar");
  },

  /**
   * Check if sidebar is toggled (expanded)
   */
  isToggled() {
    if (typeof window !== "undefined" && window.site) {
      return window.site.read_cookie("sidebar-toggle") === "true";
    }
    return false;
  },

  /**
   * Check if sidebar is minimized
   */
  isMinimized() {
    const el = this.getElement();
    return el ? el.classList.contains("minimized") : true;
  },

  /**
   * Toggle sidebar programmatically
   */
  toggle(value) {
    const el = this.getElement();
    if (!el) return;

    const newValue = typeof value === "boolean" ? value : !this.isToggled();

    if (typeof window !== "undefined" && window.site) {
      window.site.set_cookie("sidebar-toggle", newValue);
    }

    if (newValue) {
      el.classList.add("toggled");
      el.classList.remove("minimized");
    } else {
      el.classList.remove("toggled");
      el.classList.add("minimized");
    }
  },

  /**
   * Minimize sidebar
   */
  minimize() {
    this.toggle(false);
  },

  /**
   * Maximize sidebar
   */
  maximize() {
    this.toggle(true);
  },
};

/**
 * Initialize the sidebar React component
 */
export const initSidebar = () => {
  const sidebarContainer = document.getElementById("sidebar");

  if (!sidebarContainer) {
    console.warn("Sidebar container not found");
    return null;
  }

  SidebarAPI.container = sidebarContainer;

  // Use React 18 createRoot API
  const root = createRoot(sidebarContainer);
  root.render(<Sidebar />);

  return SidebarAPI;
};

export default Sidebar;
