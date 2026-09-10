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

// -- constants ---------------------------------------------------------

// Row index sentinels used in the `form.widgets.<name>.<idx>...` submit keys.
const IDX_AUTO_APPEND = "AA";  // trailing blank "type to add" row (not counted)
const IDX_TEMPLATE = "TT";     // hidden template row, cloned to build new rows

// Custom events dispatched on `document.body`, kept for backwards compatibility
// with the former jQuery handler and the form adapters that listen for them.
const EVENT_LOADED = "datagrid:loaded";
const EVENT_ROW_ADDED = "datagrid:row_added";
const EVENT_ROW_REMOVED = "datagrid:row_removed";

// Dispatched on a cell mount node after its row was reindexed, so that an
// already-mounted queryselect/uidreference re-reads its submit name/id.
const EVENT_CELL_REINDEXED = "datagrid:cell_reindexed";

// `<tbody>` events that signal the user started editing the auto-append row.
// Bound as *native* listeners because the cells are adopted DOM living in a
// separate React root, where React's synthetic events are unreliable.
const ACTIVITY_EVENTS = ["input", "change", "select"];

const BODY_SELECTOR = ".datagridwidget-body";

// Registry of live controllers. The global `window.widgets.datagrid` facade
// uses it to route DOM-based API calls to the owning controller.
const REGISTRY = [];

// Fire the one-time `datagrid:loaded` event only once across all grids.
let LOADED_FIRED = false;

// Source for stable, unique React row keys that survive structural changes.
let ROW_SEQ = 0;


// -- helper components -------------------------------------------------

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

  return (
    <tr className={klass}
        data-index={row.index}
        ref={(el) => callbacks.ref(row, el)}>
      {row.cells.map((cell, i) => (
        <Adopt key={i} className={cell.className} node={cell.node} />
      ))}
      {config.allow_insert && button("add", "plus", "Add row", flags.add)}
      {config.allow_delete &&
        button("delete", "trash", "Delete row", flags.del)}
      {config.allow_reorder &&
        button("moveup", "arrow-up", "Move up", flags.up)}
      {config.allow_reorder &&
        button("movedown", "arrow-down", "Move down", flags.down)}
    </tr>
  );
};


// -- controller --------------------------------------------------------

/* A row in `this.rows` (the controller's source of truth):
 *
 *   key        stable unique id, used as the React key (survives reorder)
 *   index      current logical index: "0".."n" for real rows, "AA" for the
 *              trailing auto-append row
 *   old_index  the index the adopted DOM still carries while a reindex is
 *              pending; null once the DOM has been reindexed to `index`
 *   is_aa      true for the trailing auto-append row (never submitted)
 *   mounted    true once the row's per-cell widgets have been mounted
 *   dom        the rendered `<tr>` element (set via ref)
 *   cells      [{className, node}] adopted server `<td>` children
 */
class DataGridWidgetController extends React.Component {

  constructor(props) {
    super(props);

    const model = props.model || read_model(props.root_el);
    this.thead = model.thead;
    this.config = model.config;
    this.template = model.template;

    this.rows = model.rows.map(
      (row) => this.make_row(row.cells, { index: row.index }));

    // trailing blank auto-append row
    if (this.config.auto_append) {
      this.rows.push(this.make_template_row(true));
    }

    // assign indices up-front so the first render already carries the correct
    // `data-index` and the adopted names can be reindexed on mount
    this.commit_indices();

    this.tbody = null;
    this.promoting = false;

    this.on_add = this.on_add.bind(this);
    this.on_delete = this.on_delete.bind(this);
    this.on_moveup = this.on_moveup.bind(this);
    this.on_movedown = this.on_movedown.bind(this);
    this.on_row_activity = this.on_row_activity.bind(this);
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
    this.rows.forEach((row) => { row.mounted = true; });
    this.bind_activity_listeners(true);
    if (!LOADED_FIRED) {
      LOADED_FIRED = true;
      trigger_custom_event(EVENT_LOADED);
    }
  }

  componentWillUnmount() {
    const idx = REGISTRY.indexOf(this);
    if (idx > -1) {
      REGISTRY.splice(idx, 1);
    }
    this.bind_activity_listeners(false);
  }

  componentDidUpdate() {
    // reindex adopted node names/ids for rows whose position changed, *before*
    // any freshly inserted cell widget mounts and reads its `data-name`
    this.reindex_pending();
    // mount widgets + notify for freshly inserted rows
    for (const row of this.rows) {
      if (!row.mounted && row.dom) {
        row.mounted = true;
        trigger_custom_event(EVENT_ROW_ADDED, {
          datagrid: this.tbody,
          row: row.dom,
        });
      }
    }
  }

