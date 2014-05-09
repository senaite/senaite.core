/**
 * Controller class for Analysis Service Edit view
 */
function AnalysisServiceEditView() {

    window.jarn.i18n.loadCatalog("bika");
    var _ = window.jarn.i18n.MessageFactory("bika");

    var that = this;

    var manual_fd  = $('#archetypes-fieldname-ManualEntryOfResults');
    var manual_chk = $('#archetypes-fieldname-ManualEntryOfResults #ManualEntryOfResults');
    var instre_fd  = $('#archetypes-fieldname-InstrumentEntryOfResults');
    var instr_chk  = $('#archetypes-fieldname-InstrumentEntryOfResults #InstrumentEntryOfResults');
    var methods_fd = $('#archetypes-fieldname-Methods');
    var methods_ms = $('#archetypes-fieldname-Methods #Methods');
    var method_fd  = $('#archetypes-fieldname-_Method');
    var method_sel = $('#archetypes-fieldname-_Method #_Method');
    var instrs_fd  = $('#archetypes-fieldname-Instruments');
    var instrs_ms  = $('#archetypes-fieldname-Instruments #Instruments');
    var instr_fd   = $('#archetypes-fieldname-Instrument');
    var instr_sel  = $('#archetypes-fieldname-Instrument #Instrument');
    var defcalc_chk= $('#archetypes-fieldname-UseDefaultCalculation #UseDefaultCalculation');
    var calc_fd    = $('#archetypes-fieldname-_Calculation');
    var calc_sel   = $('#archetypes-fieldname-_Calculation #_Calculation');
    var acalc_fd   = $('#archetypes-fieldname-DeferredCalculation');
    var acalc_sel  = $('#archetypes-fieldname-DeferredCalculation #DeferredCalculation');
    var interim_fd = $("#archetypes-fieldname-InterimFields");

    /**
     * Entry-point method for AnalysisServiceEditView
     */
    that.load = function() {

        // Check if there is, at least, one instrument available
        if ($(instrs_ms).find('option').length == 0) {
            // Ooops, there isn't any instrument!
            $(manual_chk).prop('checked', true);
            $(manual_chk).prop('readonly', true);
            $(instr_chk).prop('checked', false);
            $(instr_chk).prop('readonly', true);
            var errmsg = _("No instruments available");
            var title = _("Instrument entry of results option not allowed");
            var html = "<div id='no-instruments-alert' class='alert'>"+
                       "    <dt>" + errmsg + "</dt>"+
                       "    <dd>" + title + "</dd>"+
                       "</div>";
            $('#analysisservice-base-edit').before(html);
        }

        // The 'Allow instrument entry of results' value changes
        $(instr_chk).change(function() {
            if ($(this).is(':checked')) {

                // The user must select the instruments supported by
                // this Analysis Service. The default method will be
                // retrieved from the default instrument selected.

                // The user must be able to allow manual entry
                $(manual_chk).unbind("click");

                // Hide the methods multiselector
                $(methods_fd).hide();

                // Disable the default method selector
                $(method_sel).focus(function(e) {
                    $(this).blur();
                });

                // Show the instruments multiselector
                $(instrs_fd).fadeIn('slow');

                // Show the default instrument selector
                $(instr_fd).fadeIn('slow');

                // Disable the default calculation selector
                $(calc_sel).focus(function(e) {
                    $(this).blur();
                });

                // Hide the alternate calculation selector
                $(acalc_fd).hide();

                // Delegate remaining actions to Instruments change event
                $(instrs_ms).change();

            } else {

                // The method selection must be done manually, by
                // selecting the methods for which this Analysis Service
                // has support.

                // Remove the invalid instrument alert (if exists)
                $('#invalid-instruments-alert').remove();

                // The user mustn't be allowed to unset manual entry
                $(manual_chk).prop('checked', true);
                $(manual_chk).click(function(e) {
                    e.preventDefault();
                });

                // Hide the instruments multiselector
                $(instrs_fd).hide();

                // Hide the default instrument selector
                $(instr_fd).hide();

                // Show the methods multiselector
                $(methods_fd).fadeIn('slow');

                // Show the default method selector
                $(method_fd).show();
                $(method_sel).unbind("focus");

                // Delegate remaining actions to Methods change event
                $(methods_ms).change();
            }
        });

        // The methods multiselect changes
        $(methods_ms).change(function(e) {
            var prevmethod = $(method_sel).val();
            $(method_sel).find('option').remove();

            // Populate with the methods from the multi-select
            var methods = $(methods_ms).val();
            if (methods != null) {
                $.each(methods, function(index, value) {
                    var option = $(methods_ms).find('option[value="'+value+'"]').clone();
                    $(method_sel).append(option);
                });
            } else {
                $(method_sel).prepend('<option value="">'+_('None')+'</option>');
            }

            // Select the previously selected method or the first one
            defoption = $(method_sel).find('option[value="'+$(method_sel).attr('data-default')+'"]');
            if (defoption == null || defoption == '') {
                defoption = $(method_sel).find('option[value="'+prevmethod+'"]');
                if (defoption == null || defoption == '') {
                    defoption = $(method_sel).find('option').first();
                }
            }
            $(method_sel).val(defoption.val());

            // Delegate remaining actions to Method change event
            $(method_sel).change();
        });

        $(method_sel).change(function(e) {
            // Delegate actions to Default Calculation change event
            $(defcalc_chk).change();
        });


        // The instruments multiselect changes
        $(instrs_ms).change(function(e) {
            var previnstr = $(instr_sel).val();
            if ($(this).val() == null) {
                // At least one instrument must be selected
                $(this).val($(this).find('option').first().val());
            }

            // Populate the default instrument list with the selected instruments
            $(instr_sel).find('option').remove();
            var insts = $(instrs_ms).val();
            $.each(insts, function(index, value) {
                var option = $(instrs_ms).find('option[value="'+value+'"]').clone();
                $(instr_sel).append(option);
            });

            // Select the previously selected instrument or the first one
            defoption = $(instr_sel).find('option[value="'+previnstr+'"]');
            if (defoption == null || defoption == '') {
                defoption = $(instr_sel).find('option[value="'+$(instr_sel).attr('data-default')+'"]');
                if (defoption == null || defoption == '') {
                    defoption = $(instr_sel).find('option').first();
                }
            }
            $(instr_sel).val($(defoption).val());

            // Check if out-of-date or QC-fail instruments have been
            // selected.
            $('#invalid-instruments-alert').remove();
            $.each(insts, function(index, value) {
                // Is valid?
                if (value != '' && $(instr_chk).is(':checked')) {
                    var request_data = {
                        catalog_name: "uid_catalog",
                        UID: value
                    };
                    window.bika.lims.jsonapi_read(request_data, function(data) {
                        if (!$(instr_chk).is(':checked')) {
                            $('#invalid-instruments-alert').remove();
                        } else if (data.objects[0].Valid != '1') {
                            var title = data.objects[0].Title;
                            if ($('#invalid-instruments-alert').length > 0) {
                                $('#invalid-instruments-alert dd').first().append(", " + title);
                            } else {
                                var errmsg = _("Some of the selected instruments are out-of-date or with failed calibration tests");
                                var html = "<div id='invalid-instruments-alert' class='alert'>"+
                                           "    <dt>" + errmsg + ":</dt>"+
                                           "    <dd>" + title + "</dd>"+
                                           "</div>";
                                $('#analysisservice-base-edit').before(html);
                            }
                        }
                    });
                }
            });

            // Delegate remaining actions to Instrument change event
            $(instr_sel).change();

        });


        // The instrument selector changes
        $(instr_sel).change(function() {
            // Clear and disable the method list and populate with the
            // method assigned to the selected instrument
            $.ajax({
                url: window.portal_url + "/get_instrument_method",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'uid': $(instr_sel).val() },
                dataType: 'json',
                async: false
            }).done(function(data) {
                if (data != null && data['uid']) {
                    // Set the instrument's method
                    if ($(method_sel).find('option[value="'+data['uid']+'"]').length == 0) {
                        var option = '<option value="'+data['uid']+'">'+data['title']+'</option>';
                        $(method_sel).append(option);
                    }
                    $(method_sel).val(data['uid']);
                } else {
                    // Oooopps. The instrument has no method assigned
                    if ($(method_sel).find('option[value=""]').length == 0) {
                        $(method_sel).append("<option value=''>"+_("None")+"</option>");
                    }
                    $(method_sel).val('');
                }
                // Delegate the action to Default Calc change event
                $(defcalc_chk).change();
            });
        });


        // The 'Default Calculation' checkbox changes
        $(defcalc_chk).change(function() {
            $(calc_sel).find('option').remove();
            $(calc_sel).append('<option value="">'+_('None')+'</option>');

            // Hide Calculation Interims widget
            //$(interim_fd).hide();

            if ($(this).is(':checked')) {

                // Toggle default/alternative calculation
                $(acalc_fd).hide();
                $(calc_fd).show();
                $(calc_fd).prop('disabled', true);

                // Load the calculation for the selected method
                var muid = $(method_sel).val();
                if (muid != null && muid != '') {
                    // A valid method was selected
                    $.ajax({
                        url: window.portal_url + "/get_method_calculation",
                        type: 'POST',
                        data: {'_authenticator': $('input[name="_authenticator"]').val(),
                               'uid': muid },
                        dataType: 'json'
                    }).done(function(data) {
                        if (data != null && data['uid']) {
                            $(calc_sel).prepend('<option value="'+data['uid']+'">'+data['title']+'</option>');
                        }
                        $(calc_sel).val($(calc_sel).find('option').first().val());

                        // Delegate the action to Default Calculation change event
                        $(calc_sel).change();
                    });
                } else {
                    $(calc_sel).change();
                }
            } else {
                // Toggle default/alternative calculation
                $(calc_fd).hide();
                $(acalc_fd).show();

                // Delegate the action to Alternative Calculation change event
                $(acalc_sel).change();
            }
        });

        // The 'Default calculation' changes
        $(calc_sel).change(function() {
            loadInterims($(this).val());
        });

        // The 'Alternative calculation' changes
        $(acalc_sel).change(function() {
            loadInterims($(this).val());
        });

        // Apply default styling
        applyStyles();

        // Grab original values
        catchOriginalValues();

        // Apply the behavior
        $(instr_chk).change();
    }

    function catchOriginalValues() {
        $(manual_chk).attr('data-default', $(manual_chk).is(':checked'));
        $(instr_chk).attr('data-default', $(instr_chk).is(':checked'));
        $(methods_ms).attr('data-default', $(methods_ms).val());
        $(method_sel).attr('data-default', $(method_sel).val());
        $(instrs_ms).attr('data-default', $(instrs_ms).val());
        $(instr_sel).attr('data-default', $(instr_sel).val());
        $(defcalc_chk).attr('data-default', $(defcalc_chk).is(':checked'));
        $(calc_sel).attr('data-default', $(calc_sel).val());
        $(acalc_sel).attr('data-default', $(acalc_sel).val());

        // Remove 'None' option from 'Methods' multi-select
        $(methods_ms).find('option[value=""]').remove();

        // Disable the default calculation selector
        $(calc_sel).focus(function(e) {
            $(this).blur();
        });

        // Toggle default/alternative calculation
        if ($(defcalc_chk).is(':checked')) {
            $(acalc_fd).hide();
            $(calc_fd).show();
        } else {
            $(calc_fd).hide();
            $(acalc_fd).show();
        }
    }

    /**
     * Loads the Interim fields Widget for the specificied calculation
     */
    function loadInterims(calcuid) {
        $(interim_fd).hide();
        var rows, i;
        if (calcuid == null || calcuid == ""){
            $("#InterimFields_more").click(); // blank last row
            rows = $("tr.records_row_InterimFields"); // Clear the rest
            if($(rows).length > 1){
                for (i = $(rows).length - 2; i >= 0; i--) {
                    $($(rows)[i]).remove();
                }
            }
            $(interim_fd).hide();
            return;
        }
        var request_data = {
            catalog_name: "bika_setup_catalog",
            UID: calcuid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
            // Clear rows
            var rows, i;
            $("#InterimFields_more").click(); // blank last row
            rows = $("tr.records_row_InterimFields");
            var originals = [];
            if($(rows).length > 1){
                for (i = $(rows).length - 2; i >= 0; i--) {
                    // Save the original values
                    var keyword = $($($(rows)[i]).find('td input')[0]).val();
                    if (keyword != '') {
                        var value = $($($(rows)[i]).find('td input')[2]).val();
                        var unit = $($($(rows)[i]).find('td input')[3]).val();
                        var hidd = $($($(rows)[i]).find('td input')[4]).is(':checked');
                        var wide = $($($(rows)[i]).find('td input')[5]).is(':checked');
                        originals.push([keyword, value, unit, hidd, wide]);
                    }
                    $($(rows)[i]).remove();
                }
            }
            if (data.objects.length > 0) {
                $(interim_fd).fadeIn('slow');
                $("[id^='InterimFields-keyword-']").attr("id", "InterimFields-keyword-0");
                $("[id^='InterimFields-title-']").attr("id", "InterimFields-title-0");
                $("[id^='InterimFields-value-']").attr("id", "InterimFields-value-0");
                $("[id^='InterimFields-unit-']").attr("id", "InterimFields-unit-0");

                for (i = 0; i < data.objects[0].InterimFields.length; i++) {
                    var row = data.objects[0].InterimFields[i];
                    var original = null;
                    for (j = 0; j < originals.length; j++) {
                        if (originals[j][0] == row.keyword) {
                            original = originals[j]; break;
                        }
                    }
                    $("#InterimFields-keyword-"+i).val(row.keyword);
                    $("#InterimFields-title-"+i).val(row.title);
                    if (original == null) {
                        $("#InterimFields-value-"+i).val(row.value);
                        $("#InterimFields-unit-"+i).val(row.unit);
                    } else {
                        $("#InterimFields-value-"+i).val(original[1]);
                        $("#InterimFields-unit-"+i).val(original[2]);
                    }
                    $("#InterimFields_more").click();
                }
            }
        });
    }


    /**
     * Checks if the selected instruments aren't out-of-date and their
     * latest Internal Calibration Tests are valid. If an invalid
     * instrument gets selected, shows an alert to the user
     */
    function validateInstruments() {
        $('#invalid-instruments-alert').remove();
        if ($('#InstrumentEntryOfResults').is(':checked')) {
            window.jarn.i18n.loadCatalog("bika");
            var _ = window.jarn.i18n.MessageFactory("bika");
            var insts = $('#Instruments').val() ? $('#Instruments').val() : [];
            $.each(insts, function(index, value) {
                // Is valid?
                var request_data = {
                    catalog_name: "uid_catalog",
                    UID: value
                };
                window.bika.lims.jsonapi_read(request_data, function(data) {
                    if (data.objects[0].Valid != '1') {
                        var title = data.objects[0].Title;
                        if ($('#invalid-instruments-alert').length > 0) {
                            $('#invalid-instruments-alert dd').first().append(", " + title);
                        } else {
                            var errmsg = _("Some of the selected instruments are out-of-date or with failed calibration tests");
                            var html = "<div id='invalid-instruments-alert' class='alert'>"+
                                       "    <dt>" + errmsg + ":</dt>"+
                                       "    <dd>" + title + "</dd>"+
                                       "</div>";
                            $('#analysisservice-base-edit').before(html);
                        }
                    }
                });
            });
        } else {
            loadEmptyInstrument();
        }
    }


    function applyStyles() {
        $(instrs_fd)
            .css('border', '1px solid #cfcfcf')
            .css('border-bottom', 'none')
            .css('background-color', '#efefef')
            .css('padding', '10px')
            .css('margin-bottom', '0px');
        $(instr_fd)
            .css('border', '1px solid #cfcfcf')
            .css('border-top', 'none')
            .css('background-color', '#efefef')
            .css('padding', '10px');

        $(acalc_fd).find('label').hide();
        $(calc_fd).find('label').hide();
    }
}
