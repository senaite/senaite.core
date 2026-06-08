import React from "react";
import {SidebarItem} from "./SidebarItem";

/**
 * Sidebar Navigation Component
 * Renders the navigation tree
 */
export const SidebarNavigation = ({
  navigationData,
  searchQuery,
  onShowMore,
}) => {
  if (!navigationData || navigationData.length === 0) {
    return null;
  }

  return (
    <div className="sidebar-navigation">
      <ul className="nav-level-1">
        {navigationData.map((item) => (
          <SidebarItem
            key={item.id}
            item={item}
            level={1}
            searchQuery={searchQuery}
            onShowMore={onShowMore}
          />
        ))}
      </ul>
    </div>
  );
};
