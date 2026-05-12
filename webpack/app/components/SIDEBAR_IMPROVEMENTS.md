# SENAITE Sidebar Improvements

Modern sidebar redesign inspired by Claude.ai's clean and intuitive interface.

## Overview

The SENAITE sidebar has been completely redesigned with modern UI/UX principles, featuring:

- **Clean, minimal design** with improved visual hierarchy
- **Smooth animations** using cubic-bezier easing functions
- **Search functionality** to quickly find navigation items
- **Collapsible sections** for better organization
- **Keyboard navigation** support (Ctrl/Cmd + B to toggle)
- **Improved accessibility** with ARIA attributes and screen reader support
- **Responsive design** that works on mobile devices
- **Dark mode support** (optional, based on system preferences)
- **Better hover states** with subtle animations and visual feedback

## New Features

### 1. Search Functionality

A search bar at the top of the sidebar allows users to quickly filter navigation items:

- **Auto-expand on focus** - Sidebar automatically expands when search is focused
- **Real-time filtering** - Navigation items are filtered as you type
- **Parent section expansion** - Parent sections automatically expand to show matching children
- **Visual highlighting** - Matching items are highlighted with a yellow background

**Keyboard shortcut**: Click the search field or tab to it

### 2. Collapsible Sections

Navigation sections with children can be collapsed/expanded:

- **Visual indicators** - Caret icons show expand/collapse state
- **Click to toggle** - Click the caret or section header to toggle
- **Auto-collapse on minimize** - Sections automatically collapse when sidebar is minimized
- **Smooth animations** - Sections expand/collapse with smooth transitions

### 3. Keyboard Navigation

Full keyboard support for improved accessibility:

- **Ctrl/Cmd + B** - Toggle sidebar open/closed
- **Tab navigation** - Navigate through links and search with Tab
- **Enter** - Activate links
- **Escape** - Clear search (when search is focused)

### 4. Improved Hover States

Enhanced visual feedback for better user experience:

- **Background color change** - Subtle gray background on hover
- **Slight translation** - Items shift 2px to the right on hover
- **Icon scaling** - Icons slightly scale up (1.1x) on hover
- **Smooth transitions** - All hover effects use smooth cubic-bezier easing

### 5. Better Accessibility

Comprehensive accessibility improvements:

- **ARIA attributes** - Proper roles, labels, and states
- **Screen reader announcements** - State changes are announced
- **Focus visible** - Clear focus indicators for keyboard navigation
- **Semantic HTML** - Proper use of `<nav>`, `<button>`, etc.
- **sr-only** class for screen reader-only content

## Technical Changes

### JavaScript (sidebar.js)

**New Methods**:
- `setup_search()` - Initialize search functionality
- `setup_collapsible_sections()` - Setup expandable/collapsible sections
- `setup_keyboard_navigation()` - Add keyboard shortcuts
- `on_search_input()` - Handle search filtering
- `toggle_section()` - Toggle section expand/collapse
- `collapse_all_sections()` - Collapse all sections
- `announce_state()` - Announce state changes to screen readers

**Enhanced Features**:
- Faster hover timeout (300ms instead of 1000ms)
- Better interaction tracking with `is_interacting` flag
- Improved event handling with bound methods

### SCSS (sidebar.scss)

**New Styles**:
- Modern color scheme using Tailwind-inspired grays and blues
- Smooth animations with cubic-bezier easing
- Rounded corners (8px border-radius) on all interactive elements
- Subtle shadows for depth
- Custom scrollbar styling
- Dark mode support
- Responsive breakpoints

**Key Design Tokens**:
```scss
// Colors
- Background: #ffffff (white)
- Border: #e5e7eb (gray-200)
- Text: #374151 (gray-700)
- Hover background: #f3f4f6 (gray-100)
- Active background: #eff6ff (blue-50)
- Active text: #2563eb (blue-600)

// Spacing
- Padding: 10-16px
- Margin: 2-8px
- Border radius: 6-8px

// Transitions
- Duration: 200-300ms
- Easing: cubic-bezier(0.4, 0.0, 0.2, 1)
```

### Template (sidebar.pt)

**New Elements**:
```html
<!-- Search container -->
<div id="sidebar-search-container">
  <input type="search"
         id="sidebar-search"
         class="form-control"
         placeholder="Search navigation..."
         aria-label="Search navigation" />
</div>
```

**Improved Structure**:
- Added `role="navigation"` for accessibility
- Added `aria-label="Main navigation"`
- Added `aria-expanded` attribute that updates dynamically

## Usage

### Basic Usage

The sidebar works automatically once the JavaScript is loaded:

```javascript
// Sidebar is initialized automatically on page load
// Configuration is done via the Sidebar class constructor
```

### Custom Configuration

