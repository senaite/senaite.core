/**
 * Edit Analysis Modal - Dynamic field behavior
 *
 * Handles auto-append for multiselect-duplicates and
 * multivalue fields, and datetime combining.
 */
(function() {
  "use strict";

  /**
   * Auto-append a new empty field when the last field
   * in a container has a value.
   */
  function autoAppend(container, tagName) {
    var fields = container.querySelectorAll(tagName);
    var last = fields[fields.length - 1];
    if (!last) {
      return;
    }
    var hasValue = tagName === "select"
      ? last.value !== ""
      : last.value.trim() !== "";
    if (!hasValue) {
      return;
    }
    var clone = last.cloneNode(true);
    if (tagName === "select") {
      clone.selectedIndex = 0;
    } else {
      clone.value = "";
    }
    container.appendChild(clone);
    bindAutoAppend(container, tagName);
  }

  /**
   * Bind change/blur events to trigger auto-append.
   */
  function bindAutoAppend(container, tagName) {
    var fields = container.querySelectorAll(tagName);
    fields.forEach(function(field) {
      field.onchange = function() {
        autoAppend(container, tagName);
      };
      if (tagName === "input") {
        field.onblur = function() {
          autoAppend(container, tagName);
        };
      }
    });
  }

  /**
   * Combine date and time inputs into a hidden field.
   */
  function bindDatetime(container) {
    var dateInput = container.querySelector(
      "input[type=\"date\"]"
    );
    var timeInput = container.querySelector(
      "input[type=\"time\"]"
    );
    var hiddenInput = container.querySelector(
      "input[type=\"hidden\"]"
    );
    if (!dateInput || !hiddenInput) {
      return;
    }

    function update() {
      var dateVal = dateInput.value || "";
      var timeVal = timeInput ? timeInput.value : "";
      if (dateVal && !timeVal) {
        timeVal = "00:00";
      }
      hiddenInput.value = dateVal && timeVal
        ? dateVal + " " + timeVal
        : "";
    }

    dateInput.addEventListener("change", update);
    if (timeInput) {
      timeInput.addEventListener("change", update);
    }
  }

  // Initialize multiselect-duplicates
  document.querySelectorAll(".multiselect-duplicates")
    .forEach(function(el) {
      bindAutoAppend(el, "select");
    });

  // Initialize multivalue
  document.querySelectorAll(".multivalue")
    .forEach(function(el) {
      bindAutoAppend(el, "input");
    });

  // Initialize datetime widgets
  document.querySelectorAll(".datetimewidget")
    .forEach(function(el) {
      bindDatetime(el);
    });
})();
