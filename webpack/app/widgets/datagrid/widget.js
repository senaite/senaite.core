import React from "react";

import { read_model } from "./model.js";

/* SENAITE DataGrid Widget (ReactJS)
 *
 * Replaces the former jQuery `datagrid.js` handler. The controller owns the
 * row-level UX (add/remove/reorder/auto-append, row buttons, order index and
 * the `.count` marker) while the individual cells stay server-rendered by
 * z3c.form and are *adopted* into the React rows. The per-cell React widgets
 * (queryselect/uidreference) mount into those adopted nodes as before, so the
 * request-key submit contract (`form.widgets.<name>.<idx>.widgets.<sub>`) is
 * preserved and `extract()`/the form adapters do not change.
 */

// Registry of live controllers, keyed by their `<tbody>` element. Used by the
// global `window.widgets.datagrid` facade to route DOM-based API calls.
const REGISTRY = [];

// Guard so the one-time `datagrid:loaded` event is only fired once.
let LOADED_FIRED = false;

// Monotonic counter for stable React keys across structural changes.
let ROW_SEQ = 0;


/* Move the children of a captured server node into a React-owned element.
 *
 * The adopted content (plain inputs or queryselect mount `<div>`s) keeps its
 * identity, so mounted per-cell widgets survive. Children are moved once on
 * mount; on reorder React moves the whole `<tr>` (stable key) and the adopted
 * nodes ride along untouched.
 */
class Adopt extends React.Component {

  constructor(props) {
    super(props);
    this.ref = React.createRef();
  }

  componentDidMount() {
    const el = this.ref.current;
    const src = this.props.node;
    if (!el || !src) {
      return;
    }
    while (src.firstChild) {
      el.appendChild(src.firstChild);
    }
  }

  render() {
    const Tag = this.props.as || "td";
    return <Tag className={this.props.className} ref={this.ref} />;
  }
}


/* A single datagrid row: adopted cells + React-rendered manipulator buttons */
const DataGridRow = (props) => {
  const { row, config, flags, callbacks } = props;
  const klass = "datagridwidget-row row-" + props.position +
    (row.is_aa ? " auto-append" : "");

  const button = (action, icon, title, disabled) => (
    <td className={"datagridwidget-manipulator " + action}>
      <button type="button"
              className={"btn btn-sm btn-outline-secondary dgf--row-" + action}
              title={title}
              disabled={disabled}
              onClick={(e) => callbacks[action](e, row)}>
        <i className={"fas fa-" + icon} />
      </button>
    </td>
  );

  const handle = (
    <td className="datagridwidget-manipulator drag-handle">
      <button type="button"
              className="btn btn-sm btn-outline-secondary dgf--row-drag"
              title="Drag to reorder"
              draggable={!row.is_aa}
              disabled={row.is_aa}
              onDragStart={(e) => callbacks.drag_start(e, row)}
              onDragEnd={callbacks.drag_end}>
        <i className="fas fa-grip-vertical" />
      </button>
    </td>
  );

  return (
    <tr className={klass}
        data-index={row.index}
        onDragOver={callbacks.drag_over}
        onDrop={(e) => callbacks.drop(e, row)}
        ref={(el) => callbacks.ref(row, el)}>
      {row.cells.map((cell, i) => (
        <Adopt key={i} className={cell.className} node={cell.node} />
      ))}
      {config.allow_insert && button("add", "plus", "Add row", flags.add)}
      {config.allow_delete &&
        button("delete", "trash", "Delete row", flags.del)}
      {config.allow_reorder && handle}
      {config.allow_reorder &&
        button("moveup", "arrow-up", "Move up", flags.up)}
      {config.allow_reorder &&
        button("movedown", "arrow-down", "Move down", flags.down)}
    </tr>
  );
};


class DataGridWidgetController extends React.Component {

