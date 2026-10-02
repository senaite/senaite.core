/**
 * Workflow Menu
 *
 * Renders the workflow dropdown in the SENAITE content toolbar.
 *
 * The current review state is shown immediately from props (seeded by
 * the server-side `data-*` attributes). The transition list is fetched
 * lazily from `@@workflow_menu_data` the first time the menu opens and
 * cached per-UID for the lifetime of the page.
 */

import React, {useCallback, useEffect, useRef, useState} from "react";


const transitionCache = new Map();


const t = (msg) => {
  if (typeof window !== "undefined" && typeof window._t === "function") {
    return window._t(msg);
  }
  return msg;
};


const WorkflowMenu = (props) => {
  const {uid, stateTitle, stateClass, fetchUrl} = props;
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState(
    transitionCache.has(uid) ? "ready" : "idle");
  const [items, setItems] = useState(
    transitionCache.get(uid) || null);
  const [error, setError] = useState(null);
  const wrapperRef = useRef(null);

  const load = useCallback(() => {
    if (items !== null || status === "loading") {
      return;
    }
    setStatus("loading");
    fetch(fetchUrl, {
      credentials: "same-origin",
      headers: {Accept: "application/json"},
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
      })
      .then((data) => {
        const list = data.transitions || [];
        transitionCache.set(uid, list);
        setItems(list);
        setStatus("ready");
      })
      .catch((err) => {
        setError(err.message || String(err));
        setStatus("error");
      });
  }, [uid, fetchUrl, items, status]);

  const toggle = useCallback((event) => {
    event.preventDefault();
    setOpen((prev) => {
      const next = !prev;
      if (next) {
        load();
      }
      return next;
    });
  }, [load]);

  useEffect(() => {
    if (!open) {
      return undefined;
    }
    const onClickAway = (event) => {
      const node = wrapperRef.current;
      if (node && !node.contains(event.target)) {
        setOpen(false);
      }
    };
    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClickAway);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("mousedown", onClickAway);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return (
    <div ref={wrapperRef} className="d-inline-flex">
      <a href="#"
         className="nav-link dropdown-toggle workflow-menu-toggle"
         role="button"
         aria-haspopup="true"
         aria-expanded={open}
         onClick={toggle}>
        <span className={`${stateClass || ""} tb-state`}>
          {stateTitle}
        </span>
      </a>
      <div className={
          `dropdown-menu workflow-menu-dropdown${open ? " show" : ""}`}>
        {status === "loading" && (
          <span className="dropdown-item-text text-muted">
            <i className="fas fa-spinner fa-spin mr-1"/>
            {t("Loading…")}
          </span>
        )}
        {status === "error" && (
          <span className="dropdown-item-text text-danger">
            {error}
          </span>
        )}
        {status === "ready" && items && items.length === 0 && (
          <span className="dropdown-item-text text-muted">
            {t("No transitions available")}
          </span>
        )}
        {status === "ready" && items && items.map((transition) => (
          <a key={transition.id}
             className="dropdown-item"
             href={transition.url}
             title={transition.description}>
            {transition.title}
          </a>
        ))}
      </div>
    </div>
  );
};


export default WorkflowMenu;
