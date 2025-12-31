import {useState, useEffect, useCallback} from "react";

/**
 * Custom hook for managing sidebar toggle state
 * Handles cookie persistence and keyboard navigation
 */
export const useSidebarState = (cookieKey = "sidebar-toggle") => {
  const [isToggled, setIsToggled] = useState(() => {
    if (typeof window !== "undefined" && window.site) {
      return window.site.read_cookie(cookieKey) === "true";
    }
    return false;
  });

  const [isMinimized, setIsMinimized] = useState(!isToggled);

  const toggle = useCallback((value) => {
    const newValue = typeof value === "boolean" ? value : !isToggled;
    setIsToggled(newValue);
    setIsMinimized(!newValue);

    if (typeof window !== "undefined" && window.site) {
      window.site.set_cookie(cookieKey, newValue);
    }
  }, [isToggled, cookieKey]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if ((event.ctrlKey || event.metaKey) && event.key === "b") {
        event.preventDefault();
        toggle();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [toggle]);

  return {
    isToggled,
    isMinimized,
    toggle,
  };
};
