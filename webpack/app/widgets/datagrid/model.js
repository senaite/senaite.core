/* SENAITE DataGrid Widget - server DOM capture
 *
 * The datagrid cells are rendered server-side by z3c.form (plain inputs for
 * simple fields, mount `<div>`s for the React queryselect/uidreference cells).
 * We capture those cell nodes *before* React (and the per-cell widgets) mount,
 * so the controller can adopt them into its own React-rendered rows while the
 * request-key contract (`form.widgets.<name>.<idx>.widgets.<sub>`) stays intact.
 */

// Cells rendered by the server that the datagrid manages itself (row buttons).
const MANIPULATOR_CLASS = "datagridwidget-manipulator";


/* Read the manipulation/config flags from the mount element dataset */
const read_config = (el, tbody) => {
  return {
    name_prefix: tbody.dataset.name_prefix,
    id_prefix: tbody.dataset.id_prefix,
    allow_insert: el.dataset.allow_insert !== "false",
    allow_delete: el.dataset.allow_delete !== "false",
    allow_reorder: el.dataset.allow_reorder !== "false",
    auto_append: (el.dataset.auto_append || "true") !== "false",
  };
};


/* Capture the data cells of a single server-rendered `<tr>`
 *
 * Returns a list of `{className, node}` where `node` is the server `<td>`.
 * Manipulator cells (row buttons) are skipped - the controller renders those.
 */
const read_cells = (tr) => {
  const cells = [];
  for (const td of Array.from(tr.children)) {
    if (td.classList.contains(MANIPULATOR_CLASS)) {
      continue;
    }
    cells.push({ className: td.className, node: td });
  }
  return cells;
};


/* Capture the full server-rendered datagrid model from the mount element */
export const read_model = (el) => {
  const table = el.querySelector("table.datagridwidget-table-view");
  const tbody = table.querySelector("tbody.datagridwidget-body");
  const thead = table.querySelector("thead");
  const config = read_config(el, tbody);

  const rows = [];
  let template = null;

  for (const tr of Array.from(tbody.children)) {
    const index = tr.dataset.index;
    const cells = read_cells(tr);
    if (index === "TT") {
      // hidden template row - clone source for new rows
      template = { cells };
    } else if (index === "AA") {
      // server-rendered auto-append row - the controller manages it itself
      continue;
    } else {
      rows.push({ index: index, cells: cells });
    }
  }

  return { thead, config, rows, template };
};
