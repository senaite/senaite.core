import React, {useState, useCallback, useEffect} from "react";
import {createPortal} from "react-dom";
import {useSidebarState} from "./hooks/useSidebarState";
import {useSidebarResize} from "./hooks/useSidebarResize";
import {useNavigation} from "./hooks/useNavigation";
import {SidebarHeader} from "./components/SidebarHeader";
import {SidebarSearch} from "./components/SidebarSearch";
import {SidebarNavigation} from "./components/SidebarNavigation";

/**
 * Main Sidebar Component
 * Modern sidebar with smooth animations and collapsible sections
 *
 * Features:
 * - Toggle button for persistent state
 * - Smooth CSS transitions
 * - Keyboard navigation support (Ctrl/Cmd+B)
 * - Collapsible navigation sections
 * - Search functionality for navigation items
 * - Resizable sidebar with drag handle
 * - Mobile-responsive with overlay and slide-in animation
 * - Body scroll lock when mobile sidebar is open
 */
export const Sidebar = () => {
  const {isToggled, isMinimized, toggle} = useSidebarState();
  const {width, isResizing, startResize} = useSidebarResize();
  const {navigationData, isLoading, error, showMoreItems} = useNavigation();

  const [searchQuery, setSearchQuery] = useState("");
  const [isSearchActive, setIsSearchActive] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile viewport
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkMobile();
    window.addEventListener("resize", checkMobile);
    return () => window.removeEventListener("resize", checkMobile);
  }, []);

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
  }, [isMinimized, isToggled, isLoading, isSearchActive, width]);

  // Manage body scroll for mobile
  useEffect(() => {
    if (isMobile && isToggled && !isMinimized) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobile, isToggled, isMinimized]);

  // Handle backdrop click to close sidebar
  const handleBackdropClick = useCallback(() => {
    if (isMobile) {
      toggle(false);
    }
  }, [isMobile, toggle]);

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

  const showBackdrop = isMobile && isToggled && !isMinimized;

  return (
    <>
      {/* Mobile backdrop - rendered via portal to body */}
      {createPortal(
        <div
          className={`sidebar-backdrop ${showBackdrop ? "show" : ""}`}
          onClick={handleBackdropClick}
        />,
        document.body
      )}

      {/* On mobile, render toggle button outside sidebar via portal */}
      {isMobile && !isToggled ? (
        createPortal(
          <SidebarHeader isToggled={isToggled} onToggle={handleToggle} />,
          document.body
        )
      ) : (
        <SidebarHeader isToggled={isToggled} onToggle={handleToggle} />
      )}

      <SidebarSearch
        onSearch={handleSearch}
        onFocus={handleSearchFocus}
        onBlur={handleSearchBlur}
      />

      {isLoading && (
        <div className="sidebar-loading">
          <div className="spinner" />
          <span>{window._t ? window._t("Loading navigation...") : "Loading navigation..."}</span>
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
        />
      )}
    </>
  );
};

export default Sidebar;
