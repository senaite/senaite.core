/**
 * Form Tabbing Component
 *
 * Remembers the active tab in Bootstrap 4 tabs for content edit and view forms
 * Uses URL parameter to persist the active tab across page reloads
 */

import $ from "jquery";

class FormTabbing {
  constructor() {
    this.TAB_PARAM = "tab";
  }

  /**
   * Initialize form tabbing functionality
   */
  init() {
    const tabs = document.querySelectorAll(".nav-tabs a[data-toggle='tab']");
    if (tabs.length === 0) {
      console.debug("FormTabbing: No tabs found");
      return;
    }

    console.debug(`FormTabbing: Found ${tabs.length} tabs`);

    // Restore the tab from URL parameter
    this.restoreActiveTab();

    // Update tab links to modify URL on click
    this.updateTabLinks();

    // Add tab parameter to edit/view links
    this.addTabParameterToLinks();

    // Listen for tab changes to update URL and links using jQuery
    $(".nav-tabs a[data-toggle='tab']").on("shown.bs.tab", (event) => {
      const tabId = $(event.target).attr("id");
      if (tabId) {
        this.updateUrl(tabId);
        // Update edit/view links when tab changes
        this.addTabParameterToLinks();
      }
    });

    console.debug("FormTabbing: Tab memory initialized");
  }

  /**
   * Get URL parameter value
   */
  getUrlParameter(name) {
    const url = window.location.href;
    const escapedName = name.replace(/[\[\]]/g, "\\$&");
    const regex = new RegExp("[?&]" + escapedName + "(=([^&#]*)|&|#|$)");
    const results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return "";
    return decodeURIComponent(results[2].replace(/\+/g, " "));
  }

  /**
   * Update URL parameter
   */
  updateUrlParameter(param, value) {
    let url = window.location.href;
    const regex = new RegExp("([?&])" + param + "=.*?(&|$)", "i");
    const separator = url.indexOf("?") !== -1 ? "&" : "?";

    if (url.match(regex)) {
      return url.replace(regex, "$1" + param + "=" + value + "$2");
    } else {
      return url + separator + param + "=" + value;
    }
  }

  /**
   * Update URL with tab parameter
   */
  updateUrl(tabId) {
    try {
      const newUrl = this.updateUrlParameter(this.TAB_PARAM, tabId);
      window.history.replaceState({}, "", newUrl);
      console.debug(`FormTabbing: Updated URL with tab ${tabId}`);
    } catch (e) {
      console.warn("FormTabbing: Could not update URL", e);
    }
  }

  /**
   * Restore the active tab from URL parameter
   */
  restoreActiveTab() {
    try {
      const savedTabId = this.getUrlParameter(this.TAB_PARAM);

      if (!savedTabId) {
        console.debug("FormTabbing: No tab parameter found");
        return;
      }

      console.debug(`FormTabbing: Looking for tab with ID: ${savedTabId}`);

      let savedTab = document.getElementById(savedTabId);
      if (!savedTab) {
        console.warn(`FormTabbing: Tab element with ID "${savedTabId}" not found in DOM`);

        // Try to find the tab by href as fallback
        const tabByHref = document.querySelector(`.nav-tabs a[href="#${savedTabId.replace("-tab", "")}"]`);
        if (tabByHref) {
          savedTab = tabByHref;
          console.debug("FormTabbing: Found tab by href instead");
        } else {
          console.warn("FormTabbing: Could not find tab by href either");
          return;
        }
      }

      // Remove active class from all tabs and panes
      $(".nav-tabs .nav-link").removeClass("active");
      $(".tab-pane").removeClass("active show");

      // Activate the saved tab using Bootstrap's tab method
      $(savedTab).tab("show");
      console.info(`FormTabbing: Successfully restored tab ${savedTabId}`);
    } catch (e) {
      console.error("FormTabbing: Error restoring tab", e);
    }
  }

  /**
   * Update tab links to modify URL on click
   */
  updateTabLinks() {
    $(".nav-tabs a[data-toggle='tab']").on("click", (event) => {
      const $tab = $(event.currentTarget);
      const originalHref = $tab.attr("href");
      if (originalHref && originalHref.indexOf("#") === 0) {
        const tabId = $tab.attr("id");
        if (tabId) {
          // Update URL with the new tab parameter
          setTimeout(() => {
            this.updateUrl(tabId);
          }, 0);
        }
      }
    });
  }

  /**
   * Add tab parameter to edit/view links
   */
  addTabParameterToLinks() {
    let currentTab = this.getUrlParameter(this.TAB_PARAM);
    if (!currentTab) {
      const $activeTab = $(".nav-tabs .nav-link.active");
      if ($activeTab.length > 0) {
        currentTab = $activeTab.attr("id");
      }
    }

    if (!currentTab) {
      return;
    }

    // Find edit and view links and add the tab parameter
    const linkSelectors = [
      "#contentview-edit a",
      "#contentview-view a",
    ];

    $(linkSelectors.join(", ")).each((index, link) => {
      const $link = $(link);
      let href = $link.attr("href");

      if (!href || href.indexOf("#") === 0) {
        return;
      }

      // Skip external links
      if (href.indexOf("http") === 0 && href.indexOf(window.location.hostname) === -1) {
        return;
      }

      // Remove existing tab parameter if present
      const regex = new RegExp("([?&])" + this.TAB_PARAM + "=.*?(&|$)", "i");
      href = href.replace(regex, "$1").replace(/[?&]$/, "");

      // Add new tab parameter
      const separator = href.indexOf("?") !== -1 ? "&" : "?";
      const newHref = href + separator + this.TAB_PARAM + "=" + encodeURIComponent(currentTab);
      $link.attr("href", newHref);
      console.debug("FormTabbing: Updated tab parameter on link: " + newHref);
    });
  }

}

export default FormTabbing;
