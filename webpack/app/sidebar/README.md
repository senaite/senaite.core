# SENAITE Sidebar - React Component

Modern sidebar navigation component built with React, featuring smooth animations, search functionality, and responsive design.

## Directory Structure

```
sidebar/
├── README.md                          # This file
├── index.js                           # Entry point and initialization
├── Sidebar.js                         # Main container component
├── components/
│   ├── SidebarHeader.js              # Header with toggle button
│   ├── SidebarSearch.js              # Search input component
│   ├── SidebarNavigation.js          # Navigation list container
│   └── SidebarItem.js                # Individual nav item (recursive)
├── hooks/
│   ├── useSidebarState.js            # Toggle state and keyboard nav
│   ├── useSidebarResize.js           # Resize functionality
│   └── useNavigation.js              # Navigation data fetching
└── styles/
    └── sidebar.scss                   # All styles
```

## Features

- **Toggle State**: Persistent expand/collapse via cookies
- **Keyboard Navigation**: Ctrl/Cmd+B to toggle sidebar
- **Search**: Real-time filtering with parent expansion
- **Resizable**: Drag handle with width persistence (200px-600px)
- **Responsive**: Mobile-friendly with different breakpoints
- **Accessible**: ARIA labels, keyboard navigation, screen reader support
- **Loading States**: Spinners and error messages
- **Dark Mode**: Support for Bootstrap 5.3+ dark theme
- **Load More**: Pagination for folders with many items

## Component Architecture

### Main Components

#### `<Sidebar />`
Main container that orchestrates all functionality.

**State:**
- Toggle state (minimized/maximized)
- Search query
- Navigation data
- Loading/error states
- Resize width

**Props:** None (self-contained)

#### `<SidebarHeader />`
Displays toggle button.

**Props:**
- `isToggled` (boolean): Current toggle state
- `onToggle` (function): Callback when button clicked

#### `<SidebarSearch />`
Search input with event handlers.

**Props:**
- `onSearch` (function): Called on input change
- `onFocus` (function): Called on focus
- `onBlur` (function): Called on blur

#### `<SidebarNavigation />`
Renders navigation tree.

**Props:**
- `navigationData` (array): Navigation items
- `searchQuery` (string): Current search query
- `onShowMore` (function): Load more items callback

#### `<SidebarItem />`
Individual navigation item (recursive for children).

**Props:**
- `item` (object): Navigation item data
- `level` (number): Nesting level (1-5)
- `searchQuery` (string): Filter text
- `onShowMore` (function): Load more callback

### Custom Hooks

#### `useSidebarState(cookieKey)`
Manages toggle state with cookie persistence.

**Returns:**
```javascript
{
  isToggled: boolean,      // Is sidebar toggled open
  isMinimized: boolean,    // Is sidebar minimized
  toggle: (value) => void  // Toggle function
}
```

#### `useSidebarResize(minWidth, maxWidth, cookieKey)`
Manages resize functionality.

**Returns:**
```javascript
{
  width: number,                    // Current width in pixels
  isResizing: boolean,              // Is currently resizing
  startResize: (event) => void      // Start resize handler
}
```

#### `useNavigation()`
Fetches and manages navigation data from backend API.

**Returns:**
```javascript
{
  navigationData: array,        // Navigation items
  isLoading: boolean,           // Is fetching data
  error: string|null,           // Error message if any
  showMoreItems: () => void     // Fetch all items
}
```

## Data Flow

```
Template (sidebar.pt)
    ↓
Empty <div id="sidebar"></div>
    ↓
React renders into container
    ↓
<Sidebar />
    ├── useSidebarState() → Toggle state from cookies
    ├── useSidebarResize() → Width from cookies
    └── useNavigation() → Fetch from @@sidebar-navigation-json
        ↓
<SidebarHeader /> + <SidebarSearch /> + <SidebarNavigation />
    ↓
<SidebarItem /> (recursive for tree structure)
```

## Backend API

The component fetches data from:
```
/@@sidebar-navigation-json?current_url={url}&show_more={boolean}
```

**Response Format:**
```json
{
  "success": true,
  "data": [
    {
      "id": "clients",
      "title": "Clients",
      "description": "",
      "url": "/clients",
      "icon": "senaite_theme/icon/clientfolder",
      "portal_type": "ClientFolder",
      "review_state": "active",
      "is_current": false,
      "is_parent": false,
      "is_folderish": true,
      "depth": 1,
      "has_more": true,
      "total_count": 150,
      "children": [...]
    }
  ]
}
```

