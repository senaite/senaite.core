jQuery(function($) {

    function toggleOptionsVisibility($widget) {
        const isChecked = $widget.find(".rejectionwidget-checkbox").prop("checked");
        $widget.find("div.options-set").toggle(isChecked);
    }

    function toggleOtherInputVisibility($widget) {
        const isChecked = $widget.find(".rejectionwidget-checkbox-other").prop("checked");
        $widget.find(".rejectionwidget-input-other").toggle(isChecked);
    }

    $(function() {
        const $widgets = $("div.RejectionWidget");

        $widgets.each(function() {
            const $widget = $(this);
            toggleOptionsVisibility($widget);
            toggleOtherInputVisibility($widget);
        });

        $(document).on("change copy", "input.rejectionwidget-checkbox", function() {
            toggleOptionsVisibility($(this).closest("div.RejectionWidget"));
        });

        $(document).on("change copy", "input.rejectionwidget-checkbox-other", function() {
            toggleOtherInputVisibility($(this).closest("div.RejectionWidget"));
        });
    });

});