  constructor(props) {
    super(props);

    const model = props.model || read_model(props.root_el);
    this.thead = model.thead;
    this.config = model.config;
    this.template = model.template;

    // Internal source of truth. Each row: {key, index, is_aa, old_index,
    // cells:[{className, node}], dom}
    this.rows = model.rows.map((row) => this.make_row(row.cells, {
      index: row.index,
    }));

    // trailing blank auto-append row
    if (this.config.auto_append) {
      this.rows.push(this.make_template_row(true));
    }

    // assign indices up-front so the first render already carries the correct
    // `data-index` and the adopted names can be reindexed on mount
    this.commit_indices();

    this.tbody = null;
    this.promoting = false;
    this.drag_row = null;

    this.on_add = this.on_add.bind(this);
    this.on_delete = this.on_delete.bind(this);
    this.on_moveup = this.on_moveup.bind(this);
    this.on_movedown = this.on_movedown.bind(this);
    this.on_row_activity = this.on_row_activity.bind(this);
    this.on_drag_start = this.on_drag_start.bind(this);
    this.on_drag_over = this.on_drag_over.bind(this);
    this.on_drop = this.on_drop.bind(this);
    this.on_drag_end = this.on_drag_end.bind(this);
    this.set_row_ref = this.set_row_ref.bind(this);
  }

  /* -- lifecycle ------------------------------------------------------- */

  componentDidMount() {
    REGISTRY.push(this);
    // reindex adopted names/ids (e.g. the trailing AA row: TT -> AA) *before*
    // the per-cell widgets read `data-name`/`data-id` on mount
    this.reindex_pending();
    // adopted cells are now in the document -> mount their per-cell widgets
    this.mount_cell_widgets(this.tbody);
    for (const row of this.rows) {
      row.mounted = true;
    }
    // Native listeners for the auto-append trigger. React synthetic events are
    // unreliable here because the cells are adopted DOM (and queryselect lives
    // in its own React root), so we listen on the real `<tbody>` node instead.
    // `select` is the bubbling custom event fired by queryselect on selection.
    if (this.tbody && this.config.auto_append) {
      for (const type of ["input", "change", "select"]) {
        this.tbody.addEventListener(type, this.on_row_activity, false);
      }
    }
    if (!LOADED_FIRED) {
      LOADED_FIRED = true;
      trigger_custom_event("datagrid:loaded");
    }
  }

  componentWillUnmount() {
    const idx = REGISTRY.indexOf(this);
    if (idx > -1) {
      REGISTRY.splice(idx, 1);
    }
    if (this.tbody && this.config.auto_append) {
      for (const type of ["input", "change", "select"]) {
        this.tbody.removeEventListener(type, this.on_row_activity, false);
      }
    }
  }

  componentDidUpdate() {
    // reindex adopted node names/ids for rows whose position changed, *before*
    // any freshly inserted cell widget mounts and reads its `data-name`
    this.reindex_pending();
    // mount widgets + notify for freshly inserted rows
    for (const row of this.rows) {
      if (!row.mounted && row.dom) {
        row.mounted = true;
        trigger_custom_event("datagrid:row_added", {
          datagrid: this.tbody,
          row: row.dom,
        });
      }
    }
  }

  /* Reindex the adopted DOM of every row whose logical index changed.
   *
   * Plain inputs are reindexed in place. Already-mounted per-cell React widgets
   * (queryselect/uidreference) keep their submit name in state, so `reindex_row`
   * additionally dispatches a `datagrid:cell_reindexed` event they listen for to
   * re-read the new `data-name`/`data-id`.
   */
  reindex_pending() {
    for (const row of this.rows) {
      if (row.old_index != null) {
        this.reindex_row(row, row.index, row.old_index);
        row.old_index = null;
      }
    }
  }

  /* -- row model helpers ----------------------------------------------- */

  make_row(cells, extra) {
    ROW_SEQ += 1;
    return Object.assign({
      key: ROW_SEQ,
      index: null,
      is_aa: false,
      old_index: null,
      dom: null,
      mounted: true,
      cells: cells,
    }, extra || {});
  }

