/* SENAITE Sidebar
 *
 * Modern sidebar inspired by Claude.ai's design with smooth animations,
 * collapsible sections, and improved accessibility.
 *
 * Features:
 * - Auto-expand on hover with configurable delay
 * - Toggle button for persistent state
 * - Smooth CSS transitions
 * - Keyboard navigation support
 * - Collapsible navigation sections
 * - Search functionality for navigation items
 */

class Sidebar {

  constructor(config) {

    this.config = Object.assign({
      "el": "sidebar",
      "toggle_el": "sidebar-header",
      "search_el": "sidebar-search",
      "cookie_key": "sidebar-toggle",
    }, config);

    // Track navigation data
    this.navigation_data = null;
    this.navigation_container = null;

    // Bind "this" context when called
    this.fetch_navigation = this.fetch_navigation.bind(this);
    this.render_navigation = this.render_navigation.bind(this);
    this.maximize = this.maximize.bind(this);
    this.minimize = this.minimize.bind(this);
    this.on_click = this.on_click.bind(this);
    this.on_search_focus = this.on_search_focus.bind(this);
    this.on_search_blur = this.on_search_blur.bind(this);
    this.on_search_input = this.on_search_input.bind(this);
    this.toggle_section = this.toggle_section.bind(this);

    // Initialize sidebar element
    this.el = document.getElementById(this.config.el);
    if (!this.el) {
      console.warn("Sidebar element not found:", this.config.el);
      return this;
    }

    // Setup event handlers
    this.setup_toggle_button();
    this.setup_search();
    this.setup_collapsible_sections();
    this.setup_keyboard_navigation();

    // Restore toggle state from cookie
    if (this.is_toggled()) {
      this.el.classList.remove("minimized");
      this.el.classList.add("toggled");
    }

    // Fetch and render navigation from JSON API
    this.fetch_navigation();

    return this;
  }

