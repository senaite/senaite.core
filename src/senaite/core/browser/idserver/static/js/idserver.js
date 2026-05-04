/* Number Generator view (/ng) UI behaviors:
 *   - Tab persistence via location.hash
 *   - Regex filter that updates tab badges
 *   - Live next-id preview as the counter input is edited
 *   - Visual marker and confirmation prompt on delete (counter == 0)
 *   - Sortable columns
 */
(function () {

    /* ---- Tab persistence via location.hash ---------------------------- */

    function activateTabFromHash() {
        var hash = location.hash;
        if (!hash || hash.length < 2) return;
        var trigger = document.querySelector(
            '.nav-tabs a[href="' + hash + '"]');
        if (!trigger) return;
        if (window.jQuery && window.jQuery.fn.tab) {
            window.jQuery(trigger).tab("show");
            return;
        }
        // Fallback if jQuery is not present
        var links = document.querySelectorAll(".nav-tabs .nav-link");
        for (var i = 0; i < links.length; i++) {
            links[i].classList.remove("active");
            links[i].setAttribute("aria-selected", "false");
        }
        var panes = document.querySelectorAll(".tab-pane");
        for (var j = 0; j < panes.length; j++) {
            panes[j].classList.remove("active", "show");
        }
        trigger.classList.add("active");
        trigger.setAttribute("aria-selected", "true");
        var pane = document.querySelector(hash);
        if (pane) pane.classList.add("active", "show");
    }

    function bindTabHashUpdate() {
        var links = document.querySelectorAll(
            '.nav-tabs [data-toggle="tab"]');
        for (var i = 0; i < links.length; i++) {
            links[i].addEventListener("click", function () {
                history.replaceState(null, "", this.getAttribute("href"));
            });
        }
    }

    /* ---- Filter (regex) ----------------------------------------------- */

    function applyFilter() {
        var input = document.getElementById("numbergenerator-filter");
        if (!input) return;
        var raw = input.value.trim();
        var rx = null;
        if (raw) {
            try { rx = new RegExp(raw, "i"); } catch (e) { rx = null; }
        }
        var rows = document.querySelectorAll(".numbergenerator-row");
        for (var i = 0; i < rows.length; i++) {
            var row = rows[i];
            if (!raw) { row.style.display = ""; continue; }
            if (!rx) { row.style.display = "none"; continue; }
            var cell = row.querySelector("td.numbergenerator-key");
            var key = cell ? cell.textContent : "";
            row.style.display = rx.test(key) ? "" : "none";
        }
        var panes = document.querySelectorAll(".tab-pane");
        for (var j = 0; j < panes.length; j++) {
            var pane = panes[j];
            var visible = 0;
            var paneRows = pane.querySelectorAll(".numbergenerator-row");
            for (var k = 0; k < paneRows.length; k++) {
                if (paneRows[k].style.display !== "none") visible++;
            }
            var link = document.getElementById(pane.id + "-link");
            if (!link) continue;
            var badge = link.querySelector(".badge");
            if (badge) badge.textContent = visible;
        }
    }

    /* ---- Live next-id preview ----------------------------------------- */

    function updateNextIdFor(input) {
        var row = input.closest("tr");
        if (!row) return;
        var cell = row.querySelector(".numbergenerator-next code");
        if (!cell) return;
        var counter = parseInt(input.value, 10);
        if (isNaN(counter)) return;
        var nextValue = counter + 1;
        // Preserve the original rendering on first edit so we can
        // restore widths consistently across keystrokes.
        if (!cell.dataset.original) {
            cell.dataset.original = cell.textContent;
        }
        var original = cell.dataset.original;
        // Replace the last contiguous digit run with the new value,
        // padded to the original width.
        var match = original.match(/(\d+)(?=\D*$)/);
        if (!match) return;
        var width = match[1].length;
        var padded = String(nextValue);
        while (padded.length < width) padded = "0" + padded;
        cell.textContent = original.substring(0, match.index) +
            padded + original.substring(match.index + match[1].length);
    }

    function markPendingDelete(input) {
        var row = input.closest("tr");
        if (!row) return;
        if (input.value === "0") {
            row.classList.add("pending-delete");
        } else {
            row.classList.remove("pending-delete");
        }
    }

    function bindCounterInputs() {
        var inputs = document.querySelectorAll(".numbergenerator-counter");
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].addEventListener("input", function () {
                updateNextIdFor(this);
                markPendingDelete(this);
            });
            // Initial state for already-zero values
            markPendingDelete(inputs[i]);
        }
    }

    /* ---- Confirmation on delete --------------------------------------- */

    function bindDeleteConfirmation() {
        var form = document.getElementById("manage_form");
        if (!form) return;
        form.addEventListener("submit", function (e) {
            var inputs = form.querySelectorAll(".numbergenerator-counter");
            var deletes = [];
            for (var i = 0; i < inputs.length; i++) {
                var input = inputs[i];
                if (input.value !== "0") continue;
                // Only count inputs whose stored value is non-zero,
                // i.e. the row would actually be removed.
                if (input.defaultValue === "0") continue;
                var row = input.closest("tr");
                var keyCell = row && row.querySelector(
                    ".numbergenerator-key");
                if (keyCell) {
                    deletes.push(keyCell.textContent.trim());
                }
            }
            if (deletes.length === 0) return;
            var preview = deletes.slice(0, 10).join("\n");
            if (deletes.length > 10) {
                preview += "\n... and " + (deletes.length - 10) + " more";
            }
            var msg = "Delete " + deletes.length +
                " counter(s)? This cannot be undone:\n\n" + preview;
            if (!confirm(msg)) {
                e.preventDefault();
                return false;
            }
        });
    }

    /* ---- Sortable columns --------------------------------------------- */

    function getCellValue(cell) {
        var input = cell.querySelector("input");
        if (input) return input.value;
        return cell.textContent.trim();
    }

    function compare(a, b, mode, asc) {
        if (mode === "number") {
            var aNum = parseFloat(a);
            var bNum = parseFloat(b);
            if (!isNaN(aNum) && !isNaN(bNum)) {
                return asc ? aNum - bNum : bNum - aNum;
            }
        }
        return asc ? a.localeCompare(b) : b.localeCompare(a);
    }

    function sortTable(table, th) {
        var col = parseInt(th.getAttribute("data-col"), 10);
        var mode = th.getAttribute("data-sort") || "text";
        var asc = th.getAttribute("data-sort-dir") !== "asc";
        var headers = table.querySelectorAll(".numbergenerator-th");
        for (var i = 0; i < headers.length; i++) {
            headers[i].removeAttribute("data-sort-dir");
        }
        th.setAttribute("data-sort-dir", asc ? "asc" : "desc");
        var tbody = table.querySelector("tbody");
        var rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
        rows.sort(function (r1, r2) {
            return compare(
                getCellValue(r1.children[col]),
                getCellValue(r2.children[col]),
                mode, asc);
        });
        for (var j = 0; j < rows.length; j++) {
            tbody.appendChild(rows[j]);
        }
    }

    function bindSortableColumns() {
        var tables = document.querySelectorAll(".numbergenerator-table");
        for (var i = 0; i < tables.length; i++) {
            var table = tables[i];
            var ths = table.querySelectorAll(".numbergenerator-th.sortable");
            (function (table, ths) {
                for (var j = 0; j < ths.length; j++) {
                    (function (th) {
                        th.addEventListener("click", function () {
                            sortTable(table, th);
                        });
                    })(ths[j]);
                }
            })(table, ths);
        }
    }

    /* ---- Init --------------------------------------------------------- */

    function init() {
        bindTabHashUpdate();
        activateTabFromHash();
        var filter = document.getElementById("numbergenerator-filter");
        if (filter) filter.addEventListener("input", applyFilter);
        bindCounterInputs();
        bindDeleteConfirmation();
        bindSortableColumns();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }

})();
