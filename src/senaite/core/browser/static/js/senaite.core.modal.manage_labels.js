/* Manage Labels modal — toggle chip selection, sync hidden field,
 * wire color presets and the random button.
 *
 * Loaded by `senaite/core/browser/modals/templates/manage_labels.pt`
 * via `++plone++senaite.core.static/js/senaite.core.modal.manage_labels.js`.
 *
 * The script is tolerant to multiple modal opens: it scopes every
 * query to the form element it finds and bails out silently when
 * the modal markup is not present.
 */
(function() {
  "use strict";

  function init() {
    var form = document.querySelector(".manage-labels-form");
    if (!form) return;

    var selectedField = form.querySelector(
      'input[name="selected_labels"]');
    var newInput = form.querySelector('input[name="new_label"]');
    var colorInput = form.querySelector('input[name="new_label_color"]');
    var toggles = form.querySelectorAll(".manage-labels-toggle");
    var presets = form.querySelectorAll(".manage-labels-preset");
    var randomBtn = form.querySelector(".manage-labels-random");

    function syncSelectedField() {
      var picked = [];
      toggles.forEach(function(btn) {
        if (btn.getAttribute("data-selected") === "1") {
          picked.push(btn.getAttribute("data-label"));
        }
      });
      if (selectedField) {
        selectedField.value = picked.join(",");
      }
    }

    function onToggleClick(event) {
      var btn = event.currentTarget;
      var on = btn.getAttribute("data-selected") === "1";
      btn.setAttribute("data-selected", on ? "0" : "1");
      btn.classList.toggle("is-selected", !on);
      btn.classList.toggle("is-removed", on);
      syncSelectedField();
    }

    function onPresetClick(event) {
      if (!colorInput) return;
      colorInput.value = event.currentTarget.getAttribute("data-color");
    }

    function onRandomClick() {
      if (!colorInput) return;
      var hex = "#" + Math.floor(Math.random() * 0xffffff)
        .toString(16).padStart(6, "0");
      colorInput.value = hex;
    }

    toggles.forEach(function(btn) {
      btn.addEventListener("click", onToggleClick);
      if (btn.getAttribute("data-selected") === "1") {
        btn.classList.add("is-selected");
      }
    });
    presets.forEach(function(sw) {
      sw.addEventListener("click", onPresetClick);
    });
    if (randomBtn) {
      randomBtn.addEventListener("click", onRandomClick);
    }

    syncSelectedField();
    if (newInput) newInput.focus();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    // Modal markup is already in the DOM (the listing controller
    // injects it after the document is ready).
    init();
  }
})();
