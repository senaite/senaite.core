/**
 * Client Edit Form Controller
 *
 * This controller is loaded for the client edit view, e.g.
 * `/senaite/clients/client-1`.
 */
window.ClientEditView = class ClientEditView {
  constructor() {
    this.$decimalMarkField = $("#archetypes-fieldname-DecimalMark");
    this.$decimalMarkToggle = $("#DefaultDecimalMark");

    // Bind methods
    this.load = this.load.bind(this);
    this.initializeDecimalMarkBehavior = this.initializeDecimalMarkBehavior.bind(this);
    this.toggleDecimalMarkVisibility = this.toggleDecimalMarkVisibility.bind(this);
  }

  /**
   * Entry-point method
   */
  load() {
    this.initializeDecimalMarkBehavior();
  }

  /**
   * Controls visibility of DecimalMark field based on toggle
   */
  initializeDecimalMarkBehavior() {
    this.toggleDecimalMarkVisibility(this.$decimalMarkToggle.is(":checked"));

    this.$decimalMarkToggle.on("change", () => {
      this.toggleDecimalMarkVisibility(this.$decimalMarkToggle.is(":checked"));
    });
  }

  toggleDecimalMarkVisibility(isChecked) {
    if (isChecked) {
      this.$decimalMarkField.fadeOut();
    } else {
      this.$decimalMarkField.fadeIn();
    }
  }
}
