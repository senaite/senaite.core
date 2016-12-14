jQuery(function($){
    $(document).ready(function(){
        hide_show_options();
        $('input.rejectionwidget-checkbox').bind("change", function () {
            hide_show_options();
        });
        rejectionwidget_loadEventHandlers();
    });
});

function hide_show_options() {
    // Hide/show the rejection options divisions depending on the checkbox status
    var checkbox = $('input.rejectionwidget-checkbox').attr('checked');
    if (checkbox == "checked") {
        // Showing the options-set
        $('div.options-set-container').show();
    }
    else{
        // Hide the options-set
        $('div.options-set-container').hide();
    }
}
function rejectionwidget_loadEventHandlers() {
    // Append an option div at the end of the options set
    $("#RejectionReasons_more").click(function(i,e){
        var fieldname = $(this).attr("id").split("_")[0];
        var optionsset = $('div.options-set');
        var all_optionset = $('div.option-set');
        // clone last text set
        var option = $(all_optionset[all_optionset.length-1]).clone();
        // after cloning, make sure the new element's IDs are unique
        var input = $(option).find("input[id^='"+fieldname+"']");
        var input_ID = $(input).attr('id');
        var input_name = $(input).attr('name');
        var option_ID = $(option).attr('id');
        var input_id_prefix = input_ID.split("-")[0] + "-" + input_ID.split("-")[1];
        var input_name_prefix = input_name.split("-")[0];
        var option_prefix = option_ID.split("-")[0] + "-" + option_ID.split("-")[1];
        // New id for input and div
        var nr = parseInt(input_ID.split("-")[2]) + 1;
        $(input).attr('id', input_id_prefix + "-" + nr).val('');
        $(input).attr('name', input_name_prefix + "-" + nr + ":records:ignore_empty").val('');
        $(option).attr('id', option_prefix + "-" + nr).val('');
        $(option).appendTo($(optionsset));
    });
    $(".rej_deletebtn").live('click', function(i,e){
        if($(".RejectionSetupWidget .option-set").length > 1){
            // Remove an option div IF it is not the last item.
            $(this).parent().remove();
        } else {
            // If this is the last item, just clear the fields
           $(".RejectionSetupWidget input[type='text']").val('');
        }

    });
}
