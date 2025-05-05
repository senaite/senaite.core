/**
 * Calculation Edit Form Controller
 *
 * This controller is loaded for the calculation edit view, e.g.
 * `/senaite/bika_setup/bika_calculations/calculation-1`.
 */
window.CalculationEditView = class CalculationEditView {
  constructor() {
    this.load = this.load.bind(this);
    this.onFormulaChange = this.onFormulaChange.bind(this);
  }

  load() {
    // Immediately hide the TestParameters_more button
    $("#TestParameters_more").hide();

    // Bind change event to formula input
    $(document).on("change", "#Formula", this.onFormulaChange);
  }

  onFormulaChange() {
    const existingParams = [];

    $("[id^=TestParameters-keyword]").each(function () {
      existingParams.push($(this).val());
    });

    const formula = $("#Formula").val();
    const matches = formula.match(/\[[^\]]*\]/gi) || [];

    matches.forEach((keyword) => {
      keyword = keyword.replace("[", "").replace("]", "");
      if (!existingParams.includes(keyword)) {
        const existingRows = $(".records_row_TestParameters");
        const lastRow = existingRows.last();
        const newRowIndex = existingRows.length.toString();
        const newRow = lastRow.clone(true);

        newRow.find("[id^=TestParameters-keyword]")
          .val(keyword)
          .attr("id", "TestParameters-keyword-" + newRowIndex);
        newRow.find("[id^=TestParameters-value]")
          .attr("id", "TestParameters-value-" + newRowIndex);

        newRow.insertBefore(lastRow);
      }
    });
  }
}