  /* Build a fresh row by cloning the hidden template row cells */
  make_template_row(is_aa) {
    const cells = this.template.cells.map((cell) => ({
      className: cell.className,
      node: cell.node.cloneNode(true),
    }));
    const row = this.make_row(cells, { is_aa: !!is_aa, old_index: "TT" });
    row.mounted = false;
    return row;
  }

  get_visible_rows() {
    // rows excludes the hidden template (TT); AA is included (matches the
    // former `get_visible_rows`)
    return this.rows;
  }

  /* -- index / count bookkeeping --------------------------------------- */

  count_real_rows() {
    return this.rows.filter((row) => !row.is_aa).length;
  }

  /* Assign sequential numeric indices to real rows, "AA" to the append row */
  commit_indices() {
    let cnt = 0;
    for (const row of this.rows) {
      const target = row.is_aa ? "AA" : String(cnt);
      if (!row.is_aa) {
        cnt += 1;
      }
      if (target !== row.index) {
        if (row.old_index == null) {
          row.old_index = row.index;
        }
        row.index = target;
      }
    }
  }

  reindex_row(row, new_index, old_index) {
    const tr = row.dom;
    if (!tr || new_index === old_index) {
      return;
    }
    const name_prefix = this.config.name_prefix + ".";
    const id_prefix = this.config.id_prefix + "-";

    const replace = (el, attr, prefix) => {
      const val = el.getAttribute(attr);
      if (!val) {
        return;
      }
      const pattern = new RegExp("^" + escape_re(prefix + old_index));
      el.setAttribute(attr, val.replace(pattern, prefix + new_index));
    };

    reindex_attr(tr, '[id^="formfield-' + id_prefix + '"]',
      (el) => replace(el, "id", "formfield-" + id_prefix));
    reindex_attr(tr, '[name^="' + name_prefix + '"]',
      (el) => replace(el, "name", name_prefix));
    reindex_attr(tr, '[id^="' + id_prefix + '"]',
      (el) => replace(el, "id", id_prefix));
    reindex_attr(tr, '[for^="' + id_prefix + '"]',
      (el) => replace(el, "for", id_prefix));
    reindex_attr(tr, '[href*="#' + id_prefix + '"]',
      (el) => replace(el, "href", "#" + id_prefix));
    reindex_attr(tr, '[data-fieldname^="' + name_prefix + '"]',
      (el) => replace(el, "data-fieldname", name_prefix));
    // mount `<div>`s of the per-cell React widgets carry the submit name/id in
    // `data-name`/`data-id` - reindex them so freshly mounted cells submit
    // under the correct row index
    reindex_attr(tr, '[data-name^="' + name_prefix + '"]',
      (el) => replace(el, "data-name", name_prefix));
    reindex_attr(tr, '[data-id^="' + id_prefix + '"]',
      (el) => replace(el, "data-id", id_prefix));

    // notify already-mounted per-cell React widgets (which keep their submit
    // name in state) to re-read the reindexed `data-name`/`data-id`
    reindex_attr(tr, "[data-name]", (el) => {
      el.dispatchEvent(new CustomEvent("datagrid:cell_reindexed", {
        bubbles: false,
        detail: { name: el.dataset.name, id: el.dataset.id },
      }));
    });
  }

  /* -- structural operations ------------------------------------------- */

  refresh() {
    this.commit_indices();
    this.forceUpdate();
  }

  insert_row(ref_row, before) {
    const new_row = this.make_template_row(false);
    const at = this.rows.indexOf(ref_row);
    const pos = at < 0 ? this.rows.length : (before ? at : at + 1);
    this.rows.splice(pos, 0, new_row);
    this.refresh();
    return new_row;
  }

  remove_row(row) {
    const at = this.rows.indexOf(row);
    if (at < 0) {
      return;
    }
    this.rows.splice(at, 1);
    const dom = row.dom;
    this.refresh();
    trigger_custom_event("datagrid:row_removed", {
      datagrid: this.tbody,
      row: dom,
    });
  }