You can customize the sidebar behavior:

```javascript
const sidebar = new Sidebar({
  el: "sidebar",                    // Sidebar element ID
  toggle_el: "sidebar-header",      // Toggle button container ID
  search_el: "sidebar-search",      // Search input ID
  cookie_key: "sidebar-toggle",     // Cookie name for state persistence
  timeout: 300,                     // Hover delay in milliseconds
  animation_duration: 300           // Animation duration
});
```

### CSS Customization

Override the design tokens in your base SCSS:

```scss
// In base.scss
$sidebar-minimized-width: 50px;
$sidebar-maximized-width: 240px;  // Increase width if needed

// Or override specific styles
#sidebar {
  background-color: your-custom-color;
}
```

## Browser Support

The sidebar is compatible with:

- **Modern browsers**: Chrome, Firefox, Safari, Edge (latest versions)
- **Mobile browsers**: iOS Safari, Chrome Mobile
- **Accessibility tools**: NVDA, JAWS, VoiceOver

**CSS Features Used**:
- Flexbox
- CSS Custom Properties (--variables)
- CSS Transitions & Animations
- CSS Grid (for layout)
- Media Queries
- Pseudo-elements

**JavaScript Features Used**:
- ES6 Classes
- Arrow functions
- Template literals
- `querySelector` / `querySelectorAll`
- Event listeners
- Cookies (via window.site)

## Migration from Old Sidebar

The new sidebar is **backward compatible** with existing SENAITE installations:

1. **No breaking changes** - All existing functionality is preserved
2. **Progressive enhancement** - New features work alongside old code
3. **Same class names** - `minimized`, `toggled`, `active` classes remain
4. **Same event handlers** - Hover and click events work as before

### What's New

- Search bar (automatically added)
- Collapsible sections (automatically enabled)
- Keyboard shortcuts (automatically enabled)
- Improved styling (automatically applied)

### What Stays the Same

- Cookie-based state persistence
- Auto-expand on hover
- Toggle button functionality
- Navigation structure

## Troubleshooting

### Search not working

**Problem**: Search input doesn't filter navigation items
**Solution**: Ensure navigation items have class `navTreeItem` on `<li>` elements

### Sections not collapsing

**Problem**: Clicking section headers doesn't collapse/expand
**Solution**: Ensure sections have `ul.nav-level-1 > li > a` structure

### Sidebar not expanding on hover

**Problem**: Hovering doesn't expand the sidebar
**Solution**: Check that `window.site.read_cookie()` is available

### Styles not applying

**Problem**: New styles don't appear
**Solution**:
1. Rebuild webpack: `npm run build`
2. Clear browser cache
3. Check that sidebar.scss is imported in senaite.core.scss

## Development

### Building Assets

```bash
# Development build with watch
npm run watch

# Production build
npm run build

# Build specific component
npm run build:js
npm run build:css
```

### Testing

```bash
# Run tests
npm test

# Run linter
npm run lint

# Check accessibility
npm run a11y
```

### File Structure

```
webpack/app/
├── components/
│   ├── sidebar.js              # Main JavaScript controller
│   └── SIDEBAR_IMPROVEMENTS.md # This file
├── scss/
│   ├── sidebar.scss            # Sidebar-specific styles
│   ├── base.scss               # Design tokens & variables
│   └── senaite.core.scss       # Main SCSS entry point
└── ...

src/senaite/core/browser/viewlets/
├── sidebar.py                  # Python viewlet
└── templates/
    └── sidebar.pt              # HTML template
```

## Future Enhancements

Potential improvements for future versions:

1. **Recent items section** - Show recently accessed pages
2. **Favorites/Pinning** - Allow users to pin frequently used items
3. **Drag-and-drop reordering** - Customize navigation order
4. **Themes** - Light/dark/custom color schemes
5. **Keyboard shortcuts list** - Help dialog showing available shortcuts
6. **Analytics integration** - Track most-used navigation items
7. **Breadcrumb trail** - Show current location in navigation hierarchy
8. **Quick actions** - Add frequently used actions to sidebar
9. **Notifications badge** - Show unread counts on navigation items
10. **Multi-language support** - Better i18n for search and labels

## Credits

Inspired by the clean and intuitive design of:
- [Claude.ai](https://claude.ai) - Modern AI chat interface
- [Linear](https://linear.app) - Project management tool
- [Notion](https://notion.so) - Documentation platform

## License

This code is part of SENAITE.CORE and is licensed under the GNU General Public License version 2 (GPLv2).

## Support

For issues or questions:
- GitHub Issues: [senaite/senaite.core](https://github.com/senaite/senaite.core)
- Community Forum: [community.senaite.org](https://community.senaite.org)
- Documentation: [senaite.com](https://www.senaite.com)
