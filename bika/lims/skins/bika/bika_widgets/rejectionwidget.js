jQuery(function($){
    $(document).ready(function(){
        hide_show_options();
        $('input[type="checkbox"]').bind("change", function () {
            hide_show_options();
        });
        rejectionwidget_loadEventHandlers();
    });
});

function hide_show_options() {
    // Hide/show the rejection options divisions depending on the checkbox status
    var checkbox = $('input[type="checkbox"]').attr('checked');
    if (checkbox == "checked") {
        // Showing the options-set
        $('div.options-set').show();
    }
    else{
        // Hide the options-set
        $('div.options-set').hide();
    }
}
function rejectionwidget_loadEventHandlers() {
    // Append an option div at the end of the options set
    $("input[id$='_more']").click(function(i,e){
        var fieldname = $(this).attr("id").split("_")[0];
        var optionsset = $('div.options-set');
        var all_optionset = $('div.option-set');
        // clone last text set
        var option = $(all_optionset[all_optionset.length-1]).clone();
        // after cloning, make sure the new element's IDs are unique
        var input = $(option).find("input[id^='"+fieldname+"']");
        var ID = $(input).attr('id');
        var prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
        // New id
        var nr = parseInt(ID.split("-")[2]) + 1;
        $(input).attr('id', prefix + "-" + nr).val('');
        $(option).appendTo($(optionsset));
    });
    // Remove an option div
    $(".rej_deletebtn").live('click', function(i,e){
        var option = $(this).parent();
        var siblings = $(option).siblings();
        if (siblings.length > 0) {
            $(this).parent().remove();
        };
        return
    });
}
