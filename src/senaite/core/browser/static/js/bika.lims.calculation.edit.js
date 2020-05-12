/**
 * Controller class for calculation edit page.
 */
function CalculationEditView() {

    var that = this;

    that.load = function() {

        // Immediately hide the TestParameters_more button
        $("#TestParameters_more").hide();

        // When updating Formula, we must modify TestParameters
        $('#Formula').live('change', function(event){

            // Get existing param keywords
            var existing_params = [];
            $.each($("[id^=TestParameters-keyword]"), function(i, e){
                existing_params.push($(e).val());
            });

            // Find param keywords used in formula
            var formula = $("#Formula").val();
            var re = /\[[^\]]*\]/gi;
            var used = formula.match(re);

            // Add missing params to bottom of list
            $.each(used, function(i, e){
                e = e.replace('[', '').replace(']', '');
                if(existing_params.indexOf(e) == -1){
                    // get the last (empty) param row, for copying
                    var existing_rows = $(".records_row_TestParameters");
                    var lastrow = $(existing_rows[existing_rows.length-1]);
                    // row_count for renaming new row
                    var nr = existing_rows.length.toString();
                    // clone row
                    var newrow = $(lastrow).clone(true);
                    // insert the keyword into the new row
                    $(newrow).find('[id^=TestParameters-keyword]').val(e);
                    // rename IDs of inputs
                    $(newrow).find('[id^=TestParameters-keyword]').attr('id', 'TestParameters-keyword-' + nr);
                    $(newrow).find('[id^=TestParameters-value]').attr('id', 'TestParameters-value-' + nr);
                    $(newrow).insertBefore(lastrow);
                }
            });
        });
    }

}
