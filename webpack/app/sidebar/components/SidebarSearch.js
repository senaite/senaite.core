import React, {useState, useCallback} from "react";

/**
 * Sidebar Search Component
 * Provides search functionality for filtering navigation items
 */
export const SidebarSearch = ({onSearch, onFocus, onBlur}) => {
  const [query, setQuery] = useState("");

  const handleInput = useCallback((event) => {
    const value = event.target.value;
    setQuery(value);
    if (onSearch) {
      onSearch(value);
    }
  }, [onSearch]);

  const handleFocus = useCallback((event) => {
    if (onFocus) {
      onFocus(event);
    }
  }, [onFocus]);

  const handleBlur = useCallback((event) => {
    if (onBlur) {
      onBlur(event);
    }
  }, [onBlur]);

  return (
    <div id="sidebar-search-container">
      <input
        type="text"
        id="sidebar-search"
        placeholder={window._t ? window._t("Search...") : "Search..."}
        value={query}
        onInput={handleInput}
        onFocus={handleFocus}
        onBlur={handleBlur}
      />
    </div>
  );
};
