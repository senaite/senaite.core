jQuery(function($) {
    function hide_show_options() {
        // Hide/show the rejection options divisions depending on the checkbox status
        var isChecked = $("input.rejectionwidget-checkbox").prop("checked");
        if (isChecked) {
            $("div.rejectionwidget-container").show();
        } else {
            $("div.rejectionwidget-container").hide();
        }
    }

    function rejectionwidget_loadEventHandlers() {
        // Append an option div at the end of the options set
        $("#RejectionReasons_more").on("click", function(e) {
            var fieldname = this.id.split("_")[0];
            var optionsset = $("div.options-set");
            var all_optionset = $("div.option-set");
            // Clone last option set
            var option = all_optionset.last().clone();
            var input = option.find("input[id^='" + fieldname + "']");
            var input_ID = input.attr('id');
            var input_name = input.attr('name');
            var option_ID = option.attr('id');

            var idParts = input_ID.split("-");
            var nameParts = input_name.split("-");
            var optionParts = option_ID.split("-");

            var nr = parseInt(idParts[2], 10) + 1;

            input.attr({
                'id': idParts[0] + "-" + idParts[1] + "-" + nr,
                'name': nameParts[0] + "-" + nr + ":records:ignore_empty"
            }).val('');

            option.attr('id', optionParts[0] + "-" + optionParts[1] + "-" + nr);
            option.appendTo(optionsset);
        });

        // Use event delegation for dynamic delete buttons
        $(document).on('click', ".rej_deletebtn", function(e) {
            e.preventDefault();
            var $optionSets = $(".RejectionSetupWidget .option-set");
            if ($optionSets.length > 1) {
                // Remove the option div
                $(this).closest('.option-set').remove();
            } else {
                // If it's the last option-set, just clear the fields
                $(".RejectionSetupWidget input[type='text']").val('');
            }
        });
    }

    // Initialize the widget
    hide_show_options();
    $('input.rejectionwidget-checkbox').on('change', hide_show_options);
    rejectionwidget_loadEventHandlers();
});
