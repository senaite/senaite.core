import React, {useState, useCallback, useRef} from "react";
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

  const sidebarRef = useRef(null);

  const handleSearch = useCallback((query) => {
    setSearchQuery(query);
  }, []);

  const handleSearchFocus = useCallback(() => {
    setIsSearchActive(true);
  }, []);

  const handleSearchBlur = useCallback(() => {
    setTimeout(() => {
      setIsSearchActive(false);
    }, 200);
  }, []);

  const handleToggle = useCallback(() => {
    toggle();
  }, [toggle]);

  const sidebarClasses = ["sidebar"];
  if (isMinimized) {
    sidebarClasses.push("minimized");
  }
  if (isToggled) {
    sidebarClasses.push("toggled");
  }
  if (isLoading) {
    sidebarClasses.push("loading");
  }
  if (isSearchActive) {
    sidebarClasses.push("search-active");
  }

  const sidebarStyle = {
    width: isMinimized ? "50px" : `${width}px`,
  };

  return (
    <div
      id="sidebar"
      ref={sidebarRef}
      className={sidebarClasses.join(" ")}
      style={sidebarStyle}
      aria-expanded={!isMinimized}
      role="navigation"
      aria-label="Main navigation"
    >
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
    </div>
  );
};

export default Sidebar;
