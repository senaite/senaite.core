/**
 * Controller class for Analysis Service Edit view
 */
function AnalysisServiceEditView() {

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
    var interim_rw = $("#archetypes-fieldname-InterimFields tr.records_row_InterimFields");
    var ldsel_chk  = $('#archetypes-fieldname-DetectionLimitSelector #DetectionLimitSelector');
    var ldman_fd   = $('#archetypes-fieldname-AllowManualDetectionLimit');
    var ldman_chk  = $('#archetypes-fieldname-AllowManualDetectionLimit #AllowManualDetectionLimit');

    /**
     * Entry-point method for AnalysisServiceEditView
     */
    that.load = function() {

        // LIMS-1775 Allow to select LDL or UDL defaults in results with readonly mode
        // https://jira.bikalabs.com/browse/LIMS-1775
        $(ldsel_chk).change(function() {
            if ($(this).is(':checked')) {
                $(ldman_fd).show();
            } else {
                $(ldman_fd).hide();
                $(ldman_chk).prop('checked', false);
            }
        });
        $(ldsel_chk).change();

        // service defaults
        // update defalt Containers
        $(".portaltype-analysisservice #RequiredVolume, .portaltype-analysisservice #Separate").change(function(){
            var separate = $("#Separate").prop("checked");
            if(!separate){
                $("[name='Preservation\\:list']").prop("disabled", false);
            }
            var requestdata = {
                "allow_blank":true,
                "show_container_types":!separate,
                "show_containers":separate,
                "_authenticator": $("input[name='_authenticator']").val()
            };
            updateContainers("#Container\\:list", requestdata);
        });

        // partition table -> separate checkboxes
        // partition table -> minvol field
        // update row's containers
        $(".portaltype-analysisservice [name^='PartitionSetup.separate'],.portaltype-analysisservice [name^='PartitionSetup.vol']").change(function(){
            var separate = $(this).parents("tr").find("[name^='PartitionSetup.separate']").prop("checked");
            if (!separate){
                $(this).parents("tr").find("[name^='PartitionSetup.preservation']").prop("disabled", false);
            }
            var minvol = $(this).parents("tr").find("[name^='PartitionSetup.vol']").val();
            var target = $(this).parents("tr").find("[name^='PartitionSetup.container']");
            var requestdata = {
                "allow_blank":true,
                "minvol":minvol,
                "show_container_types":!separate,
                "show_containers":separate,
                "_authenticator": $("input[name='_authenticator']").val()
            };
            updateContainers(target, requestdata);
        });

        // copy sampletype MinimumVolume to minvol when selecting sampletype
        $(".portaltype-analysisservice [name^='PartitionSetup.sampletype']").change(function(){
            var st_element = this;
            var request_data = {
                catalog_name: "uid_catalog",
                UID: $(this).val()
            };
            window.bika.lims.jsonapi_read(request_data, function(data) {
                var minvol = data.objects[0].MinimumVolume;
                var target = $(st_element).parents("tr").find("[name^='PartitionSetup.vol']");
                $(target).val(minvol);
                // trigger change on containers, in case SampleType volume rendered
                // the selected container too small and removed it from the list
                $(st_element).parents("tr").find("[name^='PartitionSetup.container']").change();
            });
        });


        // handling of pre-preserved containers in the Default Container field
        // select the preservation and disable the input.
        $(".portaltype-analysisservice #Container").bind("selected", function(){
            var container_uid = $(this).attr("uid");
            var request_data = {
                catalog_name: "uid_catalog",
                UID: container_uid
            };
            window.bika.lims.jsonapi_read(request_data, function(data) {
                if (data.objects.length < 1 ||
                    (!data.objects[0].PrePreserved) || (!data.objects[0].Preservation)) {
                    $("#Preservation").val("");
                    $("#Preservation").prop("disabled", false);
                } else {
                    $("#Preservation").val(data.objects[0].Preservation);
                    $("#Preservation").prop("disabled", true);
                }
            });
        });

        // handling of pre-preserved containers in the per Sample-Type rows
        // select the preservation and disable the input.
        $(".portaltype-analysisservice [name^='PartitionSetup.container']").change(function(){
            var target = $(this).parents("tr").find("[name^='PartitionSetup.preservation']");
            var container_uid = $(this).val();
            if(!container_uid || (container_uid.length == 1 && !container_uid[0])){
                $(target).prop("disabled", false);
                return;
            }
            container_uid = container_uid[0];
            var request_data = {
                catalog_name: "uid_catalog",
                UID: container_uid
            };
            window.bika.lims.jsonapi_read(request_data, function(data) {
                if (data.objects.length < 1 ||
                    (!data.objects[0].PrePreserved) || (!data.objects[0].Preservation)) {
                    $(target).prop("disabled", false);
                } else {
                    $(this).val(container_uid);  // makes no sense to leave multiple items selected
                    $(target).val(data.objects[0].Preservation);
                    $(target).prop("disabled", true);
                }
            });
        });

        // update on first load
        // $(".portaltype-analysisservice [name^='PartitionSetup.separate']").change();
        // $(".portaltype-analysisservice [name^='Container']").change();
        // $(".portaltype-analysisservice [name^='PartitionSetup.container']").trigger("selected");

        // initial setup - hide Interim widget if no Calc is selected
        if($(".portaltype-analysisservice #Calculation").val() === ""){
            $("#InterimFields_more").click(); // blank last row
            var rows = $("tr.records_row_InterimFields"); // Clear the rest
            if($(rows).length > 1){
                for (var i = $(rows).length - 2; i >= 0; i--) {
                    $($(rows)[i]).remove();
                }
            }
            $("#archetypes-fieldname-InterimFields").hide();
            return;
        }

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

        // The 'Manual entry of results' value changes
        $(manual_chk).change(function() {
            if ($(this).is(':checked')) {

                // The user can select the Analysis Service methods
                // manually. The default method will be retrieved from
                // the methods selected in the multiselect box

                // Show the methods multiselector
                $(methods_fd).fadeIn('slow');

                // Show the default method selector
                $(method_fd).show();
                $(method_sel).unbind("focus");

                // Delegate remaining actions to Methods change event
                $(methods_ms).change();

            } else {

                // The method selection must be done by enabling the
                // 'Allow instrument entry of results'

                // Hide and clear the methods multiselector
                $(methods_fd).hide();
                $(methods_ms).find('option[selected]').prop('selected', false);
                $(methods_ms).val('');

                // Delegate remaining actions to Methods change event
                $(methods_ms).change();

                // Select instrument entry and fire event
                $(instr_chk).prop('checked', true);
            }
            $(instr_chk).change();
        });

        // The 'Allow instrument entry of results' value changes
        $(instr_chk).change(function() {
            if ($(this).is(':checked')) {

                // The user must select the instruments supported by
                // this Analysis Service. The default method will be
                // retrieved from the default instrument selected.

                // The user must be able to allow manual entry
                $(manual_chk).unbind("click");

                // Show the instruments multiselector
                $(instrs_fd).fadeIn('slow');

                // Remove the 'none' option from instruments multiselector
                $(instrs_ms).find('option[value=""]').remove();

                // Remove the 'none' option from def instrument selector
                $(instr_sel).find('option[value=""]').remove();

                // Show the default instrument selector
                $(instr_fd).fadeIn('slow');

                // Disable the default method selector
                $(method_sel).focus(function(e) {
                    $(this).blur();
                });

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

                // Hide the instruments multiselector and unselect all
                $(instrs_fd).hide();
                if ($(instrs_ms).find('option[value=""]').length == 0) {
                    $(instrs_ms).prepend('<option value="">None</option>');
                }
                $(instrs_ms).val('');
                $(instrs_ms).find('option[value=""]').prop("selected", true);

                // Hide the default instrument selector
                $(instr_fd).hide();

                // Unselect the default instrument
                if ($(instr_sel).find('option[value=""]').length == 0) {
                    $(instr_sel).prepend('<option value="">None</option>');
                }
                $(instr_sel).val('');
                $(instr_sel).find('option[value=""]').prop("selected", true);

                // The user mustn't be allowed to unset manual entry
                $(manual_chk).click(function(e) {
                    e.preventDefault();
                });

                // The user must be able to select the default method manualy
                $(methods_ms).change();
                $(method_sel).unbind("focus");

                // If manual entry is not selected, select it and
                // fire event cascade
                if (!$(manual_chk).is(':checked')) {
                    $(manual_chk).prop('checked', true);
                    $(manual_chk).change();
                }
            }
        });

        // The methods multiselect changes
        $(methods_ms).change(function(e) {
            var prevmethod = $(method_sel).val();
            var prevmethodtxt = $(method_sel).find('option[value="'+prevmethod+'"]').html();
            /*if ($(this).val() == null) {
                // At least one method must be selected
                $(this).val($(this).find('option').first().val());
            }*/

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
            if (!$(instr_chk).is(':checked')) {
                $(method_sel).val(defoption.val());
            } else {
                if ($(method_sel).find('option[value="'+prevmethod+'"]').length == 0) {
                    $(method_sel).append('<option value="'+prevmethod+'">'+prevmethodtxt+'</option>');
                }
                $(method_sel).val(prevmethod);
            }

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
                            var instrument_path = window.location.protocol + "//" + window.location.host + data.objects[0].path;
                            if ($('#invalid-instruments-alert').length > 0) {
                                $('#invalid-instruments-alert dd').first().append(", " + title);
                            } else {
                                var errmsg = _("Some of the selected instruments are out-of-date or with failed calibration tests");
                                var html = "<div id='invalid-instruments-alert' class='alert'>"+
                                           "    <dt>" + errmsg + ":</dt>"+
                                           "    <dd> <a href=" +instrument_path + ">" + title + "</a></dd>"+
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
            $(method_sel).find('option').remove();
            $(method_sel).append("<option value=''>"+_("None")+"</option>");
            $(method_sel).val('');
            $.ajax({
                url: window.portal_url + "/get_instrument_method",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'uid': $(instr_sel).val() },
                dataType: 'json',
                async: false
            }).done(function(data) {
                $(method_sel).find('option').remove();
                if (data != null && data['uid']) {
                    // Set the instrument's method
                    var option = '<option value="'+data['uid']+'">'+data['title']+'</option>';
                    $(method_sel).append(option);
                    $(method_sel).val(data['uid']);
                } else {
                    // Oooopps. The instrument has no method assigned
                    $(method_sel).append("<option value=''>"+_("None")+"</option>");
                    $(method_sel).val('');
                }
                // Delegate the action to Default Calc change event
                $(defcalc_chk).change();
            });
        });


        // The 'Default Calculation' checkbox changes
        $(defcalc_chk).change(function() {

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
                        $(calc_sel).find('option').remove();
                        if (data != null && data['uid']) {
                            $(calc_sel).prepend('<option value="'+data['uid']+'">'+data['title']+'</option>');
                        } else {
                            $(calc_sel).append('<option value="">'+_('None')+'</option>');
                        }
                        $(calc_sel).val($(calc_sel).find('option').first().val());

                        // Delegate the action to Default Calculation change event
                        $(calc_sel).change();
                    });
                } else {
                    $(calc_sel).find('option').remove();
                    $(calc_sel).append('<option value="">'+_('None')+'</option>');
                    $(calc_sel).change();
                }
            } else {
                $(calc_sel).find('option').remove();
                $(calc_sel).append('<option value="">'+_('None')+'</option>');
                $(calc_sel).val('');

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

        // Save the manually entered interims to keep them if another
        // calculation is set. We need to know which interim fields
        // are from the current selected calculation and which of them
        // have been set manually.
        $('body').append("<input type='hidden' id='temp_manual_interims' value='[]'>");
        rows = $("tr.records_row_InterimFields");
        var originals = [];
        if($(rows).length > 1){
            for (i = $(rows).length - 2; i >= 0; i--) {
                // Get the original values
                var keyword = $($($(rows)[i]).find('td input')[0]).val();
                if (keyword != '') {
                    var title = $($($(rows)[i]).find('td input')[1]).val();
                    var value = $($($(rows)[i]).find('td input')[2]).val();
                    var unit = $($($(rows)[i]).find('td input')[3]).val();
                    var hidd = $($($(rows)[i]).find('td input')[4]).is(':checked');
                    var wide = $($($(rows)[i]).find('td input')[5]).is(':checked');
                    originals.push([keyword, title, value, unit, hidd, wide]);
                }
            }
        }
        var toremove = []
        var calcuid = "";
        $(calc_sel).find('option').remove();
        if ($(defcalc_chk).is(':checked')) {
            calcuid = $(calc_sel).attr('data-default');
        } else {
            calcuid = $(acalc_sel).attr('data-default');
        }
        if (calcuid != null && calcuid != '') {
            var request_data = {
                catalog_name: "bika_setup_catalog",
                UID: calcuid
            };
            window.bika.lims.jsonapi_read(request_data, function(data) {
                if (data.objects.length > 0) {
                    $(calc_sel).append('<option value="'+data.objects[0].UID+'">'+data.objects[0].Title+'</option>');
                    $(calc_sel).val(data.objects[0].UID);
                    for (i = 0; i < data.objects[0].InterimFields.length; i++) {
                        var row = data.objects[0].InterimFields[i];
                        toremove.push(row.keyword);
                    }
                } else {
                    $(calc_sel).append('<option value="'+data+'">'+_('None')+'</option>');
                    $(calc_sel).val('');
                }
                var manualinterims = originals.filter(function(el) {
                    return toremove.indexOf(el[0]) < 0;
                });
                // Save the manualinterims in some hidden place
                $('#temp_manual_interims').val($.toJSON(manualinterims));

                // Fire events cascade
                $(manual_chk).change();
            });
        } else {
            // Fire events cascade
            $(manual_chk).change();
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

            // Manually entered results?
            var manualinterims = $.parseJSON($('#temp_manual_interims').val());
            if (manualinterims.length > 0) {
                $(interim_fd).fadeIn('slow');
                var i = $("tr.records_row_InterimFields").length-1;
                for (k = 0; k < manualinterims.length; k++) {
                    $("#InterimFields-keyword-"+i).val(manualinterims[k][0]);
                    $("#InterimFields-title-"+i).val(manualinterims[k][1]);
                    $("#InterimFields-value-"+i).val(manualinterims[k][2]);
                    $("#InterimFields-unit-"+i).val(manualinterims[k][3]);
                    $("#InterimFields_more").click();
                    i++;
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
                        var instrument_path = window.location.protocol + "//" + window.location.host + data.objects[0].path;
                        if ($('#invalid-instruments-alert').length > 0) {
                            $('#invalid-instruments-alert dd').first().append(", " + title);
                        } else {
                            var errmsg = _("Some of the selected instruments are out-of-date or with failed calibration tests");
                            var html = "<div id='invalid-instruments-alert' class='alert'>"+
                                       "    <dt>" + errmsg + ":</dt>"+
                                       "    <dd> <a href=" +instrument_path + ">" + title + "</a></dd>"+
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


    function updateContainers(target,requestdata){
        $.ajax({
            type: "POST",
            url: window.location.href + "/getUpdatedContainers",
            data: requestdata,
            success: function(data){
                // keep the current selection if possible
                var option = $(target).val();
                if (option === null || option === undefined){
                    option = [];
                }
                $(target).empty();
                $.each(data, function(i,v){
                    if($.inArray(v[0], option) > -1) {
                        $(target).append("<option value='"+v[0]+"' selected='selected'>"+v[1]+"</option>");
                    } else {
                        $(target).append("<option value='"+v[0]+"'>"+v[1]+"</option>");
                    }
                });
            },
            dataType: "json"
        });
    }


    function applyStyles() {

        $($(manual_fd)).after($(methods_fd));

        $(methods_fd)
            .css('border', '1px solid #cfcfcf')
            .css('background-color', '#efefef')
            .css('padding', '10px')
            .css('margin-bottom', '20px');

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
            .css('padding', '10px')
            .css('margin-bottom', '20px');

        $(acalc_fd).find('label').hide();
        $(calc_fd).find('label').hide();
    }
}
