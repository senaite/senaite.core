/* SENAITE DataGrid Widget Handler
 */

// IE NodeList.forEach polyfill.
// See: https://developer.mozilla.org/en-US/docs/Web/API/NodeList/forEach#polyfill
if (window.NodeList && !NodeList.prototype.forEach) {
  NodeList.prototype.forEach = Array.prototype.forEach;
}

window.widgets = window.widgets || {};


document.addEventListener("DOMContentLoaded", () => {

  // duplicate declaration when in global namespace
  class DataGrid {
    constructor() {
      console.debug("DataGrid::constructor");
      this.datagrids = document.querySelectorAll(".datagridwidget-body");
      this._define_handler();
      for (const datagrid of this.datagrids) {
        this.init_datagrid_rows(datagrid);
        this.init_auto_append_handler(datagrid);
      }
      return this;
    }

    init_datagrid_rows(datagrid) {
      let rows = this.get_rows(datagrid);
      for (const row of rows) {
        this.init_row(row);
      }
    }

    init_row(row) {
      // bind event handlers to row buttons
      let buttons = this.get_row_buttons(row);
      for (const [action, el] of Object.entries(buttons)) {
        if (!el) {
          continue;
        }
        el.addEventListener("click", this[`on_${action}`].bind(this));
      }
    }

    init_auto_append_handler(datagrid) {
      if (!this.is_auto_append_allowed(datagrid)) {
        return;
      }
      this.get_visible_rows(datagrid).forEach(function (row) {
        row.removeEventListener("focusout", this.on_auto_append);
      }, this);

      var last_row = this.get_last_visible_row(datagrid);
      if (last_row) {
        last_row.addEventListener("focusout", this.on_auto_append);
      }
    }

    _define_handler() {
        // Store event handler which also has to be removed, so we can detach it.
        // See: https://stackoverflow.com/a/10444156/1337474 , also comment about "bind"
        // using ``bind`` will change the function signature too.

        this.on_auto_append = function (e) {
          if (e) {
              e.stopPropagation();
          }
          // Also allow direct call without event.
          if (e && !e.target.closest(".datagridwidget-cell")) {
              return;
          }
          let datagrid = e.target.closest(".datagridwidget-body")
          this.auto_append_row(datagrid);
        }.bind(this);

        this.on_auto_append_input = function (e) {
          var row = e.currentTarget;
          let datagrid = row.closest(".datagridwidget-body")
          row.classList.remove("auto-append");
          row.dataset.oldIndex = row.dataset.index; // store for replacing.
          delete row.dataset.index; // remove "AA" index
          this.update_order_index(datagrid);
          row.removeEventListener("input", this.on_auto_append_input);
        }.bind(this);
    }

    get_rows(datagrid) {
      return datagrid.querySelectorAll(".datagridwidget-row");
    }

    get_visible_rows(datagrid) {
      return datagrid.querySelectorAll(".datagridwidget-row:not([data-index=TT])")
    }

    get_last_row(datagrid) {
      return datagrid.querySelector(".datagridwidget-row:last-child");
    }

    get_last_visible_row(datagrid) {
      let result = datagrid.querySelectorAll(
        ".datagridwidget-row:not([data-index=TT])"
      );
      return result[result.length - 1];
    }

    count_rows(datagrid) {
      let cnt = 0;
      let rows = this.get_rows(datagrid);
      for (const row of rows) {
        if (["AA", "TT"].indexOf(row.dataset.index) === -1) {
          cnt++;
        }
      }
      return cnt;
    }

    is_auto_append_allowed(datagrid) {
      return (datagrid.dataset.autoAppend || "true").toLowerCase() !== "false";
    }

    auto_append_row(datagrid) {
      this.get_visible_rows(datagrid).forEach(function (row) {
          row.classList.remove("auto-append");
          if (row.dataset.index !== "TT") {
              // actually, getVisibleRows should only return non-"TT"
              // rows, but to be clear here...
              // delete the index, we're setting it in updateOrderIndex again.
              row.dataset.oldIndex = row.dataset.index; // store for replacing.
              delete row.dataset.index;
          }
      });
      var last_row = this.get_last_visible_row(datagrid) || this.get_last_row(datagrid);
      let new_row = this.insert_row(last_row);
      new_row.classList.add("auto-append");
      this.reindex_row(datagrid, new_row, "AA");
      this.update_order_index(datagrid);
      new_row.addEventListener("input", this.on_auto_append_input);
    }

    get_row_buttons(row) {
      return {
        add: row.querySelector(".dgf--row-add"),
        del: row.querySelector(".dgf--row-delete"),
        up: row.querySelector(".dgf--row-moveup"),
        down: row.querySelector(".dgf--row-movedown"),
      }
    }

    find_datagrid(el) {
      return el.closest(".datagridwidget-body");
    }

    move_row(row, direction) {
      let datagrid = this.find_datagrid(row);
      let rows = this.get_rows(datagrid);
      let validrows = this.count_rows(datagrid);
      let idx = [].indexOf.call(rows, row);
      let ref_idx = 0;

      if (idx === -1) {
        return;
      }

      if (idx + 1 == validrows) {
        ref_idx = direction == "down" ? 0 : idx - 1;
      } else if (idx == 0) {
        ref_idx = direction == "up" ? validrows : idx + 2;
      } else {
        ref_idx = direction == "up" ? idx - 1  : idx + 2;
      }

      $(row).insertBefore(rows[ref_idx]);
      this.update_order_index(datagrid)
      this.init_auto_append_handler(datagrid)
    }

    move_row_up(row) {
      this.move_row(row, "up");
    }

    move_row_down(row) {
      this.move_row(row, "down");
    }

    remove_row(row) {
      let datagrid = row.closest(".datagridwidget-body")
      row.remove();
      this.update_order_index(datagrid);
      this.init_auto_append_handler(datagrid);
      let event_data = {datagrid: datagrid, row: row}
      this.trigger_custom_event("datagrid:row_removed", event_data);
    }

    insert_row(ref_row, before=false) {
      let datagrid = ref_row.closest(".datagridwidget-body")
      let newtr = this.create_new_row(datagrid);
      var $newtr = $(newtr);

      if (before) {
        $newtr.insertBefore(ref_row);
      } else {
        $newtr.insertAfter(ref_row);
      }
      this.init_auto_append_handler(datagrid);
      let event_data = {datagrid: datagrid, row: newtr}
      this.trigger_custom_event("datagrid:row_added", event_data);
      return newtr;
    }

    create_new_row(datagrid) {
      // hidden template row
      let template_row = datagrid.querySelector("[data-index=TT]");
      if (!template_row) {
        throw new Error("Could not locate empty template row in DGF");
      }

      let new_row = template_row.cloneNode(true);

      new_row.dataset.oldIndex = new_row.dataset.index; // store for replacing.
      delete new_row.dataset.index; // fresh row.
      new_row.classList.remove("datagridwidget-empty-row");
      this.init_row(new_row);
      return new_row;
    }

    update_order_index(datagrid) {
      let cnt = 0;
      let rows = this.get_rows(datagrid);

      for (const row of rows) {
        let index = row.dataset.index;
        if (["AA", "TT"].indexOf(index) > -1) {
          this.reindex_row(datagrid, row, index);
        } else {
          this.reindex_row(datagrid, row, cnt);
          row.dataset.index = cnt;
          cnt++;
        }
      }

      let name_prefix = datagrid.dataset.name_prefix + ".";
      let count_el = document.querySelector(
        'input[name="' + name_prefix + 'count"]');
      count_el.value = this.count_rows(datagrid);
      this.set_ui_state(datagrid);
    }

    reindex_row(datagrid, row, new_index) {
      let name_prefix = datagrid.dataset.name_prefix + ".";
      let id_prefix = datagrid.dataset.id_prefix + "-";
      let old_index = row.dataset.oldIndex || row.dataset.index;
      delete row.dataset.oldIndex;
      row.dataset.index = new_index; // update index data

      function replace_index(el, attr, prefix) {
        let val = el.getAttribute(attr);
        if (val) {
          var pattern = new RegExp("^" + prefix + old_index);
          el.setAttribute(attr, val.replace(pattern, prefix + new_index));
        }
      }

      row.querySelectorAll('[id^="formfield-' + id_prefix + '"]').forEach(function (el) {
        replace_index(el, "id", "formfield-" + id_prefix);
      }, this);
      row.querySelectorAll('[name^="' + name_prefix + '"]').forEach(function (el) {
        replace_index(el, "name", name_prefix);
      }, this);
      row.querySelectorAll('[id^="' + id_prefix + '"]').forEach(function (el) {
        replace_index(el, "id", id_prefix);
      }, this);
      row.querySelectorAll('[for^="' + id_prefix + '"]').forEach(function (el) {
        replace_index(el, "for", id_prefix);
      }, this);
      row.querySelectorAll('[href*="#' + id_prefix + '"]').forEach(function (el) {
        replace_index(el, "href", "#" + id_prefix);
      }, this);
      row.querySelectorAll('[data-fieldname^="' + name_prefix + '"]').forEach(function (el) {
        replace_index(el, "data-fieldname", name_prefix);
      }, this);
    }

    set_ui_state(datagrid) {
      let rows = this.get_visible_rows(datagrid);

      for (let cnt = 0; cnt < rows.length; cnt++) {
        let row = rows[cnt];
        let buttons = this.get_row_buttons(row);

        if (row.dataset.index === "AA") {
          // Special case AA

          if (buttons.add) {
            buttons.add.disabled = true;
          }
          if (buttons.delete) {
            buttons.delete.disabled = true;
          }
          if (buttons.up) {
            buttons.up.disabled = true;
          }
          if (buttons.down) {
            buttons.down.disabled = true;
          }
          if (cnt > 0) {
            // Set the previous buttons also, if available.
            let before_aa_buttons = this.get_row_buttons(
              rows[cnt - 1]
            );
            if (before_aa_buttons.down) {
              before_aa_buttons.down.disabled = true;
            }
          }
        } else if (cnt === 0) {
          // First row

          if (buttons.add) {
            buttons.add.disabled = false;
          }
          if (buttons.delete) {
            buttons.delete.disabled = false;
          }
          if (buttons.up) {
            buttons.up.disabled = true;
          }
          if (buttons.down) {
            buttons.down.disabled = rows.length === 1; // disable if 1 row.
          }
        } else if (cnt === rows.length - 1) {
          // Last button - if no AA buttons.
          // Also, if this is reached, it's not the only row.
          if (buttons.add) {
            buttons.add.disabled = false;
          }
          if (buttons.delete) {
            buttons.delete.disabled = false;
          }
          if (buttons.up) {
            buttons.up.disabled = false;
          }
          if (buttons.down) {
            buttons.down.disabled = true;
          }
        } else {
          // Normal in-between case.
          if (buttons.add) {
            buttons.add.disabled = false;
          }
          if (buttons.delete) {
            buttons.delete.disabled = false;
          }
          if (buttons.up) {
            buttons.up.disabled = false;
          }
          if (buttons.down) {
            buttons.down.disabled = false;
          }
        }
      }
    }

    trigger_custom_event(event_name, event_data) {
      let event = new CustomEvent(event_name, {detail: event_data});
      document.body.dispatchEvent(event);
    }

    /* EVENT HANDLERS */

    on_add(event) {
      event.preventDefault();
      let el = event.currentTarget;
      let row = el.closest("tr")
      console.debug("DataGrid::on_add:", row);
      this.insert_row(row);
    }

    on_del(event) {
      event.preventDefault();
      let el = event.currentTarget;
      let row = el.closest("tr")
      console.debug("DataGrid::on_del:", row);
      this.remove_row(row);
    }

    on_up(event) {
      event.preventDefault();
      let el = event.currentTarget;
      let row = el.closest("tr")
      console.debug("DataGrid::on_up:", row);
      this.move_row_up(row);
    }

    on_down(event) {
      event.preventDefault();
      let el = event.currentTarget;
      let row = el.closest("tr")
      console.debug("DataGrid::on_down:", row);
      this.move_row_down(row);
    }
  }

  // Initialize datagrids
  if (window.widgets.datagrid === undefined) {
    console.log("DataGrid::DOMContentLoaded");
    window.widgets.datagrid = new DataGrid();
    //trigger custom event to let dependent components know that datagrid ready for work
    window.widgets.datagrid.trigger_custom_event("datagrid:loaded")
  }
});
