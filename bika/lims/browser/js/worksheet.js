(function( $ ) {
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');

    // selecting a template might pre-select the instrument
    $(".template").change(function(){
        templateinstruments = $.parseJSON($(".templateinstruments").val());
        instrUID = templateinstruments[$(this).val()];
        instrList = $(".instrument")[0];
        if (instrUID != ""){
            for (i=0;i<=instrList.length;i++){
                if (instrList.options[i].value == instrUID){
                    instrList.selectedIndex = i;
                    $(instrList).change()
                }
            }
        }
    });

    // search form - selecting a category fills up the service selector
    $('[name="list_getCategoryTitle"]').live("change", function(){
        val = $('[name="list_getCategoryTitle"]').val();
        if(val == 'any'){
            $('[name="list_Title"]').empty();
            $('[name="list_Title"]').append("<option value='any'>"+_('Any')+"</option>");
            return;
        }
        $.ajax({
            url: window.location.href.split("?")[0].replace("/add_analyses","") + "/getServices",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'getCategoryTitle': val},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                current_service_selection = $('[name="list_Title"]').val();
                $('[name="list_Title"]').empty();
                $('[name="list_Title"]').append("<option value='any'>"+_('Any')+"</option>");
                for(i=0; i<data.length; i++){
                    if (data[i] == current_service_selection){
                        selected = 'selected="selected" ';
                    } else {
                        selected = '';
                    }
                    $('[name="list_Title"]').append("<option "+selected+"value='"+data[i]+"'>"+data[i]+"</option>");
                }
            }
        });
    });
    $('[name="list_getCategoryTitle"]').trigger("change");

    // adding Controls and Blanks - selecting services re-renders the list
    // of applicable reference samples
    function get_updated_controls(){
        selected_service_uids = [];
        $.each($("input:checked"), function(i,e){
            selected_service_uids.push($(e).val());
        });

        if (window.location.href.search('add_control') > -1) {
          control_type = 'c';
        } else {
          control_type = 'b';
        }

        url = window.location.href
            .replace("/add_blank", "")
            .replace("/add_control", "") + "/getWorksheetReferences"
        element = $("#worksheet_add_references");
        if(element.length > 0){
            $(element).load(url,
                {'service_uids': selected_service_uids.join(","),
                 'control_type': control_type,
                 '_authenticator': $('input[name="_authenticator"]').val()},
                function(responseText, statusText, xhr, $form) {
                }
            );
        };
    };
    $("#worksheet_services input[id*='_cb_']").live('click', function(){
        get_updated_controls();
    });
    // get references for selected services on first load
    get_updated_controls();

    // click a Reference Sample in add_control or add_blank
    $("#worksheet_add_references .bika-listing-table tbody.item-listing-tbody tr").live('click', function(e){
        // we want to submit to the worksheet.py/add_control or add_blank views.
        if (e.target.src != undefined) {
            return;
        }
        if(window.location.href.search('add_control') > -1){
            $(this).parents('form').attr("action", "add_control");
        } else {
            $(this).parents('form').attr("action", "add_blank");
        }
        // tell the form handler which services were selected
        selected_service_uids = [];
        $.each($("input:checked"), function(i,e){
            selected_service_uids.push($(e).val());
        });
        ssuids = selected_service_uids.join(",");
        $(this).parents('form').append("<input type='hidden' value='"+ssuids+"' name='selected_service_uids'/>");
        // tell the form handler which reference UID was clicked
        $(this).parents('form').append("<input type='hidden' value='"+$(this).attr("uid")+"' name='reference_uid'/>");
        // add the position dropdown's value to the form before submitting.
        $(this).parents('form').append("<input type='hidden' value='"+$('#position').val()+"' name='position'/>");
        $(this).parents('form').submit();
    });

    // click an AR in add_duplicate
    $("#worksheet_add_duplicate_ars .bika-listing-table tbody.item-listing-tbody tr").live('click', function(){
        // we want to submit to the worksheet.py/add_duplicate view.
        $(this).parents('form').attr("action", "add_duplicate");
        // add the position dropdown's value to the form before submitting.
        $(this).parents('form')
            .append("<input type='hidden' value='"+$(this).attr("uid")+"' name='ar_uid'/>")
            .append("<input type='hidden' value='"+$('#position').val()+"' name='position'/>");
        $(this).parents('form').submit();
    })

    // add_analyses analysis search is handled by bika_listing default __call__
    $('.ws-analyses-search-button').live('click', function(event) {
        // in this context we already know there is only one bika-listing-form
        form_id = "list";
        form = $("#list");

        // request new table content by re-routing bika_listing_table form submit
        stored_form_action = $(form).attr("action");
        $(form).attr("action", window.location.href);
        $(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");

        // dropdowns are printed in ../templates/worksheet_add_analyses.pt
        // We add list_<bika_analysis_catalog args>, which go
        // into contentFilter in bika_listing.py
        getCategoryTitle = $("[name='list_getCategoryTitle']").val();
        Title = $("[name='list_Title']").val();
        getClientTitle = $("[name='list_getClientTitle']").val();
        if (getCategoryTitle != 'any')
            $(form).append("<input type='hidden' name='list_getCategoryTitle' value='"+getCategoryTitle+"'>");
        if (Title != 'any')
            $(form).append("<input type='hidden' name='list_Title' value='"+Title+"'>");
        if (getClientTitle != 'any')
            $(form).append("<input type='hidden' name='list_getClientTitle' value='"+getClientTitle+"'>");

        options = {
            target: $('.bika-listing-table'),
            replaceTarget: true,
            data: form.formToArray(),
            success: function(){
            }
        }
        form.ajaxSubmit(options);

        $("[name='table_only']").remove();
        $("#list > [name='list_getCategoryTitle']").remove();
        $("#list > [name='list_Title']").remove();
        $("#list > [name='list_getClientTitle']").remove();
        $(form).attr("action", stored_form_action);
        return false;
    });

    function portalMessage(message) {
        _ = jarn.i18n.MessageFactory('bika');
        str = "<dl class='portalMessage info'>"+
            "<dt>"+_('Info')+"</dt>"+
            "<dd><ul>" + _(message) +
            "</ul></dd></dl>";
        $('.portalMessage').remove();
        $(str).appendTo('#viewlet-above-content');
    }

    $(".manage_results_header .analyst").change(function(){
        if ($(this).val() == '') {
            return false;
        }
        $.ajax({
          type: 'POST',
          url: window.location.href.replace("/manage_results", "") + "/setAnalyst",
          data: {'value': $(this).val(),
                 '_authenticator': $('input[name="_authenticator"]').val()},
          success: function(data, textStatus, jqXHR){
               portalMessage("Changes saved.");
          }
        });
    });

    $(".manage_results_header .instrument").change(function(){
        $("#content-core .instrument-error").remove();
        if ($(this).val() == '') {
            return false;
        }
        $.ajax({
          type: 'POST',
          url: window.location.href.replace("/manage_results", "") + "/set_instrument",
          data: {'value': $(this).val(),
                  '_authenticator': $('input[name="_authenticator"]').val()},
          success: function(data, textStatus, jqXHR){
               portalMessage("Changes saved.");
               /* TODO: refresh all the Analysis-Instrument selectors for all the analyses
                of the worksheet table*/
          },
          error: function(data, jqXHR, textStatus, errorThrown){
                $(".manage_results_header .instrument")
                    .closest("table")
                    .after("<div class='alert instrument-error'>" +
                        _("Unable to apply the selected instrument") + "</div>");
                return false;
          }
        });
    });

    // Manage the upper selection form for spread wide interim results values
    $("#wideinterims_analyses").change(function(){
        $("#wideinterims_interims").html('');
        $('input[id^="wideinterim_'+$(this).val()+'"]').each(function(i, obj) {
            itemval = '<option value="'+ $(obj).attr('keyword') +'">'+$(obj).attr('name')+'</option>';
            $("#wideinterims_interims").append(itemval);
        });
    });
    $("#wideinterims_interims").change(function(){
        analysis = $("#wideinterims_analyses").val();
        interim = $(this).val();
        idinter = "#wideinterim_"+analysis+"_"+interim;
        $("#wideinterims_value").val($(idinter).val());
    });
    $("#wideinterims_apply").click(function(event) {
            event.preventDefault();
            analysis=$("#wideinterims_analyses").val();
            interim=$("#wideinterims_interims").val();
            $('tr[keyword="'+analysis+'"] input[field="'+interim+'"]').each(function(i, obj) {
                if ($('#wideinterims_empty').is(':checked')) {
                    if ($(this).val()=='' || $(this).val().match(/\d+/)=='0') {
                        $(this).val($('#wideinterims_value').val());
                        $(this).change();
                    }
                } else {
                    $(this).val($('#wideinterims_value').val());
                    $(this).change();
                }
            });
    });

    // Change the instruments to be shown for an analysis when the method selected changes
    $('table.bika-listing-table select.listing_select_entry[field="Method"]').change(function() {
        var muid = $(this).val();
        if (muid) {
            // Update the instruments selector
            $(this).closest('tr').find('img.alert-instruments-invalid').remove();
            var instrselector = $(this).closest('tr').find('select.listing_select_entry[field="Instrument"]');
            var selectedinstr = $(instrselector).val();
            $(instrselector).find('option').remove();
            // Get the available instruments for the method
            $.ajax({
                url: window.portal_url + "/get_method_instruments",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'uid': muid },
                dataType: 'json'
            }).done(function(data) {
                var invalid = []
                var valid = false;
                $.each(data, function(index, value) {
                    if (value['isvalid'] == true) {
                        var selected = "";
                        if (selectedinstr == value['uid']) {
                            selected = "selected";
                        }
                        $(instrselector).append('<option value="'+value['uid']+'" '+selected+'>'+value['title']+'</option>');
                        valid = true;
                    } else {
                        invalid.push(value['title'])
                    }
                });
                if (!valid) {
                    $(instrselector).append('<option selected value=""></option>');
                }
                if (invalid.length > 0) {
                    var title = _("Invalid instruments are not shown: ")+invalid.join(", ");
                    $(instrselector).parent().append('<img class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/warning.png" title="'+title+'")">');
                }
            }).fail(function() {
                $(instrselector).append('<option selected value=""></option>');
            });

        } else {
            // Clear instruments selector
            $(instrselector).find('option').remove();
            $(instrselector).append('<option selected value=""></option>');
        }
    });
    // Remove empty options
    $('table.bika-listing-table select.listing_select_entry[field="Method"]').find('option[value=""]').remove();
    $('table.bika-listing-table select.listing_select_entry[field="Method"]').change();


});
}(jQuery));
