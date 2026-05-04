/* Show/hide the GHS hazard category field on the SampleType edit
 * form depending on the state of the "Hazardous" checkbox.
 *
 * The field is rendered by Plone's DX form machinery so the wrapper
 * id is predictable: `formfield-form-widgets-<fieldname>`.
 */
(function () {
  "use strict";

  function init() {
    var checkbox = document.querySelector(
      "input[name='form.widgets.hazardous:list']");
    var wrapper = document.getElementById(
      "formfield-form-widgets-hazard_categories");
    if (!checkbox || !wrapper) {
      return;
    }
    var sync = function () {
      wrapper.hidden = !checkbox.checked;
    };
    checkbox.addEventListener("change", sync);
    sync();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
