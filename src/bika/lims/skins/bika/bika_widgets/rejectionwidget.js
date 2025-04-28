jQuery(function($) {
    function hide_show_options(div_widget) {
        var isChecked = div_widget.find(".rejectionwidget-checkbox").prop("checked");
        if (isChecked) {
            div_widget.find("div.options-set").show();
        } else {
            div_widget.find("div.options-set").hide();
        }
    }

    function hide_show_other(div_widget) {
        var isChecked = div_widget.find(".rejectionwidget-checkbox-other").prop("checked");
        if (isChecked) {
            div_widget.find(".rejectionwidget-input-other").show();
        } else {
            div_widget.find(".rejectionwidget-input-other").hide();
        }
    }

    $(document).ready(function() {
        var widgets = $("div.RejectionWidget");

        widgets.each(function() {
            var $widget = $(this);
            hide_show_other($widget);
            hide_show_options($widget);
        });

        $(document).on("change copy", "input.rejectionwidget-checkbox-other", function() {
            var $widget = $(this).closest("div.RejectionWidget");
            hide_show_other($widget);
        });

        $(document).on("change copy", "input.rejectionwidget-checkbox", function() {
            var $widget = $(this).closest("div.RejectionWidget");
            hide_show_options($widget);
        });
    });
});
