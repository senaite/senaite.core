jQuery(function($){
    $(document).ready(function(){
        var widgets = $('div.RejectionWidget');
        for (var i=0;i < widgets.length;i++){
            hide_show_other($(widgets[i]))
            hide_show_options($(widgets[i]));
        };
        $('input.rejectionwidget-checkbox-other').bind("change copy", function () {
            hide_show_other($(this).closest('div.RejectionWidget'));
        });
        $('input.rejectionwidget-checkbox').bind("change copy", function () {
            hide_show_options($(this).closest('div.RejectionWidget'));
        });
    });
});

function hide_show_options(div_widget) {
    // Hide/show the rejection options divisions depending on the checkbox status
    var checkbox = $(div_widget).find('.rejectionwidget-checkbox').attr('checked');
    if (checkbox == "checked") {
        // Showing the options-set
        $(div_widget).find('div.options-set').show();
    }
    else{
        // Hide the options-set
        $(div_widget).find('div.options-set').hide();
    }
};
function hide_show_other(div_widget) {
    // Hide/show the "other" text field option depending on the checkbox status
    var checkbox = $(div_widget).find('.rejectionwidget-checkbox-other').attr('checked');
    if (checkbox == "checked") {
        // Showing the options-set
        $(div_widget).find('.rejectionwidget-input-other').show();
    }
    else{
        // Hide the options-set
        $(div_widget).find('.rejectionwidget-input-other').hide();
    }
}
