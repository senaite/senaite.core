# SENAITE Sidebar - JSON API Integration

Complete documentation for the modernized SENAITE sidebar with dynamic JSON API loading.

## Overview

The SENAITE sidebar has been completely redesigned with:

1. **JSON API Integration** - Navigation loads dynamically via AJAX
2. **Modern Claude.ai-inspired Design** - Clean, minimal interface
3. **Advanced Features** - Search, collapsible sections, keyboard shortcuts
4. **Better Performance** - Faster initial page loads with async loading
5. **Improved Accessibility** - Full ARIA support and screen reader compatibility

## Architecture

### Client-Server Communication

```
Browser                     Server
--------                    --------
  |                            |
  |-- GET @@sidebar-navigation-json -->|
  |                            |
  |                     [Process Request]
  |                            |
  |                     [Get Navigation Tree]
  |                            |
  |                     [Convert to JSON]
  |                            |
  |<-- JSON Response ----------|
  |                            |
[Render Navigation]            |
  |                            |
```

### JSON API Endpoint

**URL**: `@@sidebar-navigation-json`

**Method**: GET

**Response Format**:
```json
{
  "success": true,
  "data": [
    {
      "id": "clients",
      "title": "Clients",
      "description": "Manage clients",
      "url": "/clients",
      "icon": "fa-users",
      "review_state": "published",
      "is_current": false,
      "is_parent": false,
      "is_folderish": true,
      "portal_type": "ClientFolder",
      "depth": 0,
      "children": [
        {
          "id": "client-1",
          "title": "Happy Hills",
          "description": "",
          "url": "/clients/client-1",
          "icon": "",
          "review_state": "published",
          "is_current": true,
          "is_parent": false,
          "is_folderish": true,
          "portal_type": "Client",
          "depth": 1,
          "children": []
        }
      ]
    }
  ],
  "count": 1
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Error message here",
  "data": []
}
```

## Implementation Details

### Python Backend (sidebar.py)

#### New Methods in `SidebarViewletManager`:

**`get_navigation_tree()`**
```python
def get_navigation_tree(self):
    """Get the navigation tree as a structured dict

    Returns a hierarchical structure of navigation items that can be
    easily converted to JSON for the sidebar JavaScript.
    """
```

**`_process_navigation_tree(tree_data)`**
```python
def _process_navigation_tree(self, tree_data):
    """Process navigation tree into a JSON-friendly structure

    :param tree_data: Dict with navigation tree data from portlet
    :returns: List of navigation items with children
    """
```

**`_process_navigation_item(node)`**
```python
def _process_navigation_item(self, node):
    """Process a single navigation item

    :param node: Navigation node dict
    :returns: Processed navigation item dict
    """
```

#### New Class: `SidebarNavigationAPI`

```python
class SidebarNavigationAPI(BrowserView):
    """JSON API endpoint for sidebar navigation

    Provides the navigation structure as JSON for dynamic sidebar loading.
    Access via: @@sidebar-navigation-json
    """

    def __call__(self):
        """Return navigation tree as JSON"""
```

**Registered in configure.zcml**:
```xml
<browser:page
    name="sidebar-navigation-json"
    for="*"
    class=".sidebar.SidebarNavigationAPI"
    permission="zope2.View"
    layer="senaite.core.interfaces.ISenaiteCore"
    />
```

### JavaScript Frontend (sidebar.js)

#### New Properties:

```javascript
// Track navigation data
this.navigation_data = null;
this.navigation_container = null;
```

#### New Methods:

**`fetch_navigation()`**
```javascript
async fetch_navigation() {
    // Fetches navigation data from JSON API
    // Handles loading states and errors
    // Calls render_navigation() on success
}
```

**`render_navigation()`**
```javascript
render_navigation() {
    // Creates navigation container
    // Renders navigation tree from data
    // Re-initializes collapsible sections
}
```

**`render_navigation_list(items, level)`**
```javascript
render_navigation_list(items, level) {
    // Recursively renders navigation lists
    // Creates <ul> with proper nav-level-{n} class
}
```

**`render_navigation_item(item, level)`**
```javascript
render_navigation_item(item, level) {
    // Renders individual navigation items
    // Creates <li> with proper classes and attributes
    // Handles icons, titles, children
    // Skips inactive items
}
```

**`show_error(message)`**
```javascript
show_error(message) {
    // Displays error message in sidebar
    // Used when API request fails
}
```

### Template (sidebar.pt)

Updated to include:

1. **Loading Placeholder**:
```html
<div class="sidebar-loading">
  <div class="spinner"></div>
  <span i18n:translate="">Loading navigation...</span>
</div>
```

2. **Navigation Container**:
```html
<div class="sidebar-navigation">
  <!-- Populated by JavaScript -->
</div>
```

3. **Search Input**:
```html
<div id="sidebar-search-container">
  <input type="search"
         id="sidebar-search"
         class="form-control"
         placeholder="Search navigation..."
         aria-label="Search navigation" />
</div>
```

### SCSS Styles (sidebar.scss)

#### Loading State:

```scss
.sidebar-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid #f3f4f6;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
```

#### Error State:

```scss
.sidebar-error {
  padding: 16px;
  margin: 16px;
  background-color: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 14px;
  text-align: center;
}
```

## Benefits

### Performance

1. **Faster Initial Page Load**
   - Navigation loads asynchronously
   - Page renders immediately
   - No blocking on navigation generation

2. **Reduced Server Load**
   - Navigation only generated when requested
   - Can be cached on client side
   - Reduces HTML payload size