  /* Promote the trailing AA row to a real row and append a fresh AA row */
  auto_append_row() {
    for (const row of this.rows) {
      if (row.is_aa) {
        row.is_aa = false;
        if (row.old_index == null) {
          row.old_index = row.index;
        }
      }
    }
    this.rows.push(this.make_template_row(true));
    this.refresh();
  }

  move_row(row, direction) {
    const reals = this.rows.filter((r) => !r.is_aa);
    const at = reals.indexOf(row);
    if (at < 0) {
      return;
    }
    let target = direction === "up" ? at - 1 : at + 1;
    // wrap around, matching the former behaviour
    if (target < 0) {
      target = reals.length - 1;
    } else if (target >= reals.length) {
      target = 0;
    }
    reals.splice(at, 1);
    reals.splice(target, 0, row);
    this.apply_reorder(reals);
  }

  /* Move `row` to the slot occupied by `target` (drag & drop) */
  reorder(row, target) {
    const reals = this.rows.filter((r) => !r.is_aa);
    const from = reals.indexOf(row);
    if (from < 0 || reals.indexOf(target) < 0 || row === target) {
      return;
    }
    reals.splice(from, 1);
    reals.splice(reals.indexOf(target), 0, row);
    this.apply_reorder(reals);
  }

  /* Commit a reordered list of real rows, keeping the trailing AA row last */
  apply_reorder(reals) {
    const aa = this.rows.filter((r) => r.is_aa);
    // mark every real row for reindexing (order changed)
    for (const r of reals) {
      if (r.old_index == null) {
        r.old_index = r.index;
      }
    }
    this.rows = reals.concat(aa);
    this.refresh();
  }

  /* -- event handlers -------------------------------------------------- */

  on_add(e, row) {
    e.preventDefault();
    this.insert_row(row, false);
  }

  on_delete(e, row) {
    e.preventDefault();
    this.remove_row(row);
  }

  on_moveup(e, row) {
    e.preventDefault();
    this.move_row(row, "up");
  }

  on_movedown(e, row) {
    e.preventDefault();
    this.move_row(row, "down");
  }

  /* Promote the trailing auto-append row as soon as the user edits it */
  on_row_activity(e) {
    if (!this.config.auto_append || this.promoting) {
      return;
    }
    const aa = this.rows.find((row) => row.is_aa);
    if (!aa || !aa.dom || !aa.dom.contains(e.target)) {
      return;
    }
    this.promoting = true;
    this.auto_append_row();
    this.promoting = false;
  }

  /* -- drag & drop reorder --------------------------------------------- */

  on_drag_start(e, row) {
    if (row.is_aa) {
      return;
    }
    this.drag_row = row;
    if (e.dataTransfer) {
      e.dataTransfer.effectAllowed = "move";
      try {
        e.dataTransfer.setData("text/plain", String(row.key));
      } catch (err) {
        // some browsers require setData in a try/catch
      }
      if (row.dom) {
        e.dataTransfer.setDragImage(row.dom, 0, 0);
      }
    }
    if (row.dom) {
      row.dom.classList.add("datagridwidget-dragging");
    }
  }

  on_drag_over(e) {
    if (!this.drag_row) {
      return;
    }
    // required so the row becomes a valid drop target
    e.preventDefault();
    if (e.dataTransfer) {
      e.dataTransfer.dropEffect = "move";
    }
  }

  on_drop(e, row) {
    if (!this.drag_row) {
      return;
    }
    e.preventDefault();
    const dragged = this.drag_row;
    this.clear_drag();
    if (row !== dragged && !row.is_aa) {
      this.reorder(dragged, row);
    }
  }

  on_drag_end() {
    this.clear_drag();
  }

  clear_drag() {
    if (this.drag_row && this.drag_row.dom) {
      this.drag_row.dom.classList.remove("datagridwidget-dragging");
    }
    this.drag_row = null;
  }

