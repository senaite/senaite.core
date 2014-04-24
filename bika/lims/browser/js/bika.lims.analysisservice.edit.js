/**
 * Controller class for Analysis Service Edit view
 */
function AnalysisServiceEditView() {

    var that = this;

    /**
     * Entry-point method for AnalysisServiceEditView
     */
    that.load = function() {

        $('#Instruments').live('change', function() {
            if ($('#Instruments').val() == null &&
                $('#InstrumentEntryOfResults').is(':checked')) {
                $('#InstrumentEntryOfResults').change();
            }
            validateInstruments();
            loadDefaultInstrument();
            loadMethods();
            loadDefaultMethod();
        });

        $('#InstrumentEntryOfResults').change(function() {
            loadManualEntryOfResults();
            loadInstruments();
            loadDefaultInstrument();
            loadMethods();
            loadDefaultMethod();
            loadCalculations();
        });

        $('#Instrument').live('change', function() {
            loadMethods();
            loadDefaultMethod();
            loadCalculations();
        });

        $('#Methods').live('change', function() {
            loadDefaultMethod();
            loadCalculations();
        });

        $('#UseDefaultCalculation').change(function() {
            loadCalculations();
        });

        $('#DeferredCalculation').live('change', function() {
            loadCalculationInterims();
        });

        loadInstrumentEntryOfResults();
        loadManualEntryOfResults();
        loadInstruments();
        loadDefaultInstrument();
        loadMethods();
        loadDefaultMethod();
        loadCalculations();
        applyStyles();
    }

    /**
     * Loads the ManualEntryOfResults and its properties according
     * to the Instruments selection in the Instruments multiselect
     */
    function loadManualEntryOfResults() {
        if ($('#InstrumentEntryOfResults').is(':checked')) {
            // Set as not readonly
            $('#ManualEntryOfResults').prop('disabled', false);
        } else {
            // Check and set as readonly
            $('#ManualEntryOfResults').prop('checked', true);
            $('#ManualEntryOfResults').prop('disabled', true);
        }
    }

    /**
     * Loads the InstrumentEntryOfResults and its properties according
     * to the Instruments selection in the Instruments multiselect
     */
    function loadInstrumentEntryOfResults() {
        if ($('#Instruments option').length == 0) {
            // No instruments available, disable the checkbox
            $('#InstrumentEntryOfResults').prop('checked', false);
            $('#InstrumentEntryOfResults').prop('disabled', true);
            loadEmptyInstrument();
        }
    }

    /**
     * Loads the instruments multiselect in accordance to
     * InstrumentEntryOfResults checkbox state
     */
    function loadInstruments() {
        if ($('#InstrumentEntryOfResults').is(':checked')) {
            $('#archetypes-fieldname-Instruments').fadeIn('slow');
            if ($('#Instruments').val() == null) {
                $('#Instruments').val($('#Instrument option').first().val());
            }
        } else {
            $('#archetypes-fieldname-Instruments').hide();
        }
        validateInstruments();
    }

    /**
     * Loads the Default Instrument field and its properties in
     * accordance to the Instruments Multiselect state
     */
    function loadDefaultInstrument() {
        if ($('#Instrument').attr('data-default') == null) {
            var instr = $('#Instrument').val() ? $('#Instrument').val() : '';
            $('#Instrument').attr('data-default', instr);
        }
        if ($('#InstrumentEntryOfResults').is(':checked')) {
            // Fill the selector with the methods selected above
            $('#Instrument option').remove();
            var insts = $('#Instruments').val() ? $('#Instruments').val() : [];
            if (insts.length > 0) {
                $.each(insts, function(index, value) {
                    var option = $('#Instruments option[value="'+value+'"]').clone();
                    $('#Instrument').append(option);
                });
            } else {
                $('#Instrument').append('<option selected val=""></option>');
            }
            // Show the Default Instrument selector and
            // apply the first selected instrument from the
            // multiselect field.
            var definstr = $('#Instrument').attr('data-default');
            if (definstr != '' && $('#Instrument option[value="'+definstr+'"]').length > 0) {
                $('#Instrument').val(definstr);
            } else if (insts.length > 0) {
                $('#Instrument').val(insts[0]);
            } else {
                loadEmptyInstrument();
            }
            $('#archetypes-fieldname-Instrument').fadeIn('slow');
        } else {
            // If no instrument selected, hide instrument selector
            $('#archetypes-fieldname-Instrument').hide();
            loadEmptyInstrument();
        }
    }
    /**
     * Loads the methods multiselect field and its properties in
     * accordance to the InstrumentEntryOfResults state
     */
    function loadMethods() {
        if ($('#InstrumentEntryOfResults').is(':checked')) {
            // If no instrument selected, hide methods multi-select
            $('#archetypes-fieldname-Methods').hide();
        } else {
            // Manual entry: show available methods
            if ($('#Methods').val() == null) {
                //loadEmptyMethod();
                //$('#Methods').val($('#_Method option').first().val());
            }
            $('#archetypes-fieldname-Methods').fadeIn('slow');
        }
    }

    /**
     * Loads the Default Instrument field and its properties in
     * accordance to the Instruments Multiselect state and ManualEntry
     */
    function loadDefaultMethod() {
        if ($('#_Method').attr('data-default') == null) {
            var meth = $('#_Method').val() ? $('#_Method').val() : '';
            $('#_Method').attr('data-default', meth);
        }
        if ($('#TempMethod').length == 0) {
            // Add a hidden selector to allow us to manage the default
            // Method selector options dynamically
            $('body').append('<select id="TempMethod" style="display:none"></select>');
            $('#_Method option').each(function() {
                $(this).appendTo('#TempMethod');
            });
            $('#_Method option').remove();
            var defmethod = $('#_Method').attr('data-default');
            if (defmethod != null && defmethod != '') {
                var option = $('#TempMethod option[value="'+defmethod+'"]').clone();
                $('#_Method').append(option);
                $('#_Method').val($('#_Method option').first().val());
            } else {
                loadEmptyMethod();
            }
        }
        if ($('#InstrumentEntryOfResults').is(':checked')) {
            // Readonly and set default Instrument's method via ajax
            $('#_Method').prop('disabled', true);
            var instruid = $('#Instrument').val();
            if (instruid) {
                $.ajax({
                    url: window.portal_url + "/get_instrument_method",
                    type: 'POST',
                    data: {'_authenticator': $('input[name="_authenticator"]').val(),
                           'uid': instruid },
                    dataType: 'json'
                }).done(function(data) {
                    $('#_Method option').remove();
                    if (data != null && data['uid']) {
                        $('#_Method').append('<option selected="selected" value="'+data['uid']+'">'+data['title']+'</option>');
                    }
                });
            } else {
                loadEmptyMethod();
            }
        } else {
            // Non-readonly, fill the selector with the methods selected above
            $('#_Method option').remove();
            $('#_Method').prop('disabled', false);
            var meths = $('#Methods').val() ? $('#Methods').val() : [];
            var defmethod = $('#_Method').attr('data-default');
            var selectionsucceed = false;
            $.each(meths, function(index, value) {
                var title = $('#Methods option[value="'+value+'"]').html();
                var selected = (defmethod == value) ? "selected=\"selected\"" : "";
                selectionsucceed = (defmethod == value) ? true : selectionsucceed;
                $('#_Method').append('<option value="'+value+'" '+selected+'>'+title+'</option>');
            });
            if (!selectionsucceed && meths.length > 0) {
                $('#_Method option').first().attr('selected', 'selected');
            } else if (!selectionsucceed) {
                loadEmptyMethod();
            }
        }
    }

    /**
     * Loads the calculation lists to be rendered (Deferred or Default)
     * depending on the value of 'Use default calculation' and the
     * Default Method selected. Also loads the Calculation interims if
     * needed.
     */
    function loadCalculations() {
        if ($('#UseDefaultCalculation').is(':checked')) {
            // Use the calculation set by default from the selected method
            $('#archetypes-fieldname-DeferredCalculation').hide();
            $('#archetypes-fieldname-_Calculation').fadeIn('slow');
            $('#_Calculation').prop('disabled', true);
            $('#_Calculation option').remove();
            var methoduid = $('#_Method').val();
            if (methoduid != null && methoduid != '') {
                $.ajax({
                    url: window.portal_url + "/get_method_calculation",
                    type: 'POST',
                    data: {'_authenticator': $('input[name="_authenticator"]').val(),
                           'uid': methoduid },
                    dataType: 'json'
                }).done(function(data) {
                    if (data != null && data['uid']) {
                        $('#_Calculation').append('<option selected val="'+data['uid']+'">'+data['title']+'</option>');
                    }
                });
            }
        } else {
            // Use the deferred calculation (manually set)
            $('#archetypes-fieldname-_Calculation').hide();
            $('#archetypes-fieldname-DeferredCalculation').fadeIn('slow');
        }
        loadCalculationInterims();
    }

    /**
     * Load the calculations interims. Use the calculation selected,
     * DeferredCalculation or DefaultCalculation
     */
    function loadCalculationInterims() {
        // Calculation.
        // 1 - no calculation selected - clear and hide InterimFields widget completely
        // 2 - calc selected - make sure the widget is visible, and fill in default values
        var calcuid = '';
        if ($('#UseDefaultCalculation').is(':checked')) {
            calcuid = $('#_Calculation').val();
        } else {
            calcuid =$('#DeferredCalculation').val();
        }
        var rows, i;
        if (calcuid == null || calcuid == ""){
            $("#InterimFields_more").click(); // blank last row
            rows = $("tr.records_row_InterimFields"); // Clear the rest
            if($(rows).length > 1){
                for (i = $(rows).length - 2; i >= 0; i--) {
                    $($(rows)[i]).remove();
                }
            }
            $("#archetypes-fieldname-InterimFields").hide();
            return;
        }
        $("#archetypes-fieldname-InterimFields").fadeIn('slow');
        var request_data = {
            catalog_name: "bika_setup_catalog",
            UID: calcuid
        };
        window.bika.lims.jsonapi_read(request_data, function(data) {
            // Clear rows
            var rows, i;
            $("#InterimFields_more").click(); // blank last row
            rows = $("tr.records_row_InterimFields");
            if($(rows).length > 1){
                for (i = $(rows).length - 2; i >= 0; i--) {
                    $($(rows)[i]).remove();
                }
            }
            if (data.objects.length > 0) {
                $("[id^='InterimFields-keyword-']").attr("id", "InterimFields-keyword-0");
                $("[id^='InterimFields-title-']").attr("id", "InterimFields-title-0");
                $("[id^='InterimFields-value-']").attr("id", "InterimFields-value-0");
                $("[id^='InterimFields-unit-']").attr("id", "InterimFields-unit-0");

                for (i = 0; i < data.objects[0].InterimFields.length; i++) {
                    var row = data.objects[0].InterimFields[i];
                    $("#InterimFields-keyword-"+i).val(row.keyword);
                    $("#InterimFields-title-"+i).val(row.title);
                    $("#InterimFields-value-"+i).val(row.value);
                    $("#InterimFields-unit-"+i).val(row.unit);
                    $("#InterimFields_more").click();
                }
            } else {
                $("#archetypes-fieldname-InterimFields").hide();
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
            window.jarn.i18n.loadCatalog("plone");
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

    function loadEmptyInstrument() {
        $('#Instrument option').remove();
        $('#Instrument').append('<option selected val=""></option>');
    }

    function loadEmptyMethod() {
        $('#_Method option').remove();
        $('#_Method').append('<option selected val=""></option>');
    }

    function applyStyles() {
        $('#archetypes-fieldname-Instruments')
            .css('border', '1px solid #cfcfcf')
            .css('border-bottom', 'none')
            .css('background-color', '#efefef')
            .css('padding', '10px')
            .css('margin-bottom', '0px');
        $('#archetypes-fieldname-Instrument')
            .css('border', '1px solid #cfcfcf')
            .css('border-top', 'none')
            .css('background-color', '#efefef')
            .css('padding', '10px');
        $('#archetypes-fieldname-_Calculation')
            .css('border', '1px solid #cfcfcf')
            .css('background-color', '#efefef')
            .css('padding', '10px');
        $('#archetypes-fieldname-DeferredCalculation')
            .css('border', '1px solid #cfcfcf')
            .css('background-color', '#efefef')
            .css('padding', '10px');
    }
}
