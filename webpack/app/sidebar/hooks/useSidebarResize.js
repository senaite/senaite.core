import {useState, useCallback, useEffect, useRef} from "react";

/**
 * Custom hook for managing sidebar resize functionality
 * Handles mouse drag events and width persistence via cookies
 */
export const useSidebarResize = (
  minWidth = 200,
  maxWidth = 600,
  widthCookieKey = "sidebar-width"
) => {
  const [width, setWidth] = useState(() => {
    if (typeof window !== "undefined" && window.site) {
      const savedWidth = window.site.read_cookie(widthCookieKey);
      if (savedWidth) {
        const parsedWidth = parseInt(savedWidth, 10);
        if (parsedWidth >= minWidth && parsedWidth <= maxWidth) {
          return parsedWidth;
        }
      }
    }
    return 200;
  });

  const [isResizing, setIsResizing] = useState(false);
  const resizeStartX = useRef(0);
  const resizeStartWidth = useRef(0);

  const startResize = useCallback((event) => {
    event.preventDefault();
    setIsResizing(true);
    resizeStartX.current = event.clientX;
    resizeStartWidth.current = width;
    document.body.style.userSelect = "none";
    document.body.style.cursor = "ew-resize";
  }, [width]);

  const resize = useCallback((event) => {
    if (!isResizing) return;

    event.preventDefault();
    const delta = event.clientX - resizeStartX.current;
    let newWidth = resizeStartWidth.current + delta;

    newWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    setWidth(newWidth);
  }, [isResizing, minWidth, maxWidth]);

  const stopResize = useCallback(() => {
    if (!isResizing) return;

    setIsResizing(false);
    document.body.style.userSelect = "";
    document.body.style.cursor = "";

    if (typeof window !== "undefined" && window.site) {
      window.site.set_cookie(widthCookieKey, width);
    }
  }, [isResizing, width, widthCookieKey]);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener("mousemove", resize);
      document.addEventListener("mouseup", stopResize);

      return () => {
        document.removeEventListener("mousemove", resize);
        document.removeEventListener("mouseup", stopResize);
      };
    }
  }, [isResizing, resize, stopResize]);

  return {
    width,
    isResizing,
    startResize,
  };
};
