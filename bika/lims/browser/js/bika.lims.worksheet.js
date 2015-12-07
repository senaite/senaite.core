/**
 * Controller class for Worksheets Folder
 */
function WorksheetFolderView() {

    var that = this;

    that.load = function() {

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

        $('div.worksheet_add_controls select.instrument').change(function() {
            var val = $(this).val();
            $('div.worksheet_add_controls div.alert').remove();
            if (val != '' && val != null) {
                $('div.worksheet_add_controls').append('<div class="alert">'+_("Only the analyses for which the selected instrument is allowed will be added automatically.")+'</div>');
            }
        });
    }
}

/**
 * Controller class for Worksheet's add analyses view
 */
function WorksheetAddAnalysesView() {

    var that = this;

    that.load = function() {

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

        // add_analyses analysis search is handled by bika_listing default __call__
        $('.ws-analyses-search-button').live('click', function (event) {
            // in this context we already know there is only one bika-listing-form
            var form_id = "list";
            var form = $("#list");

            // request new table content by re-routing bika_listing_table form submit
            $(form).append("<input type='hidden' name='table_only' value='" + form_id + "'>");
            // dropdowns are printed in ../templates/worksheet_add_analyses.pt
            // We add <formid>_<index>=<value>, which are checked in bika_listing.py
            var filter_indexes = ['getCategoryTitle', 'Title', 'getClientTitle'];
            var i, fi;
            for (i = 0; i < filter_indexes.length; i++) {
                fi = form_id + "_" + filter_indexes[i];
                var value = $("[name='" + fi + "']").val();
                if (value == undefined || value == null || value == 'any') {
                    $("#list > [name='" + fi + "']").remove();
                    $.query.REMOVE(fi);
                }
                else {
                    $(form).append("<input type='hidden' name='" + fi + "' value='" + value + "'>");
                    $.query.SET(fi, value);
                }
            }

            var options = {
                target: $('.bika-listing-table'),
                replaceTarget: true,
                data: form.formToArray(),
                success: function () {
                }
            }
            var url = window.location.href.split("?")[0].split("/add_analyses")[0];
            url = url + "/add_analyses" + $.query.toString();
            window.history.replaceState({}, window.document.title, url);

            var stored_form_action = $(form).attr("action");
            $(form).attr("action", window.location.href);
            form.ajaxSubmit(options);

            for (i = 0; i < filter_indexes.length; i++) {
                fi = form_id + "_" + filter_indexes[i];
                $("#list > [name='" + fi + "']").remove();
            }
            $(form).attr("action", stored_form_action);
            $("[name='table_only']").remove();

            return false;
        });
    }
}

/**
 * Controller class for Worksheet's add blank/control views
 */
function WorksheetAddQCAnalysesView() {

    var that = this;

    that.load = function() {

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
    }

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

        url = window.location.href.split("?")[0]
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
}

/**
 * Controller class for Worksheet's add blank/control views
 */
function WorksheetAddDuplicateAnalysesView() {

    var that = this;

    that.load = function() {

        // click an AR in add_duplicate
        $("#worksheet_add_duplicate_ars .bika-listing-table tbody.item-listing-tbody tr").live('click', function(){
            // we want to submit to the worksheet.py/add_duplicate view.
            $(this).parents('form').attr("action", "add_duplicate");
            // add the position dropdown's value to the form before submitting.
            $(this).parents('form')
                .append("<input type='hidden' value='"+$(this).attr("uid")+"' name='ar_uid'/>")
                .append("<input type='hidden' value='"+$('#position').val()+"' name='position'/>");
            $(this).parents('form').submit();
        });
    }

}


/**
 * Controller class for Worksheet's manage results view
 */
