/**
 * Partition Magic Controller
 *
 * This controller is loaded for the partition view
 */
window.PartitionController = class PartitionController {
  constructor() {
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.on_analysis_click = this.on_analysis_click.bind(this);
  }

  load() {
    console.debug("PartitionController::load");
    this.bind_eventhandler();
  }

  /**
   * Binds delegated event handlers to the DOM
   */
  bind_eventhandler() {
    console.debug("PartitionController::bind_eventhandler");

    $("body").on("click", "tr.analysis", this.on_analysis_click);
  }

  /**
   * Handles click on analysis row
   * If the user clicks on an empty area of the row, the row's checkbox is
   * toggled. Clicks on interactive elements (links, inputs, labels, e.g. the
   * service info icon) are ignored, so they keep their own behavior.
   */
  on_analysis_click(event) {
    const $row = $(event.currentTarget);

    if ($(event.target).closest("a, input, button, select, label").length) {
      return;
    }

    $row.find("input[type=checkbox]").trigger("click");
  }
}
