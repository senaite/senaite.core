import {useState, useEffect, useCallback} from "react";

/**
 * Custom hook for fetching and managing navigation data
 */
export const useNavigation = () => {
  const [navigationData, setNavigationData] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchNavigation = useCallback(async (showMore = false) => {
    try {
      setIsLoading(true);
      setError(null);

      const portalUrl = window.portal_url || "/";
      const currentUrl = document.body.dataset.baseUrl ||
                         window.location.href;

      const url = `${portalUrl}/@@sidebar-navigation-json?current_url=${encodeURIComponent(currentUrl)}&show_more=${showMore}`;

      const response = await fetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "same-origin",
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || "Failed to fetch navigation");
      }

      setNavigationData(result.data);
    } catch (err) {
      console.error("Error fetching sidebar navigation:", err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNavigation();
  }, [fetchNavigation]);

  const showMoreItems = useCallback(() => {
    fetchNavigation(true);
  }, [fetchNavigation]);

  return {
    navigationData,
    isLoading,
    error,
    showMoreItems,
  };
};