  /* Add/remove the native auto-append listeners on the `<tbody>` */
  bind_activity_listeners(bind) {
    if (!this.tbody || !this.config.auto_append) {
      return;
    }
    const method = bind ? "addEventListener" : "removeEventListener";
    for (const type of ACTIVITY_EVENTS) {
      this.tbody[method](type, this.on_row_activity, false);
    }
  }

  /* -- row model helpers ----------------------------------------------- */

  make_row(cells, extra = {}) {
    ROW_SEQ += 1;
    return {
      key: ROW_SEQ,
      index: null,
      is_aa: false,
      old_index: null,
      dom: null,
      mounted: true,
      cells: cells,
      ...extra,
    };
  }

  /* Build a fresh row by cloning the hidden template row cells */
  make_template_row(is_aa) {
    const cells = this.template.cells.map((cell) => ({
      className: cell.className,
      node: cell.node.cloneNode(true),
    }));
    // cloned cells still carry the template index (TT) and are not yet mounted
    return this.make_row(cells, {
      is_aa: !!is_aa,
      old_index: IDX_TEMPLATE,
      mounted: false,
    });
  }

  /* All rows the facade treats as "visible" - excludes the hidden template
   * (TT) but includes the auto-append row (AA), matching the former handler. */
  get_visible_rows() {
    return this.rows;
  }

  count_real_rows() {
    return this.rows.filter((row) => !row.is_aa).length;
  }

  /* -- index / reindex bookkeeping ------------------------------------- */