## Styling

All styles are in `styles/sidebar.scss` using SCSS variables:

```scss
$sidebar-bg: #ffffff;
$sidebar-border: #e5e7eb;
$link-color: #374151;
$primary: #d97706;
```

### CSS Classes

- `.minimized` - Sidebar collapsed to 50px width
- `.toggled` - Sidebar permanently expanded
- `.loading` - Loading state
- `.search-active` - Search field focused
- `.navTreeItem` - Navigation item
- `.navTreeCurrentNode` - Active item
- `.navTreeCurrentParent` - Parent of active item
- `.expanded` / `.collapsed` - Section state

## Usage

The sidebar is automatically initialized in `senaite.core.js`:

```javascript
import {initSidebar} from "./sidebar"

document.addEventListener("DOMContentLoaded", () => {
  // ... other initialization ...

  // Initialize and expose sidebar API
  window.senaite.core.sidebar = initSidebar();

  // BBB: Legacy reference
  window.sidebar = window.senaite.core.sidebar;
});
```

### Sidebar API

The sidebar is accessible globally via `window.senaite.core.sidebar` (or `window.sidebar` for backwards compatibility):

```javascript
// Check if sidebar is toggled (expanded)
window.senaite.core.sidebar.isToggled()  // returns boolean

// Check if sidebar is minimized
window.senaite.core.sidebar.isMinimized()  // returns boolean

// Toggle sidebar programmatically
window.senaite.core.sidebar.toggle()  // toggle current state
window.senaite.core.sidebar.toggle(true)  // force expand
window.senaite.core.sidebar.toggle(false)  // force minimize

// Minimize sidebar
window.senaite.core.sidebar.minimize()

// Maximize sidebar
window.senaite.core.sidebar.maximize()

// Get sidebar DOM element
window.senaite.core.sidebar.getElement()  // returns HTMLElement
```

**Example Usage:**
```javascript
// Programmatically expand the sidebar
window.senaite.core.sidebar.maximize();

// Check current state
if (window.senaite.core.sidebar.isMinimized()) {
  console.log("Sidebar is minimized");
}
```

## Migration from Vanilla JS

The React component maintains the same functionality as the previous vanilla JavaScript implementation:

**Preserved:**
- Cookie-based state persistence
- Keyboard shortcuts (Ctrl/Cmd+B)
- Search filtering
- Resize functionality
- Load more pagination
- All CSS classes and styling

**Improved:**
- Declarative React code (easier to maintain)
- Better state management with hooks
- Cleaner separation of concerns
- Easier to test and extend
- Better performance with React's virtual DOM

## Extending

### Adding New Features

1. **Add a new hook** in `hooks/` for new state logic
2. **Add a new component** in `components/` for new UI elements
3. **Import and use** in `Sidebar.js`

Example - Adding a favorites feature:

```javascript
// hooks/useFavorites.js
export const useFavorites = () => {
  const [favorites, setFavorites] = useState([]);
  // ... logic ...
  return {favorites, addFavorite, removeFavorite};
};

// Sidebar.js
import {useFavorites} from "./hooks/useFavorites";

export const Sidebar = () => {
  const {favorites, addFavorite} = useFavorites();
  // ... use in render ...
};
```

### Styling Changes

All styles are in `styles/sidebar.scss`. Modify SCSS variables at the top for theme changes:

```scss
$primary: #your-color;  // Changes accent color throughout
```

## Browser Support

- Modern browsers (ES6+)
- React 16.8+ (hooks support)
- IE11 not supported (use Babel polyfills if needed)

## Performance

- Uses React hooks for efficient re-renders
- Cookie caching prevents unnecessary state resets
- Recursive components only render visible items
- Search filtering happens client-side (instant)
- Navigation data fetched once on mount

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation (Ctrl/Cmd+B)
- Screen reader announcements for state changes
- Focus management
- Semantic HTML (`<nav>`, `<ul>`, `<li>`)

## Future Enhancements

Possible improvements:
- React.memo() for performance optimization
- Virtual scrolling for very large trees
- Drag-and-drop reordering
- Context menu on right-click
- Favorites/bookmarks
- Collapsible groups persistence
- Animation transitions with react-spring
