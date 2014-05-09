jQuery(function($){
    $(document).ready(function(){
        window.jarn.i18n.loadCatalog("plone");
        _p = jarn.i18n.MessageFactory('plone');
        window.jarn.i18n.loadCatalog("bika");
        _ = jarn.i18n.MessageFactory('bika');

        recordswidget_lookups();
        recordswidget_loadEventHandlers();

    });
});

function recordswidget_lookups(elements){
    if(elements == undefined){
        var inputs = $(".ArchetypesRecordsWidget [combogrid_options]").not('.has_combogrid_widget');
    } else {
        var inputs = elements;
    }
    for (var i = inputs.length - 1; i >= 0; i--) {
        var element = inputs[i];
        var options = $.parseJSON($(element).attr('combogrid_options'));
        if(options == '' || options == undefined || options == null){
            continue;
        }
        options.select = function(event, ui){
            event.preventDefault();
            // Set value in activated element (must exist in colModel!)
            var fieldName = $(this).attr('name').split(".")[0];
            var key = "";
            if ($(this).attr('name').split(".").length > 1) {
            	key = $(this).attr('name').split(".")[1].split(":")[0];
            }
            row_nr = parseInt(this.id.split("-")[2]);
            $(this).val(ui.item[key]);
            // Set values if colModel matches recordswidget subfield name
            var colModel = $.parseJSON($(this).attr('combogrid_options')).colModel;
            for (var i = colModel.length - 1; i >= 0; i--) {
                var colname = colModel[i]['columnName'];
                if (colname != key) {
                    var element = $('#'+fieldName+'-'+colname+'-'+row_nr);
                    if(element.length == 1){
                        $(element).val(ui.item[colname]);
                    }
                }
            }
        };
        if(window.location.href.search("portal_factory") > -1){
            options.url = window.location.href.split("/portal_factory")[0] + "/" + options.url;
        }
        options.url = options.url + '?_authenticator=' + $('input[name="_authenticator"]').val();
        $(element).combogrid(options);
    };
}

function recordswidget_loadEventHandlers(elements) {
    $('.ArchetypesRecordsWidget [combogrid_options]').live('focus', function(){
        /*if ($(this).hasClass('has_combogrid_widget')) {
            return;
        }*/
        var options = $.parseJSON($(this).attr('combogrid_options'));
        if(options != '' && options != undefined && options != null){
            // For inputs with combogrids, we want them to clear when focused
            $(this).val('');
            // We also want to clear all colModel->subfield completions
            var fieldName = $(this).attr('name').split(".")[0];
            var key = "";
            if ($(this).attr('name').split(".").length > 1) {
                key = $(this).attr('name').split(".")[1].split(":")[0];
            }
            var colModel = $.parseJSON($(this).attr('combogrid_options')).colModel;
            row_nr = parseInt(this.id.split("-")[2]);
            for (var i = colModel.length - 1; i >= 0; i--) {
                var colname = colModel[i]['columnName'];
                if (colname != key) {
                    var element = $('#'+fieldName+'-'+colname+'-'+row_nr);
                    if(element.length == 1){
                        $(element).val('');
                    }
                }
            }
        }
    });

    $("input[id$='_more']").click(function(i,e){
        var fieldname = $(this).attr("id").split("_")[0];
        var table = $('#'+fieldname+"_table");
        var rows = $(".records_row_"+fieldname);
        // clone last row
        var row = $(rows[rows.length-1]).clone();
        // after cloning, make sure the new element's IDs are unique
        var found = $(row).find("input[id^='"+fieldname+"']");
        for (var i = found.length - 1; i >= 0; i--) {
            var ID = found[i].id;
            var prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
            var nr = parseInt(ID.split("-")[2]) + 1;
            $(found[i]).attr('id', prefix + "-" + nr);
        };
        // First check to see that all required subfields are completed,
        // before allowing a new row to be added
        for (var i = found.length - 1; i >= 0; i--) {
            var e = found[i];
            var required = $(e).hasClass('required');
            var val = $(e).val();
            if (required && val == ""){
                window.bika.lims.portalMessage(e.id.split("-")[1] + ": " + _p("Input is required but not given."));
                return false;
            }
        };
        // clear values
        for(i=0; i<$(row).children().length; i++){
            var td = $(row).children()[i];
            var input = $(td).children()[0];
            $(input).val('');
            $(input).removeClass("hasDatepicker");
        }
        $(row).appendTo($(table));
        recordswidget_lookups($(row).find('[combogrid_options]'));
    });

    $(".rw_deletebtn").live('click', function(i,e){
        var row = $(this).parent().parent();
        var siblings = $(row).siblings();
        if (siblings.length < 2) return;
        $(this).parent().parent().remove();
    });
}
