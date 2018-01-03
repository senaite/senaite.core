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
            $('div.worksheet_add_controls div.bika-alert').remove();
            if (val != '' && val != null) {
                $('div.worksheet_add_controls').append('<div class="bika-alert">'+_("Only the analyses for which the selected instrument is allowed will be added automatically.")+'</div>');
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
        $('[name="list_FilterByCategory"]').live("change", function(){
            val = $('[name="list_FilterByCategory"]').find(":selected").val();
            if(val == 'any'){
                $('[name="list_FilterByService"]').empty();
                $('[name="list_FilterByService"]').append("<option value='any'>"+_('Any')+"</option>");
                return;
            }
            $.ajax({
                url: window.location.href.split("?")[0].replace("/add_analyses","") + "/getServices",
                type: 'POST',
                data: {'_authenticator': $('input[name="_authenticator"]').val(),
                       'getCategoryUID': val},
                dataType: "json",
                success: function(data, textStatus, $XHR){
                    current_service_selection = $('[name="list_FilterByService"]').val();
                    $('[name="list_FilterByService"]').empty();
                    $('[name="list_FilterByService"]').append("<option value='any'>"+_('Any')+"</option>");
                    for(i=0; i<data.length; i++){
                        if (data[i] == current_service_selection){
                            selected = 'selected="selected" ';
                        } else {
                            selected = '';
                        }
                        $('[name="list_FilterByService"]').append(
                            "<option "+selected+"value='"+data[i][0]+
                            "'>"+data[i][1]+"</option>");
                    }
                }
            });
        });
        $('[name="list_FilterByCategory"]').trigger("change");

        // add_analyses analysis search is handled by
        // worksheet/views/add_analyses/AddAnalysesView/__call__
        $('.ws-analyses-search-button').live('click', function (event) {
            // in this context we already know there is only one bika-listing-form
            var form_id = "list";
            var form = $('form[id="'+form_id+'"]');
            var params = {};

            // dropdowns are printed in ../templates/worksheet_add_analyses.pt
            // We add <formid>_<filterby_index>=<value>, which are checked in
            // worksheet/view/add_analyses.py/__call__, that are different
            // from listing or catalog filters
            var filter_indexes = ['FilterByCategory', 'FilterByService',
                'FilterByClient'];
            var field_set = $(this).parent('fieldset');
            for (var i=0; i<filter_indexes.length; i++) {
                var idx_name = filter_indexes[i];
                var field_name = form_id+"_"+idx_name;
                var element = $(field_set).find('[name="'+field_name+'"]');
                var value = $(element).val();
                if (value == undefined || value == null || value == 'any') {
                    continue;
                }
                params[idx_name] = value;
            }
            // Add other fields required from bikalisting form
            params['form_id'] = form_id;
            params['table_only'] = form_id;
            params['portal_type'] = 'Analysis';
            params['submitted'] = '1';
            var base_fields = ['_authenticator', 'view_url', 'list_sort_on', 'list_sort_order'];
            for (var i=0; i<base_fields.length; i++) {
                var field_name = base_fields[i];
                var field = $(form).find('input[name="'+field_name+'"]');
                var value = $(field).val();
                if (value == undefined || value == null) {
                    continue;
                }
                params[field_name] = value;
            }

            $.post(window.location.href, params).done(function(data) {
                $(form).find('.bika-listing-table-container').html(data);
                window.bika.lims.BikaListingTableView.load();
            });

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
            $.each($(".worksheet_add_control_services .bika-listing-table input:checked"), function(i,e){
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

        loadInstrumentEventHandlers();
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

    /**
     * Stores the constraints regarding to methods and instrument assignments to
     * each analysis. The variable is filled in initializeInstrumentsAndMethods
     * and is used inside loadMethodEventHandlers.
     */
    var mi_constraints = null;

    /**
     * Applies the rules and constraints to each analysis displayed in the
     * manage results view regarding to methods, instruments and results.
     * For example, this service is responsible of disabling the results field
     * if the analysis has no valid instrument available for the selected
     * method if the service don't allow manual entry of results. Another
     * example is that this service is responsible of populating the list of
     * instruments avialable for an analysis service when the user changes the
     * method to be used.
     * See docs/imm_results_entry_behavior.png for detailed information.
     */
    function initializeInstrumentsAndMethods() {
        var auids = [];

        /// Get all the analysis UIDs from this manage results table, cause
        // we'll need them to retrieve all the IMM constraints/rules to be
        // applied later.
        var dictuids = $.parseJSON($('#item_data').val());
        $.each(dictuids, function(key, value) { auids.push(key); });

        // Retrieve all the rules/constraints to be applied for each analysis
        // by using an ajax call. The json dictionary returned is assigned to
        // the variable mi_constraints for further use.
        // FUTURE: instead of an ajax call to retrieve the dictionary, embed
        //  the dictionary in a div when the bika_listing template is rendered.
        $.ajax({
            url: window.portal_url + "/get_method_instrument_constraints",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val(),
                   'uids': $.toJSON(auids) },
            dataType: 'json'
        }).done(function(data) {
            // Save the constraints in the m_constraints variable
            mi_constraints = data;
            $.each(auids, function(index, value) {
                // Apply the constraints/rules to each analysis.
                load_analysis_method_constraint(value, null);
            });
        }).fail(function() {
            window.bika.lims.log("bika.lims.worksheet: Something went wrong while retrieving analysis-method-instrument constraints");
        });
    }

    /**
     * Applies the constraints and rules to the specified analysis regarding to
     * the method specified. If method is null, the function assumes the rules
     * must apply for the currently selected method.
     * The function uses the variable mi_constraints to find out which is the
     * rule to be applied to the analysis and method specified.
     * See initializeInstrumentsAndMethods() function for further information
     * about the constraints and rules retrieval and assignment.
     * @param {string} analysis_uid - The Analysis UID
     * @param {string} method_uid - The Method UID. If null, uses the method
     *  that is currently selected for the specified analysis.
     */
    function load_analysis_method_constraint(analysis_uid, method_uid) {
        if (method_uid === null) {
            // Assume to load the constraints for the currently selected method
            muid = $('select.listing_select_entry[field="Method"][uid="'+analysis_uid+'"]').val();
            muid = muid ? muid : '';
            load_analysis_method_constraint(analysis_uid, muid);
            return;
        }
        andict = mi_constraints[analysis_uid];
        if (!andict) {
            return;
        }
        constraints = andict[method_uid];
        if (!constraints || constraints.length < 7) {
            return;
        }
        m_selector = $('select.listing_select_entry[field="Method"][uid="'+analysis_uid+'"]');
        i_selector = $('select.listing_select_entry[field="Instrument"][uid="'+analysis_uid+'"]');

        // None option in method selector?
        $(m_selector).find('option[value=""]').remove();
        if (constraints[1] == 1) {
            $(m_selector).prepend('<option value="">'+_('Not defined')+'</option>');
        }

        // Select the method
        $(m_selector).val(method_uid);

        // Method selector visible?
        // 0: no, 1: yes, 2: label, 3: readonly
        $(m_selector).prop('disabled', false);
        $('.method-label[uid="'+analysis_uid+'"]').remove();
        if (constraints[0] === 0) {
            $(m_selector).hide();
        } else if (constraints[0] == 1) {
            $(m_selector).show();
        } else if (constraints[0] == 2) {
            if (andict.length > 1) {
                $(m_selector).hide();
                var method_name = $(m_selector).find('option[value="'+method_uid+'"]').innerHtml();
                $(m_selector).after('<span class="method-label" uid="'+analysis_uid+'" href="#">'+method_name+'</span>');
            }
        } else if (constraints[0] == 3) {
            //$(m_selector).prop('disabled', true);
            $(m_selector).show();
        }

        // We are going to reload Instrument list.. Enable all disabled options from other Instrument lists which has the
        // same value as old value of this Instrument Selectbox.
        ins_old_val=$(i_selector).val();
        if(ins_old_val && ins_old_val!=''){
            $('table.bika-listing-table select.listing_select_entry[field="Instrument"][value!="'+ins_old_val+'"] option[value="'+ins_old_val+'"]').prop('disabled', false);
        }
        // Populate instruments list
        $(i_selector).find('option').remove();
        if (constraints[7]) {
            $.each(constraints[7], function(key, value) {
                if(is_ins_allowed(key)){
                    $(i_selector).append('<option value="'+key+'">'+value+'</option>');
                }else{
                    $(i_selector).append('<option value="'+key+'" disabled="true">'+value+'</option>');
                }
            });
        }

        // None option in instrument selector?
        if (constraints[3] == 1) {
            $(i_selector).prepend('<option selected="selected" value="">'+_('None')+'</option>');
        }

        // Select the default instrument
        if(is_ins_allowed(constraints[4])){
           $(i_selector).val(constraints[4]);
           // Disable this Instrument in the other Instrument SelectBoxes
           $('table.bika-listing-table select.listing_select_entry[field="Instrument"][value!="'+constraints[4]+'"] option[value="'+constraints[4]+'"]').prop('disabled', true);
        }

        // Instrument selector visible?
        if (constraints[2] === 0) {
            $(i_selector).hide();
        } else if (constraints[2] == 1) {
            $(i_selector).show();
        }

        // Allow to edit results?
        if (constraints[5] === 0) {
            $('.interim input[uid="'+analysis_uid+'"]').val('');
            $('input[field="Result"][uid="'+analysis_uid+'"]').val('');
            $('.interim input[uid="'+analysis_uid+'"]').prop('disabled', true);
            $('input[field="Result"][uid="'+analysis_uid+'"]').prop('disabled', true);
        } else if (constraints[5] == 1) {
            $('.interim input[uid="'+analysis_uid+'"]').prop('disabled', false);
            $('input[field="Result"][uid="'+analysis_uid+'"]').prop('disabled', false);
        }

        // Info/Warn message?
        $('.alert-instruments-invalid[uid="'+analysis_uid+'"]').remove();
        if (constraints[6] && constraints[6] !== '') {
            $(i_selector).after('<img uid="'+analysis_uid+'" class="alert-instruments-invalid" src="'+window.portal_url+'/++resource++bika.lims.images/warning.png" title="'+constraints[6]+'")">');
        }

        $('.amconstr[uid="'+analysis_uid+'"]').remove();
        //$(m_selector).before("<span style='font-weight:bold;font-family:courier;font-size:1.4em;' class='amconstr' uid='"+analysis_uid+"'>"+constraints[10]+"&nbsp;&nbsp;</span>");
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
            var auid = $(this).attr('uid');
            var muid = $(this).val();
            load_analysis_method_constraint(auid, muid);
        });
    }

    /**
     * If a new instrument is chosen for the analysis, disable this Instrument for the other analyses. Also, remove
     * the restriction of previous Instrument of this analysis to be chosen in the other analyses.
     */
    function loadInstrumentEventHandlers() {
        $('table.bika-listing-table select.listing_select_entry[field="Instrument"]').on('focus', function () {
                // First, getting the previous value
                previous = this.value;
            }).change(function() {
            var auid = $(this).attr('uid');
            var iuid = $(this).val();
            // Disable New Instrument for rest of the analyses
            $('table.bika-listing-table select.listing_select_entry[field="Instrument"][value!="'+iuid+'"] option[value="'+iuid+'"]').prop('disabled', true);
            // Enable previous Instrument everywhere
            $('table.bika-listing-table select.listing_select_entry[field="Instrument"] option[value="'+previous+'"]').prop('disabled', false);
            // Enable 'None' option as well.
            $('table.bika-listing-table select.listing_select_entry[field="Instrument"] option[value=""]').prop('disabled', false);
        });
    }

    /**
     * Check if the Instrument is allowed to appear in Instrument list of Analysis.
     * Returns true if multiple use of an Instrument is enabled for assigned Worksheet Template or UID is not in selected Instruments
     * @param {uid} ins_uid - UID of Instrument.
     */
    function is_ins_allowed(uid) {
        var multiple_enabled = $("#instrument_multiple_use").attr('value');
        if(multiple_enabled=='True'){
            return true;
        }else{
            var i_selectors = $('select.listing_select_entry[field="Instrument"]');
            for(i=0; i < i_selectors.length; i++){
                if(i_selectors[i].value == uid){
                    return false;
                }
            }
        }
        return true;
    }
}
