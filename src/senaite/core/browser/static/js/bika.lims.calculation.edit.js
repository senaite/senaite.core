/**
 * Controller class for calculation edit page.
 */
function CalculationEditView() {
    var that = this;

    that.load = function() {
        // Immediately hide the TestParameters_more button
        $("#TestParameters_more").hide();

        // When updating Formula, we must modify TestParameters
        $(document).on("change", "#Formula", function(event) {
            // Get existing param keywords
            var existingParams = [];
            $("[id^=TestParameters-keyword]").each(function() {
                existingParams.push($(this).val());
            });

            // Find param keywords used in formula
            var formula = $("#Formula").val();
            var matches = formula.match(/\[[^\]]*\]/gi) || [];

            // Add missing params to bottom of list
            matches.forEach(function(keyword) {
                keyword = keyword.replace("[", "").replace("]", "");
                if (existingParams.indexOf(keyword) === -1) {
                    var existingRows = $(".records_row_TestParameters");
                    var lastRow = existingRows.last();
                    var newRowIndex = existingRows.length.toString();

                    var newRow = lastRow.clone(true);

                    // Update keyword and IDs
                    newRow.find("[id^=TestParameters-keyword]")
                        .val(keyword)
                        .attr("id", "TestParameters-keyword-" + newRowIndex);
                    newRow.find("[id^=TestParameters-value]")
                        .attr("id", "TestParameters-value-" + newRowIndex);

                    // Insert the new row before the last one
                    newRow.insertBefore(lastRow);
                }
            });
        });
    };
}