  /* Assign sequential numeric indices to real rows, "AA" to the append row.
   *
   * When a row's index changes, its current index is remembered in `old_index`
   * so the next `reindex_pending()` can rewrite the adopted DOM from the old to
   * the new index. `old_index` is only set if not already pending. */
  commit_indices() {
    let cnt = 0;
    for (const row of this.rows) {
      const target = row.is_aa ? IDX_AUTO_APPEND : String(cnt);
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

  /* Reindex the adopted DOM of every row with a pending index change */
  reindex_pending() {
    for (const row of this.rows) {
      if (row.old_index != null) {
        this.reindex_row(row, row.index, row.old_index);
        row.old_index = null;
      }
    }
  }

  /* Rewrite the row index embedded in the adopted DOM of a single row.
   *
   * Plain inputs are rewritten in place. queryselect/uidreference cells keep
   * their submit name in React state, so their (JSON-encoded) `data-name`/
   * `data-id` are rewritten *and* a `datagrid:cell_reindexed` event is fired
   * for the mounted widget to re-read them. */
  reindex_row(row, new_index, old_index) {
    const tr = row.dom;
    if (!tr || new_index === old_index) {
      return;
    }
    const name_prefix = this.config.name_prefix + ".";
    const id_prefix = this.config.id_prefix + "-";

    reindex_attr(tr, "name", name_prefix, old_index, new_index);
    reindex_attr(tr, "data-fieldname", name_prefix, old_index, new_index);
    reindex_attr(tr, "id", "formfield-" + id_prefix, old_index, new_index);
    reindex_attr(tr, "id", id_prefix, old_index, new_index);
    reindex_attr(tr, "for", id_prefix, old_index, new_index);
    reindex_attr(tr, "href", "#" + id_prefix, old_index, new_index);

    // JSON-encoded name/id on the per-cell React widget mount nodes
    reindex_attr(tr, "data-name", name_prefix, old_index, new_index, true);
    reindex_attr(tr, "data-id", id_prefix, old_index, new_index, true);
  }

  /* -- structural operations ------------------------------------------- */

  /* Recompute indices and re-render */
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
    const dom = row.dom;
    this.rows.splice(at, 1);
    this.refresh();
    trigger_custom_event(EVENT_ROW_REMOVED, { datagrid: this.tbody, row: dom });
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

  /* Move a real row up/down by one, wrapping around at the ends */
  move_row(row, direction) {
    const reals = this.rows.filter((r) => !r.is_aa);
    const at = reals.indexOf(row);
    if (at < 0) {
      return;
    }
    let target = direction === "up" ? at - 1 : at + 1;
    if (target < 0) {
      target = reals.length - 1;
    } else if (target >= reals.length) {
      target = 0;
    }
    reals.splice(at, 1);
    reals.splice(target, 0, row);
    this.apply_reorder(reals);
  }

  /* Commit a reordered list of real rows, keeping the trailing AA row last */
  apply_reorder(reals) {
    const aa = this.rows.filter((r) => r.is_aa);
    // the order changed -> mark every real row for reindexing
    for (const row of reals) {
      if (row.old_index == null) {
        row.old_index = row.index;
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

  /* Promote the trailing auto-append row as soon as the user edits it.
   *
   * Only genuine user edits promote the row. Programmatic value changes - e.g.
   * a form adapter pre-filling the auto-append row's part_id via
   * `add_update_field` - must NOT promote it, otherwise every adapter write
   * spawns a spurious row. Real DOM events carry `isTrusted === true`; the
   * queryselect `select` custom event is dispatched (untrusted) but represents
   * a real selection, so it is gated on its payload instead. */
  on_row_activity(e) {
    if (!this.config.auto_append || this.promoting) {
      return;
    }
    if (e.type === "select") {
      if (!(e.detail && e.detail.value)) {
        return;
      }
    } else if (!e.isTrusted) {
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

  set_row_ref(row, el) {
    if (el) {
      row.dom = el;
    }
  }

  /* Mount the per-cell React widgets within the given root element */
  mount_cell_widgets(root) {
    const mount = window.senaite?.core?.render_all_widgets;
    if (mount && root) {
      mount(root);
    }
  }

  /* -- rendering ------------------------------------------------------- */

  /* Per-row disabled flags for the manipulator buttons (port of the former
   * `set_ui_state`): the auto-append row disables all buttons, and up/down are
   * disabled at the first/last real row. */
  button_flags() {
    const last = this.rows.length - 1;
    return this.rows.map((row, i) => {
      if (row.is_aa) {
        return { add: true, del: true, up: true, down: true };
      }
      return { add: false, del: false, up: i === 0, down: i === last };
    });
  }

  render() {
    const flags = this.button_flags();
    const callbacks = {
      add: this.on_add,
      delete: this.on_delete,
      moveup: this.on_moveup,
      movedown: this.on_movedown,
      ref: this.set_row_ref,
    };

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
               name={this.config.name_prefix + ".count"}
               value={this.count_real_rows()}
               readOnly />
      </div>
    );
  }
}


// -- module helpers ----------------------------------------------------

const escape_re = (str) => str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

const trigger_custom_event = (name, data) => {
  document.body.dispatchEvent(new CustomEvent(name, { detail: data }));
};

/* Rewrite the row index embedded in an attribute value across a `<tr>`.
 *
 * Every element whose `attr` value starts with `prefix + old_index` (or
 * contains it, for `href` fragments) is rewritten to `prefix + new_index`.
 * When `json` is set the value is JSON-encoded (as the queryselect mount nodes
 * store `data-name`/`data-id`): it is decoded, rewritten, re-encoded, and the
 * mounted cell widget is notified to re-read it. */
const reindex_attr = (tr, attr, prefix, old_index, new_index, json = false) => {
  const from = prefix + old_index;
  const pattern = new RegExp("^" + escape_re(from));
  // `href` embeds the id as a `#fragment`, so match it anywhere in the value
  const selector = attr === "href" ? `[href*="${from}"]` : `[${attr}]`;

  tr.querySelectorAll(selector).forEach((el) => {
    const raw = el.getAttribute(attr);
    if (!raw) {
      return;
    }
    const quoted = json && raw.charAt(0) === "\"";
    let value = raw;
    if (quoted) {
      try {
        value = JSON.parse(raw);
      } catch (err) {
        return;
      }
    }
    if (!pattern.test(value)) {
      return;
    }
    value = value.replace(pattern, prefix + new_index);
    el.setAttribute(attr, quoted ? JSON.stringify(value) : value);
    if (json) {
      el.dispatchEvent(new CustomEvent(EVENT_CELL_REINDEXED, { bubbles: false }));
    }
  });
};

/* Locate the controller responsible for the given tbody/row element */
const find_controller = (el) => {
  if (!el) {
    return null;
  }
  const tbody = el.matches && el.matches(BODY_SELECTOR)
    ? el
    : (el.closest ? el.closest(BODY_SELECTOR) : null);
  return REGISTRY.find((ctrl) => ctrl.tbody === tbody) || null;
};


// -- global facade -----------------------------------------------------

/* Preserves the former `window.widgets.datagrid` API. Consumers (e.g. the
 * calculation edit form) call these with DOM elements, which we route to the
 * owning controller via the registry. */
window.widgets = window.widgets || {};
if (!window.widgets.datagrid) {
  window.widgets.datagrid = {
    get_visible_rows(table) {
      const ctrl = find_controller(table);
      return ctrl ? ctrl.get_visible_rows().map((row) => row.dom) : [];
    },
    remove_row(row) {
      const ctrl = find_controller(row);
      const model = ctrl && ctrl.rows.find((r) => r.dom === row);
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