  /**
   * Fetch navigation data from JSON API
   */
  async fetch_navigation() {
    try {
      // Add loading state
      this.el.classList.add("loading");

      // Get the portal URL
      const portal_url = window.portal_url || "/";

      // Get the current page URL for highlighting
      const current_url = window.location.href;

      // Fetch navigation data with current URL parameter
      const response = await fetch(
        `${portal_url}/@@sidebar-navigation-json?current_url=${encodeURIComponent(current_url)}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "same-origin",
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || "Failed to fetch navigation");
      }

      // Store navigation data
      this.navigation_data = result.data;

      // Render navigation
      this.render_navigation();

      // Remove loading state
      this.el.classList.remove("loading");
    } catch (error) {
      console.error("Error fetching sidebar navigation:", error);

      // Remove loading state
      this.el.classList.remove("loading");

      // Show error message
      this.show_error("Failed to load navigation");
    }
  }

  /**
   * Render navigation from data
   */
  render_navigation() {
    if (!this.navigation_data) {
      return;
    }

    // Find or create navigation container
    this.navigation_container = this.el.querySelector(
      ".sidebar-navigation");

    if (!this.navigation_container) {
      this.navigation_container = document.createElement("div");
      this.navigation_container.className = "sidebar-navigation";
      this.el.appendChild(this.navigation_container);
    }

    // Clear existing content
    this.navigation_container.innerHTML = "";

    // Create navigation list
    const nav_list = this.render_navigation_list(
      this.navigation_data, 1);

    this.navigation_container.appendChild(nav_list);

    // Re-setup collapsible sections after rendering
    this.setup_collapsible_sections();
  }

  /**
   * Render navigation list recursively
   */
  render_navigation_list(items, level) {
    const ul = document.createElement("ul");
    ul.className = `nav-level-${level}`;

    items.forEach(item => {
      const li = this.render_navigation_item(item, level);
      if (li) {
        ul.appendChild(li);
      }
    });

    return ul;
  }

  /**
   * Render a single navigation item
   */
  render_navigation_item(item, level) {
    // Skip inactive items
    if (item.review_state === "inactive") {
      return null;
    }

    const li = document.createElement("li");
    li.className = "navTreeItem";

    // Add state classes
    if (item.is_current) {
      li.classList.add("active", "navTreeCurrentNode");
    }
    if (item.is_parent) {
      li.classList.add("navTreeCurrentParent");
    }
    if (item.children && item.children.length > 0) {
      // Expand if this item or any child is current
      const should_expand = item.is_current || item.is_parent;
      li.classList.add("navTreeFolderish");
      li.classList.add(should_expand ? "expanded" : "collapsed");
    }

    // Create link
    const link = document.createElement("a");
    link.href = item.url;
    link.className = "navTreeLink";
    link.setAttribute("data-id", item.id);
    link.setAttribute("data-portal-type", item.portal_type);

    if (item.description) {
      link.setAttribute("title", item.description);
    }

    // Add icon if available
    if (item.icon) {
      const icon_wrapper = document.createElement("span");
      icon_wrapper.className = "node-icon";

      // SENAITE uses SVG icons from theme resources
      // Icon path is like "senaite_theme/icon/clientfolder"
      const icon_img = document.createElement("img");
      icon_img.src = `${window.portal_url || ""}/${item.icon}`;
      icon_img.alt = "";
      icon_img.className = "nav-icon";

      icon_wrapper.appendChild(icon_img);
      link.appendChild(icon_wrapper);
    }

    // Add title
    const title = document.createElement("span");
    title.className = level === 1 ? "node-title" : "child-title";
    title.textContent = item.title;
    link.appendChild(title);

    li.appendChild(link);

    // Add children if any
    if (item.children && item.children.length > 0) {
      const child_list = this.render_navigation_list(
        item.children, level + 1);
      li.appendChild(child_list);
    }

    return li;
  }

  /**
   * Show error message
   */
  show_error(message) {
    const error_el = document.createElement("div");
    error_el.className = "sidebar-error";
    error_el.textContent = message;

    if (this.navigation_container) {
      this.navigation_container.innerHTML = "";
      this.navigation_container.appendChild(error_el);
    }
  }

  /**
   * Setup toggle button event handler
   */
  setup_toggle_button() {
    this.toggle_el = document.getElementById(this.config.toggle_el);
    if (this.toggle_el) {
      this.toggle_el.addEventListener("click", this.on_click);
      // Add tooltip for accessibility
      this.toggle_el.setAttribute("title", "Toggle sidebar");
      this.toggle_el.setAttribute("aria-label", "Toggle sidebar");
    }
  }


  /**
   * Setup search functionality
   */
  setup_search() {
    this.search_el = document.getElementById(this.config.search_el);
    if (this.search_el) {
      this.search_el.addEventListener("focus", this.on_search_focus);
      this.search_el.addEventListener("blur", this.on_search_blur);
      this.search_el.addEventListener("input", this.on_search_input);
    }
  }

  /**
   * Setup collapsible sections
   */
  setup_collapsible_sections() {
    const section_headers = this.el.querySelectorAll(
      ".nav-level-1 > li > a");
    section_headers.forEach(header => {
      // Add click handler for collapsible sections
      const parent_li = header.parentElement;
      const has_children = parent_li.querySelector("ul");

      if (has_children) {
        header.addEventListener("click", (event) => {
          // Check if clicking the caret (exact target or parent)
          const target = event.target;
          const is_caret = target.classList.contains("caret") ||
                          target.closest(".caret");

          // Only toggle if clicking the caret
          // In all other cases (including minimized mode), allow navigation
          if (is_caret) {
            event.preventDefault();
            this.toggle_section(parent_li);
          }
          // Otherwise, allow normal link navigation
        });

        // Add caret indicator
        if (!header.querySelector(".caret")) {
          const caret = document.createElement("span");
          caret.className = "caret";
          caret.setAttribute("aria-hidden", "true");
          header.appendChild(caret);
        }
      }
    });
  }

  /**
   * Setup keyboard navigation
   */
  setup_keyboard_navigation() {
    this.el.addEventListener("keydown", (event) => {
      // Toggle on Ctrl/Cmd + B
      if ((event.ctrlKey || event.metaKey) && event.key === "b") {
        event.preventDefault();
        this.toggle(!this.is_toggled());
      }
    });
  }

  /**
   * Check if sidebar is toggled (permanently open)
   */
  is_toggled() {
    return window.site.read_cookie(this.config.cookie_key) == "true";
  }

  /**
   * Check if sidebar is currently minimized
   */
  is_minimized() {
    return this.el.classList.contains("minimized");
  }

  /**
   * Toggle sidebar open/closed state
   */
  toggle(toggle=false) {
    window.site.set_cookie(this.config.cookie_key, toggle);

    if (toggle) {
      this.el.classList.add("toggled");
      this.maximize();
    } else {
      this.el.classList.remove("toggled");
      this.minimize();
    }

    // Announce state change for screen readers
    const state = toggle ? "expanded" : "collapsed";
    this.announce_state(state);
  }

  /**
   * Minimize sidebar
   */
  minimize() {
    this.el.classList.add("minimized");
    this.el.setAttribute("aria-expanded", "false");

    // Collapse all sections when minimizing
    this.collapse_all_sections();
  }

  /**
   * Maximize sidebar
   */
  maximize() {
    this.el.classList.remove("minimized");
    this.el.setAttribute("aria-expanded", "true");
  }

  /**
   * Toggle a navigation section open/closed
   */
  toggle_section(section_li) {
    const is_expanded = section_li.classList.contains("expanded");

    if (is_expanded) {
      section_li.classList.remove("expanded");
      section_li.classList.add("collapsed");
    } else {
      section_li.classList.add("expanded");
      section_li.classList.remove("collapsed");
    }

    // Update ARIA attributes
    const link = section_li.querySelector("a");
    if (link) {
      link.setAttribute("aria-expanded", !is_expanded);
    }
  }

  /**
   * Collapse all navigation sections
   */
  collapse_all_sections() {
    const sections = this.el.querySelectorAll(".nav-level-1 > li.expanded");
    sections.forEach(section => {
      section.classList.remove("expanded");
      section.classList.add("collapsed");

      const link = section.querySelector("a");
      if (link) {
        link.setAttribute("aria-expanded", "false");
      }
    });
  }

  /**
   * Handle toggle button click
   */
  on_click(event) {
    this.toggle(!this.is_toggled());
  }

  /**
   * Handle search input focus
   */
  on_search_focus(event) {
    this.el.classList.add("search-active");
  }

  /**
   * Handle search input blur
   */
  on_search_blur(event) {
    setTimeout(() => {
      this.el.classList.remove("search-active");
    }, 200);
  }

  /**
   * Handle search input changes
   */
  on_search_input(event) {
    const query = event.target.value.toLowerCase().trim();
    const items = this.el.querySelectorAll(".navTreeItem");

    if (!query) {
      // Show all items when search is cleared
      items.forEach(item => {
        item.style.display = "";
        item.classList.remove("search-match", "search-no-match",
                              "search-parent-match");
      });
      return;
    }

    // First pass: mark items that directly match the query
    items.forEach(item => {
      const link = item.querySelector("a");
      if (!link) {
        return;
      }

      const text = link.textContent.toLowerCase();
      const matches = text.includes(query);

      if (matches) {
        item.classList.add("search-match");
        item.classList.remove("search-no-match", "search-parent-match");
        item.style.display = "";
      } else {
        item.classList.add("search-no-match");
        item.classList.remove("search-match", "search-parent-match");
        item.style.display = "none";
      }
    });

    // Second pass: show parents of matching items and expand them
    items.forEach(item => {
      if (item.classList.contains("search-match")) {
        // Expand and show all parent sections
        let parent = item.parentElement;
        while (parent && parent !== this.el) {
          if (parent.tagName === "LI") {
            parent.style.display = "";
            parent.classList.add("expanded");
            parent.classList.remove("collapsed");
            // Mark as parent match if not a direct match
            if (!parent.classList.contains("search-match")) {
              parent.classList.remove("search-no-match");
              parent.classList.add("search-parent-match");
            }
          }
          parent = parent.parentElement;
        }
      }
    });
  }

  /**
   * Announce state changes for screen readers
   */
  announce_state(state) {
    const announcement = document.createElement("div");
    announcement.className = "sr-only";
    announcement.setAttribute("role", "status");
    announcement.setAttribute("aria-live", "polite");
    announcement.textContent = `Sidebar ${state}`;
    this.el.appendChild(announcement);

    setTimeout(() => {
      announcement.remove();
    }, 1000);
  }
}

export default Sidebar;
