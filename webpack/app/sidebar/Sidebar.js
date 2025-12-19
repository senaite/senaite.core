import React, {useState, useCallback, useEffect} from "react";
import {useSidebarState} from "./hooks/useSidebarState";
import {useSidebarResize} from "./hooks/useSidebarResize";
import {useNavigation} from "./hooks/useNavigation";
import {SidebarHeader} from "./components/SidebarHeader";
import {SidebarSearch} from "./components/SidebarSearch";
import {SidebarNavigation} from "./components/SidebarNavigation";

/**
 * Main Sidebar Component
 * Modern sidebar with smooth animations, collapsible sections,
 * and improved accessibility
 *
 * Features:
 * - Toggle button for persistent state
 * - Smooth CSS transitions
 * - Keyboard navigation support (Ctrl/Cmd+B)
 * - Collapsible navigation sections
 * - Search functionality for navigation items
 * - Resizable sidebar with drag handle
 */
export const Sidebar = () => {
  const {isToggled, isMinimized, toggle} = useSidebarState();
  const {width, isResizing, startResize} = useSidebarResize();
  const {navigationData, isLoading, error, showMoreItems} = useNavigation();

  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchActive, setIsSearchActive] = useState(false);

  // Apply classes and styles to the #sidebar container
  useEffect(() => {
    const container = document.getElementById("sidebar");
    if (!container) return;

    const classes = [];
    if (isMinimized) classes.push("minimized");
    if (isToggled) classes.push("toggled");
    if (isLoading) classes.push("loading");
    if (isSearchActive) classes.push("search-active");

    container.className = classes.join(" ");
    container.style.width = isMinimized ? "50px" : `${width}px`;
    container.setAttribute("aria-expanded", !isMinimized);
    container.setAttribute("role", "navigation");
    container.setAttribute("aria-label", "Main navigation");
  }, [isMinimized, isToggled, isLoading, isSearchActive, width]);

  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
  }, []);

  const handleSearchFocus = useCallback(() => {
    setIsSearchActive(true);
    // Expand sidebar if minimized
    if (isMinimized) {
      toggle(true);
    }
  }, [isMinimized, toggle]);

  const handleSearchBlur = useCallback(() => {
    setTimeout(() => {
      setIsSearchActive(false);
    }, 200);
  }, []);

  const handleToggle = useCallback(() => {
    toggle();
  }, [toggle]);

  return (
    <>
      <SidebarHeader isToggled={isToggled} onToggle={handleToggle} />

      <SidebarSearch
        onSearch={handleSearch}
        onFocus={handleSearchFocus}
        onBlur={handleSearchBlur}
      />

      {isLoading && (
        <div className="sidebar-loading">
          <div className="spinner" />
          <span>Loading navigation...</span>
        </div>
      )}

      {error && (
        <div className="sidebar-error">
          {error}
        </div>
      )}

      {!isLoading && !error && (
        <SidebarNavigation
          navigationData={navigationData}
          searchQuery={searchQuery}
          onShowMore={showMoreItems}
        />
      )}

      {!isMinimized && (
        <div
          className={`resize-handle ${isResizing ? "resizing" : ""}`}
          onMouseDown={startResize}
          aria-label="Resize sidebar"
        />
      )}
    </>
  );
};

export default Sidebar;