function WorksheetManageResultsView() {

    var that = this;

    that.load = function() {

        // Remove empty options
        initializeInstrumentsAndMethods();

        loadHeaderEventsHandlers();

        loadMethodEventHandlers();

        // Manage the upper selection form for spread wide interim results values
        loadWideInterimsEventHandlers();

        loadRemarksEventHandlers();

        loadDetectionLimitsEventHandlers();
    }

    function portalMessage(message) {
        window.jarn.i18n.loadCatalog("bika");
        _ = jarn.i18n.MessageFactory('bika');
        str = "<dl class='portalMessage info'>"+
            "<dt>"+_('Info')+"</dt>"+
            "<dd><ul>" + message +
            "</ul></dd></dl>";
        $('.portalMessage').remove();
        $(str).appendTo('#viewlet-above-content');
    }

    function loadRemarksEventHandlers() {
        // Add a baloon icon before Analyses' name when you'd add a remark. If you click on, it'll display remarks textarea.
        var txt1 = '<a href="#" class="add-remark"><img src="'+window.portal_url+'/++resource++bika.lims.images/comment_ico.png" title="'+_('Add Remark')+'")"></a>';
        var pointer = $(".listing_remarks:contains('')").closest('tr').prev().find('td.service_title span.before');
        $(pointer).append(txt1);

        $("a.add-remark").click(function(e){
            e.preventDefault();
            var rmks = $(this).closest('tr').next('tr').find('td.remarks');
            if (rmks.length > 0) {
                rmks.toggle();
            }
        });
        $("a.add-remark").click();
    }

    function loadDetectionLimitsEventHandlers() {
        $('select[name^="DetectionLimit."]').change(function() {
            var defdls = $(this).closest('td').find('input[id^="DefaultDLS."]').first().val();
            var resfld = $(this).closest('tr').find('input[name^="Result."]')[0];
            var uncfld = $(this).closest('tr').find('input[name^="Uncertainty."]');
            defdls = $.parseJSON(defdls);
            $(resfld).prop('readonly', !defdls.manual);
            if ($(this).val() == '<') {
                $(resfld).val(defdls['min']);
                // Inactivate uncertainty?
                if (uncfld.length > 0) {
                    $(uncfld).val('');
                    $(uncfld).prop('readonly', true);
                    $(uncfld).closest('td').children().hide();
                }
            } else if ($(this).val() == '>') {
                $(resfld).val(defdls['max']);
                // Inactivate uncertainty?
                if (uncfld.length > 0) {
                    $(uncfld).val('');
                    $(uncfld).prop('readonly', true);
                    $(uncfld).closest('td').children().hide();
                }
            } else {
                $(resfld).val('');
                $(resfld).prop('readonly',false);
                // Activate uncertainty?
                if (uncfld.length > 0) {
                    $(uncfld).val('');
                    $(uncfld).prop('readonly', false);
                    $(uncfld).closest('td').children().show();
                }
            }
            // Maybe the result is used in calculations...
            $(resfld).change();
        });
        $('select[name^="DetectionLimit."]').change();
    }

    function loadWideInterimsEventHandlers() {
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
    }

    function initializeInstrumentsAndMethods() {
        var instrumentsels = $('table.bika-listing-table select.listing_select_entry[field="Instrument"]');
        $(instrumentsels).each(function() {
            var sel = $(this).val();
            if ($(this).find('option[value=""]').length > 0) {
                $(this).find('option[value=""]').remove();
                $(this).prepend('<option value="">'+_('None')+'</option>');
            }
            $(this).val(sel);
        });
        var methodsels = $('table.bika-listing-table select.listing_select_entry[field="Method"]');
        $(methodsels).each(function() {
            var sel = $(this).val();
            if ($(this).find('option[value=""]').length > 0) {
                $(this).find('option[value=""]').remove();
                $(this).prepend('<option value="">'+_('Not defined')+'</option>');
            }
            $(this).val(sel);
        });
    }

    function loadHeaderEventsHandlers() {
        $(".manage_results_header .analyst").change(function(){
            if ($(this).val() == '') {
                return false;
            }
            $.ajax({
              type: 'POST',
              url: window.location.href.replace("/manage_results", "") + "/set_analyst",
              data: {'value': $(this).val(),
                     '_authenticator': $('input[name="_authenticator"]').val()},
              success: function(data, textStatus, jqXHR){
                   window.jarn.i18n.loadCatalog("plone");
                   _p = jarn.i18n.MessageFactory('plone');
                   portalMessage(_p("Changes saved."));
              }
            });
        });

        // Change the results layout
        $("#resultslayout_form #resultslayout_button").hide();
        $("#resultslayout_form #resultslayout").change(function() {
            $("#resultslayout_form #resultslayout_button").click();
        });

        $(".manage_results_header .instrument").change(function(){
            $("#content-core .instrument-error").remove();
            var instruid = $(this).val();
            if (instruid == '') {
                return false;
            }
            $.ajax({
              type: 'POST',
              url: window.location.href.replace("/manage_results", "") + "/set_instrument",
              data: {'value': instruid,
                      '_authenticator': $('input[name="_authenticator"]').val()},
              success: function(data, textStatus, jqXHR){
                   window.jarn.i18n.loadCatalog("plone");
                   _p = jarn.i18n.MessageFactory('plone');
                   portalMessage(_p("Changes saved."));
                   // Set the selected instrument to all the analyses which
                   // that can be done using that instrument. The rest of
                   // of the instrument picklist will not be changed
                   $('select.listing_select_entry[field="Instrument"] option[value="'+instruid+'"]').parent().find('option[value="'+instruid+'"]').prop("selected", false);
                   $('select.listing_select_entry[field="Instrument"] option[value="'+instruid+'"]').prop("selected", true);
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
    }

    /**
     * Change the instruments to be shown for an analysis when the method selected changes
     */
    function loadMethodEventHandlers() {
        $('table.bika-listing-table select.listing_select_entry[field="Method"]').change(function() {
            var method = null;
            var service = null;
            var muid = $(this).val();
            var auid = $(this).attr('uid');
            var suid = $(this).attr('as_uid');
            var instrselector = $('select.listing_select_entry[field="Instrument"][uid="'+auid+'"]');
            var selectedinstr = $(instrselector).val();
            var m_manualentry = true;
            var s_instrentry  = false;
            var qc_analysis = $(this).closest('tr').hasClass('qc-analysis');
            $(instrselector).find('option').remove();
            $(instrselector).prop('disabled', false);
            $('img.alert-instruments-invalid[uid="'+auid+'"]').remove();
            $('.interim input[uid="'+auid+'"]').prop('disabled', false);
            $('.input[field="Result"][uid="'+auid+'"]').prop('disabled', false);

            if (muid != '') {
                // Update the instruments selector, but only if the service has AllowInstrumentEntryOfResults enabled.
                // Also, only update with those instruments available for the Analysis Service. If any of the method
                // instruments are available for that Analysis Service, check if the method allows the manual entry
                // of results.

                // Is manual entry allowed for this method?
                var request_data = {
                    catalog_name: "uid_catalog",
                    UID: muid,
                    include_fields: ['ManualEntryOfResultsViewField', 'Title']
                };
                window.bika.lims.jsonapi_read(request_data, function(data) {
                    method = (data.objects && data.objects.length > 0) ? data.objects[0] : null;
                    m_manualentry = (method != null) ? method.ManualEntryOfResultsViewField : true;
                    $('.interim input[uid="'+auid+'"]').prop('disabled', !m_manualentry);
                    $('.input[field="Result"][uid="'+auid+'"]').prop('disabled', !m_manualentry);
                    if (!m_manualentry) {
                        // This method doesn't allow the manual entry of Results
                        var title = _("Manual entry of results for method ${methodname} is not allowed", {methodname: method.Title});
                        $('.input[field="Result"][uid="'+auid+'"]').parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/warning.png" title="'+title+'")">');
                    }

                    // Has the Analysis Service the 'Allow Instrument Entry of Results' enabled?
                    var request_data = {
                        catalog_name: "uid_catalog",
                        UID: suid,
                        include_fields: ['InstrumentEntryOfResults']
                    };
                    window.bika.lims.jsonapi_read(request_data, function(asdata) {
                        service = (asdata.objects && asdata.objects.length > 0) ? asdata.objects[0] : null;
                        s_instrentry = (service != null) ? service.InstrumentEntryOfResults : false;
                        if (!s_instrentry) {
                            // The service doesn't allow instrument entry of results.
                            // Set instrument selector to None and hide it
                            $(instrselector).append("<option value=''>"+_("None")+"</option>");
                            $(instrselector).val('');
                            $(instrselector).hide();
                            return;
                        }

                        // Get the available instruments for this method and analysis service
                        $(instrselector).show();
                        $.ajax({
                            url: window.portal_url + "/get_method_service_instruments",
                            type: 'POST',
                            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                                   'muid': muid,
                                   'suid': suid },
                            dataType: 'json'
                        }).done(function(idata) {
                            var invalid = []
                            var valid = false;

                            // Populate the instrument selector with the instruments retrieved
                            $.each(idata, function(index, value) {
                                if (value['isvalid'] == true || qc_analysis == true) {
                                    $(instrselector).append('<option value="'+value['uid']+'">'+value['title']+'</option>');
                                    if (selectedinstr == value['uid']) {
                                        $(instrselector).val(value['uid'])
                                    }
                                    valid = true;
                                } else {
                                    invalid.push(value['title'])
                                }
                            });

                            if (!valid) {
                                // There isn't any valid instrument found
                                $(instrselector).append('<option value="">'+_('None')+'</option>');
                                $(instrselector).val('');

                            } else if (m_manualentry) {
                                // Some valid instruments found and Manual Entry of Results allowed
                                $(instrselector).prepend('<option value="">'+_('None')+'</option>');

                            }

                            if (invalid.length > 0) {
                                // At least one instrument is invalid (out-of-date or qc-fail)

                                if (valid) {
                                    // At least one instrument valid found too
                                    var title = _("Invalid instruments are not shown: ${invalid_list}", {invalid_list: invalid.join(", ")});
                                    $(instrselector).parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/warning.png" title="'+title+'")">');

                                } else if (m_manualentry) {
                                    // All instruments found are invalid, but manual entry is allowed
                                    var title = _("No valid instruments found: ${invalid_list}", {invalid_list: invalid.join(", ")});
                                    $(instrselector).parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/exclamation.png" title="'+title+'")">');

                                } else {
                                    // All instruments found are invalid and manual entry not allowed
                                    var title = _("Manual entry of results for method {methodname} is not allowed and no valid instruments found: ${invalid_list}",
                                                  {methodname:  method.Title, invalid_list:invalid.join(", ")});
                                    $(instrselector).parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/exclamation.png" title="'+title+'")">');
                                    $('.interim input[uid="'+auid+'"]').prop('disabled', true);
                                    $('.input[field="Result"][uid="'+auid+'"]').prop('disabled', true);
                                }
                            }

                        }).fail(function() {
                            $(instrselector).append('<option value="">'+_('None')+'</option>');
                            $(instrselector).val("");
                            if (!m_manualentry) {
                                var title = _("Unable to load instruments: ${invalid_list}", {invalid_list: invalid.join(", ")});
                                $(instrselector).parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/exclamation.png" title="'+title+'")">');
                                $(instrselector).prop('disabled', true);
                            } else {
                                $(instrselector).prop('disabled', false);
                            }
                        });

                    });
                });

            } else {
                // No method selected. Which are the instruments assigned to the analysis service and without any method assigned?
                $.ajax({
                    url: window.portal_url + "/get_method_service_instruments",
                    type: 'POST',
                    data: {'_authenticator': $('input[name="_authenticator"]').val(),
                           'muid': '0',
                           'suid': suid },
                    dataType: 'json'
                }).done(function(idata) {
                    var invalid = []
                    var valid = false;

                    // Populate the instrument selector with the instruments retrieved
                    $.each(idata, function(index, value) {
                        if (value['isvalid'] == true) {
                            $(instrselector).append('<option value="'+value['uid']+'">'+value['title']+'</option>');
                            if (selectedinstr == value['uid']) {
                                $(instrselector).val(value['uid'])
                            }
                            valid = true;
                        } else {
                            invalid.push(value['title'])
                        }
                    });

                    if (!valid) {
                        // There isn't any valid instrument found
                        $(instrselector).append('<option value="">'+_('None')+'</option>');
                        $(instrselector).val('');
                    } else {
                        // Some valid instruments found and Manual Entry of Results allowed
                        $(instrselector).prepend('<option value="">'+_('None')+'</option>');
                    }

                    if (invalid.length > 0) {
                        // At least one instrument is invalid (out-of-date or qc-fail)
                        if (valid) {
                            // At least one instrument valid found too
                            var title = _("Invalid instruments are not shown: ${invalid_list}", {invalid_list: invalid.join(", ")});
                            $(instrselector).parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/warning.png" title="'+title+'")">');
                        } else {
                            // All instruments found are invalid
                            var title = _("No valid instruments found: ${invalid_list}", {invalid_list: invalid.join(", ")});
                            $(instrselector).parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/exclamation.png" title="'+title+'")">');
                        }
                    }
                }).fail(function() {
                    $(instrselector).append('<option value="">'+_('None')+'</option>');
                    $(instrselector).val('');
                    var title = _("Unable to load instruments: ${invalid_list}", {invalid_list: invalid.join(", ")});
                    $(instrselector).parent().append('<img uid="'+auid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/exclamation.png" title="'+title+'")">');
                    $(instrselector).prop('disabled', true);
                });
            }
        });
    }
}
