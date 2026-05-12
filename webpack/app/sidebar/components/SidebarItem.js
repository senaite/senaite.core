import React, {useState, useCallback} from "react";

/**
 * Sidebar Item Component
 * Renders a single navigation item with optional children (recursive)
 */
export const SidebarItem = ({
  item,
  level = 1,
  searchQuery = "",
  onShowMore,
}) => {
  const [isExpanded, setIsExpanded] = useState(
    item.is_current || item.is_parent
  );

  const hasChildren = item.children && item.children.length > 0;

  const toggleExpanded = useCallback((event) => {
    const target = event.target;
    const isCaret = target.classList.contains("caret") ||
                    target.closest(".caret");

    if (isCaret) {
      event.preventDefault();
      setIsExpanded(!isExpanded);
    }
  }, [isExpanded]);

  const itemClasses = ["navTreeItem"];
  if (item.is_current) {
    itemClasses.push("active", "navTreeCurrentNode");
  }
  if (item.is_parent) {
    itemClasses.push("navTreeCurrentParent");
  }
  if (hasChildren) {
    itemClasses.push("navTreeFolderish");
    itemClasses.push(isExpanded ? "expanded" : "collapsed");
  }

  const shouldDisplay = !searchQuery ||
    item.title.toLowerCase().includes(searchQuery.toLowerCase());

  if (!shouldDisplay && !hasChildren) {
    return null;
  }

  const portalUrl = window.portal_url || "";

  return (
    <li className={itemClasses.join(" ")}>
      <a
        href={item.url}
        className="navTreeLink"
        data-id={item.id}
        data-portal-type={item.portal_type}
        title={item.description || ""}
        onClick={hasChildren ? toggleExpanded : undefined}
      >
        {item.icon && (
          <span className="node-icon">
            <img
              src={`${portalUrl}/${item.icon}`}
              alt=""
              className="nav-icon"
            />
          </span>
        )}
        <span className={level === 1 ? "node-title" : "child-title"}>
          {item.title}
        </span>
        {hasChildren && <span className="caret" />}
      </a>

      {hasChildren && (
        <ul className={`nav-level-${level + 1}`}>
          {item.children.map((child) => (
            <SidebarItem
              key={child.id}
              item={child}
              level={level + 1}
              searchQuery={searchQuery}
              onShowMore={onShowMore}
            />
          ))}
          {item.has_more && (
            <li className="navTreeItem load-more-item">
              <a
                href="#"
                className="navTreeLink load-more-link"
                data-parent-id={item.id}
                title="Click to load all items in this folder"
                onClick={(event) => {
                  event.preventDefault();
                  if (onShowMore) {
                    onShowMore();
                  }
                }}
              >
                Show more...
              </a>
            </li>
          )}
        </ul>
      )}
    </li>
  );
};
