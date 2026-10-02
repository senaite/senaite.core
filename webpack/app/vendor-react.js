// SENAITE shared React vendor bundle
//
// Exposes a single React/ReactDOM instance on the global scope so that
// senaite.core, its add-ons and standalone views (which do not pull in the
// core resources, e.g. senaite.impress publish views) can all consume the
// same React via Webpack externals instead of bundling their own copy.
//
// React 19 no longer ships a UMD build, so we build this tiny self-executing
// bundle ourselves. It is loaded as a plain <script> (see resources.pt),
// exactly like the vendored jQuery / TinyMCE libraries.
import React from "react";
import * as ReactDOM from "react-dom";
import * as ReactDOMClient from "react-dom/client";

window.React = React;
// Merge react-dom (createPortal, flushSync, ...) with react-dom/client
// (createRoot, hydrateRoot) so consumers of either module resolve here.
window.ReactDOM = Object.assign({}, ReactDOM, ReactDOMClient);