  set_row_ref(row, el) {
    if (el) {
      row.dom = el;
    }
  }

  /* Mount the per-cell React widgets within the given root element */
  mount_cell_widgets(root) {
    const mount = window.senaite &&
      window.senaite.core &&
      window.senaite.core.render_all_widgets;
    if (mount && root) {
      mount(root);
    }
  }

  /* -- rendering ------------------------------------------------------- */

  button_flags() {
    // port of the former `set_ui_state`: compute per-row disabled flags
    const rows = this.rows;
    const enabled = { add: false, del: false, up: false, down: false };
    return rows.map((row, cnt) => {
      if (row.is_aa) {
        return { add: true, del: true, up: true, down: true, prev_down: true };
      }
      if (cnt === 0) {
        return Object.assign({}, enabled, {
          up: true,
          down: rows.length === 1,
        });
      }
      if (cnt === rows.length - 1) {
        return Object.assign({}, enabled, { down: true });
      }
      return Object.assign({}, enabled);
    });
  }

  render() {
    const flags = this.button_flags();
    const callbacks = {
      add: this.on_add,
      delete: this.on_delete,
      moveup: this.on_moveup,
      movedown: this.on_movedown,
      drag_start: this.on_drag_start,
      drag_over: this.on_drag_over,
      drop: this.on_drop,
      drag_end: this.on_drag_end,
      ref: this.set_row_ref,
    };
    const count_name = this.config.name_prefix + ".count";

    return (
      <div>
        <table className={"table table-hover table-responsive table-sm " +
          "table-borderless datagridwidget-table-view"}>
          <Adopt as="thead" node={this.thead} />
          <tbody className="datagridwidget-body"
                 data-name_prefix={this.config.name_prefix}
                 data-id_prefix={this.config.id_prefix}
                 ref={(el) => { this.tbody = el || this.tbody; }}>
            {this.rows.map((row, i) => (
              <DataGridRow key={row.key}
                           row={row}
                           position={i}
                           config={this.config}
                           flags={flags[i]}
                           callbacks={callbacks} />
            ))}
          </tbody>
        </table>
        <input type="hidden"
               name={count_name}
               value={this.count_real_rows()}
               readOnly />
      </div>
    );
  }
}


/* -- module helpers ---------------------------------------------------- */

const escape_re = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const reindex_attr = (root, selector, fn) => {
  root.querySelectorAll(selector).forEach(fn);
};

const trigger_custom_event = (name, data) => {
  const event = new CustomEvent(name, { detail: data });
  document.body.dispatchEvent(event);
};

/* Locate the controller responsible for the given tbody/row element */
const find_controller = (el) => {
  if (!el) {
    return null;
  }
  const tbody = el.matches && el.matches(".datagridwidget-body")
    ? el
    : (el.closest ? el.closest(".datagridwidget-body") : null);
  return REGISTRY.find((ctrl) => ctrl.tbody === tbody) || null;
};

/* Global facade preserving the former `window.widgets.datagrid` API.
 *
 * Consumers (e.g. the calculation edit form) call these with DOM elements.
 */
window.widgets = window.widgets || {};
if (!window.widgets.datagrid) {
  window.widgets.datagrid = {
    get_visible_rows(table) {
      const ctrl = find_controller(table);
      return ctrl ? ctrl.get_visible_rows().map((row) => row.dom) : [];
    },
    remove_row(row) {
      const ctrl = find_controller(row);
      if (!ctrl) {
        return;
      }
      const model = ctrl.rows.find((r) => r.dom === row);
      if (model) {
        ctrl.remove_row(model);
      }
    },
    auto_append_row(table) {
      const ctrl = find_controller(table);
      if (ctrl) {
        ctrl.auto_append_row();
      }
    },
    trigger_custom_event(name, data) {
      trigger_custom_event(name, data);
    },
  };
}

export default DataGridWidgetController;
