jQuery(function($){
$(document).ready(function(){

    $("input[id$='_more']").click(function(i,e){
        fieldname = $(this).attr("id").split("_")[0];
        table = $('#'+fieldname+"_table");
        row = $($(".records_row_"+fieldname)[0]).clone();
        for(i=0; i<$(row).children().length; i++){
            td = $(row).children()[i];
            input = $(td).children()[0];
            $(input).val('');
        }
        $(row).appendTo($(table));
    });

    $("input[name*='_delete_']").click(function(i,e){
        $(this).attr('checked', false);
        fieldname = $(this).attr("id").split("_")[0];
        rows = $(".records_row_"+fieldname).length;
        if (rows < 2) return;
        $(this).parent().parent().remove();
    });

});
});
