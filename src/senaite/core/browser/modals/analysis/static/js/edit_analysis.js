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

  /**
   * Filter instrument options based on selected method.
   *
   * Reads the method-instrument mapping from the
   * data-method-instruments attribute on the instrument
   * select. Shows only instruments valid for the selected
   * method. Preserves the current selection if still valid.
   */
  function bindMethodInstrumentFilter() {
    var methodSelect = document.getElementById(
      "edit-analysis-method"
    );
    var instrumentSelect = document.getElementById(
      "edit-analysis-instrument"
    );
    if (!methodSelect || !instrumentSelect) {
      return;
    }
    var mappingJson = instrumentSelect.getAttribute(
      "data-method-instruments"
    );
    if (!mappingJson) {
      return;
    }
    var mapping = JSON.parse(mappingJson);

    // Store all instrument options on first call
    var allOptions = [];
    var options = instrumentSelect.querySelectorAll(
      "option"
    );
    options.forEach(function(opt) {
      allOptions.push({
        value: opt.value,
        text: opt.textContent,
        selected: opt.selected,
        disabled: opt.disabled
      });
    });

    function filterInstruments() {
      var methodUid = methodSelect.value || "";
      var validUids = mapping[methodUid] || mapping[""];
      var currentVal = instrumentSelect.value;

      // Clear all options
      instrumentSelect.innerHTML = "";

      // Re-add matching options
      allOptions.forEach(function(opt) {
        if (opt.value === "") {
          // Always keep the empty option
          var el = document.createElement("option");
          el.value = "";
          el.textContent = "";
          instrumentSelect.appendChild(el);
          return;
        }
        if (!validUids ||
            validUids.indexOf(opt.value) !== -1) {
          var el = document.createElement("option");
          el.value = opt.value;
          el.textContent = opt.text;
          el.disabled = opt.disabled;
          if (opt.value === currentVal && !opt.disabled) {
            el.selected = true;
          }
          instrumentSelect.appendChild(el);
        }
      });

      // Reset selection if current is no longer valid
      var currentOpt = instrumentSelect.querySelector(
        "option[value=\"" + currentVal + "\"]"
      );
      if (!currentOpt || currentOpt.disabled) {
        instrumentSelect.value = "";
      }
    }

    methodSelect.addEventListener(
      "change", filterInstruments
    );

    // Apply filter on initial load
    filterInstruments();
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

  // Initialize method-instrument filtering
  bindMethodInstrumentFilter();
})();
