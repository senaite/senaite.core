/**
 * SENAITE Workflow Menu - React Component bootstrapper
 *
 * Mounts a `WorkflowMenu` component on every `.senaite-workflow-menu`
 * placeholder rendered by the `plone.contentmenu` viewlet. The
 * placeholder carries the current review state via data-* attributes so
 * the menu is visible immediately; the list of allowed transitions is
 * fetched lazily from `@@workflow_menu_data` on first open.
 */

import React from "react";
import {createRoot} from "react-dom/client";
import WorkflowMenu from "./WorkflowMenu";
import "./styles/workflow-menu.scss";


export const initWorkflowMenus = () => {
  const nodes = document.querySelectorAll(".senaite-workflow-menu");
  const roots = [];
  nodes.forEach((node) => {
    const props = {
      uid: node.dataset.uid,
      stateTitle: node.dataset.stateTitle || "",
      stateClass: node.dataset.stateClass || "",
      fetchUrl: node.dataset.fetchUrl,
    };
    // Replace the SSR skeleton so React owns the whole subtree.
    node.replaceChildren();
    const root = createRoot(node);
    root.render(<WorkflowMenu {...props} />);
    roots.push(root);
  });
  return roots;
};

export default WorkflowMenu;