3. **Better Caching**
   - JSON responses can be cached
   - Browser can cache API responses
   - Reduced bandwidth usage

### User Experience

1. **Visual Feedback**
   - Loading spinner shows progress
   - Smooth transition when loading completes
   - Error messages if loading fails

2. **Dynamic Updates**
   - Navigation can be refreshed without page reload
   - Easy to implement live updates
   - Better for single-page app patterns

3. **Progressive Enhancement**
   - Works with JavaScript disabled (fallback needed)
   - Graceful degradation
   - Accessible to all users

### Developer Experience

1. **Separation of Concerns**
   - Backend focuses on data
   - Frontend handles presentation
   - Easier to test and maintain

2. **API-First Design**
   - Reusable API endpoint
   - Can be used by other components
   - Mobile app integration possible

3. **Flexibility**
   - Easy to add filtering/sorting
   - Can implement search server-side
   - Supports pagination if needed

## Usage Examples

### Basic Usage

The sidebar automatically loads on page load:

```javascript
// Sidebar initialization happens automatically
// No manual setup required
```

### Refresh Navigation

To refresh the navigation programmatically:

```javascript
// Get sidebar instance
const sidebar = window.sidebar; // or however you access it

// Refresh navigation
sidebar.fetch_navigation();
```

### Custom API Endpoint

To use a different API endpoint:

```javascript
const sidebar = new Sidebar({
  el: "sidebar",
  api_endpoint: "/custom-navigation-json"
});
```

### Handle API Errors

Listen for errors:

```javascript
sidebar.el.addEventListener("sidebar:error", (event) => {
  console.error("Sidebar error:", event.detail.error);
  // Show custom error message
});
```

## Testing

### Test API Endpoint

```bash
# Test the JSON API directly
curl -X GET "http://localhost:8080/plone/@@sidebar-navigation-json" \
  -H "Accept: application/json" \
  -b cookies.txt

# Expected output:
# {"success": true, "data": [...], "count": N}
```

### Test JavaScript Loading

1. Open browser console
2. Watch for fetch requests to `@@sidebar-navigation-json`
3. Verify navigation renders correctly
4. Check for errors in console

### Test Error Handling

1. **Simulate Network Error**:
   ```javascript
   // In browser console
   window.sidebar.fetch_navigation = () => {
     throw new Error("Simulated error");
   };
   window.sidebar.fetch_navigation();
   ```

2. **Test API Failure**:
   - Temporarily break the API endpoint
   - Refresh page
   - Verify error message displays

## Troubleshooting

### Navigation Not Loading

**Symptoms**: Spinner shows indefinitely, no navigation appears

**Possible Causes**:
1. API endpoint not registered
2. Permission issues
3. Network error
4. JavaScript error

**Solutions**:
1. Check browser console for errors
2. Verify API endpoint is accessible: `/@@sidebar-navigation-json`
3. Check Zope logs for server-side errors
4. Verify user has permission to view navigation

### JSON Parse Error

**Symptoms**: Error in console: "Unexpected token..."

**Cause**: API returning HTML instead of JSON

**Solution**:
1. Check API response content-type
2. Verify no error pages are being returned
3. Check for authentication redirects

### Empty Navigation

**Symptoms**: Navigation loads but shows no items

**Possible Causes**:
1. User has no permission to view any navigation items
2. Navigation portlet not configured
3. Navigation tree is empty

**Solutions**:
1. Check user permissions
2. Verify navigation portlet configuration
3. Check API response: should have `data` array

## Migration Guide

### From Server-Side Rendered Navigation

**Before**:
```html
<div tal:replace="structure navigation"/>
```

**After**:
```html
<div class="sidebar-navigation">
  <!-- Populated by JavaScript -->
</div>
```

### Required Changes

1. **Update Template** - Remove server-side navigation rendering
2. **Rebuild Assets** - Run `npm run build` to compile new JavaScript
3. **Restart Zope** - Restart to load new Python code
4. **Clear Cache** - Clear browser and server caches

## Future Enhancements

### Planned Features

1. **Real-time Updates**
   - WebSocket integration for live navigation updates
   - Notification badges for new content
   - Collaborative editing indicators

2. **Advanced Caching**
   - localStorage caching with TTL
   - Service worker for offline support
   - Smart cache invalidation

3. **Personalization**
   - User-specific navigation order
   - Pinned/favorite items
   - Recently accessed items section

4. **Analytics**
   - Track most-used navigation items
   - User behavior analytics
   - Performance monitoring

5. **Advanced Search**
   - Server-side search integration
   - Search suggestions/autocomplete
   - Search history

## Performance Metrics

### Expected Performance

- **Initial Load**: < 200ms (API request)
- **Render Time**: < 50ms (DOM manipulation)
- **Total Time to Interactive**: < 250ms

### Monitoring

Add performance tracking:

```javascript
// In fetch_navigation()
const start = performance.now();
// ... fetch and render ...
const end = performance.now();
console.log(`Navigation loaded in ${end - start}ms`);
```

## Security Considerations

1. **Permission Checks**
   - API respects Plone permissions
   - Only returns items user can access
   - No sensitive data in JSON

2. **CSRF Protection**
   - GET requests (no CSRF needed)
   - Can add CSRF token for POST if needed

3. **Data Sanitization**
   - All output is properly escaped
   - XSS protection in place
   - Safe JSON serialization

## Support

For issues or questions:
- **GitHub**: [senaite/senaite.core](https://github.com/senaite/senaite.core)
- **Community**: [community.senaite.org](https://community.senaite.org)
- **Documentation**: [senaite.com](https://www.senaite.com)
