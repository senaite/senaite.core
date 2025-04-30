jQuery(function($) {

    function hide_show_options() {
        // Toggle visibility of the rejection options container based on checkbox state
        const isChecked = $("input.rejectionwidget-checkbox").prop("checked");
        $("div.rejectionwidget-container").toggle(isChecked);
    }

    function rejectionwidget_loadEventHandlers() {
        // Handle adding new rejection reason input
        $("#RejectionReasons_more").on("click", function() {
            const fieldname = this.id.split("_")[0];
            const $optionsSet = $("div.options-set");
            const $lastOption = $("div.option-set").last();

            if (!$lastOption.length) return;

            const $newOption = $lastOption.clone();
            const $input = $newOption.find(`input[id^="${fieldname}"]`);

            const inputID = $input.attr("id") || "";
            const inputName = $input.attr("name") || "";
            const optionID = $newOption.attr("id") || "";

            const idParts = inputID.split("-");
            const nameParts = inputName.split("-");
            const optionParts = optionID.split("-");

            if (idParts.length < 3 || nameParts.length < 1 || optionParts.length < 3) return;

            const nextIndex = parseInt(idParts[2], 10) + 1;

            $input.attr({
                id: `${idParts[0]}-${idParts[1]}-${nextIndex}`,
                name: `${nameParts[0]}-${nextIndex}:records:ignore_empty`
            }).val("");

            $newOption.attr("id", `${optionParts[0]}-${optionParts[1]}-${nextIndex}`);
            $newOption.appendTo($optionsSet);
        });

        // Handle removal of rejection reason input
        $(document).on("click", ".rej_deletebtn", function(e) {
            e.preventDefault();
            const $optionSets = $(".RejectionSetupWidget .option-set");
            if ($optionSets.length > 1) {
                $(this).closest(".option-set").remove();
            } else {
                // Only clear if it's the last remaining option
                $(".RejectionSetupWidget input[type='text']").val('');
            }
        });
    }

    // Initialize the widget
    hide_show_options();
    $("input.rejectionwidget-checkbox").on("change", hide_show_options);
    rejectionwidget_loadEventHandlers();

});
