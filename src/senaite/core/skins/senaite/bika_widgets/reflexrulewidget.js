jQuery(function($){
    $(document).ready(function(){
        // This will be a variable to be used everywhere
        var setupdata = $.parseJSON($('#rules-setup-data').html());
        description_controller();
        method_controller(setupdata);
        remove_last_rule_set();
        setup_as_and_discrete_results(setupdata);
        setup_addnew_buttons();
        // Hide the del_button in the fist td.rulescontainer
        $('table#ReflexRules_table').find('.rw_deletebtn').first().hide();
        setup_del_action_button();
        $('select#Method').bind("change", function () {
            // Updates the new method
            $.each($('table#ReflexRules_table').find('.rw_deletebtn'),
                function(index, element){
                    $(element).trigger( "click" );
                });
            var del_buts = $('table#ReflexRules_table').find('.rw_deletebtn');
            for (var i=0; del_buts.length > i; i++) {
                $(del_buts[i]).trigger( "click" );
            }
            setupdata = $.parseJSON($('#rules-setup-data').html());
            method_controller(setupdata);
        });
        $('input[id^="ReflexRules-range"]').bind("change", function () {
            range_controller(this);
        });
        // Binding the and_or controller
        $('select[id^="ReflexRules-and_or-"]').bind("change", function () {
                and_or_controller($(this).closest('div.conditionscontainer'));
            });
        // Running the trigger controller
        $.each($('select[id^="ReflexRules-trigger"]'), function(index, element){
                trigger_controller(element);
            });
        // Binding the trigger controller
        $('select[id^="ReflexRules-trigger"]').bind("change", function () {
            trigger_controller(this);
        });
        $('select[id^="ReflexRules-analysisservice-0-0"]')
            .bind("change", function () {
                analysiservice_change(this, setupdata);
            });
        // Setting the ws and define result stuff
        $.each($('div.action'), function(index, element){
                otherWS_controller(element);
                action_select_controller(element, true);
            });
        // Binding the controllers
        $('select[id^="ReflexRules-otherWS-"]').bind("change", function () {
            otherWS_controller($(this).closest('div.action'));
        });
        $('select[id^="ReflexRules-action-"]').bind("change", function () {
            action_select_controller($(this).closest('div.action'), false);
        });
        // Setting local id when page is loaded for the first time
        set_action_select_value($('div.action'));
        // Controller on 'ReflexRules-setresulton' selection list
        $('select[id^="ReflexRules-setresulton-"]').bind("change", function () {
            setresulton_controller($(this).closest('div.action'));
        });
        // Setting up the selected analysis services outside the main rule
        setup_as(setupdata);
        setup_svof(setupdata);
        // Setting up the worksheet templates select options
        setup_worksheettemplate(setupdata);
    });
    /**
     * The controller to hide/show the description.
     */
    function description_controller(){
        $('#ReflexRules_help').hide();
        $('label[for="ReflexRules"]').click(function(e) {
            $('#ReflexRules_help').toggle();
        });
    }

    function method_controller(setupdata){
        /**
        This function updates the options in the 'mother' rule
        according to the selected method
        */
        var method = $('select[id="Method"]').find(":selected").attr('value');
        // Getting the analysis service ralated to the method
        var ass = setupdata[method].analysisservices;
        var ass_keys = setupdata[method].as_keys;
        // Remove selection options
        $('select[id^="ReflexRules-analysisservice-0-0"]')
            .find("option").remove();
        // Create an option for each analysis service obtained for
        // the current method
        for (var i=0; ass_keys.length > i; i++){
            $('select[id^="ReflexRules-analysisservice-0-0"]').append(
                '<option value="' + ass_keys[i] +
                '">' + ass[ass_keys[i]].as_title + '</option>'
            );
        }
        var as_dom = $('select[id^="ReflexRules-analysisservice-0-0"]');
        $.each(as_dom,function(index, element){
            $(element).trigger("change");
        });
    }

    function analysiservice_change(as, setupdata){
        /**
        This function hides/shows the expected result fields accordingly with
        the main analysis service. It also loads the available options for expected
        discrete results.
        */
        var method = $('select[id="Method"]').find(":selected").attr('value');
        //Check if the selected analysis service has discrete rules
        var as_uid = $(as).find(":selected").attr('value');
        var as_info = setupdata[method].analysisservices[as_uid];
        if (as_info === undefined){
            var _ = window.jarn.i18n.MessageFactory("senaite.core");
            window.bika.lims.portalMessage(_('An analysis service must be selected'));
        }
        else{
            var resultoptions = as_info.resultoptions;
            var i=0, select;
            if(resultoptions.length > 0){
                // If the analysis service has discrete values, lets hide the range
                // inputs and display the result selector with all the possible
                // results for the analysis service
                // "Expected results" section
                $('.rangecontainer').hide().find('input').val('');
                $('.resultoptioncontainer').show();
                // Delete old options
                select = $('.resultoptioncontainer').find('select');
                $(select).find('option').remove();
                // Actions section
                var select_actionset = $('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete']");
                $('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete']")
                    .show();
                // Delete old options
                $('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete'] option")
                    .remove();
                $('div.actions-set')
                    .find("input[id^='ReflexRules-setresultvalue']")
                    .hide().val('');
                // Write the different options in both sites
                for (i=0; resultoptions.length > i; i++){
                    $(select).append(
                        '<option value="' + resultoptions[i].ResultValue +
                        '">' + resultoptions[i].ResultText + '</option>'
                    );
                    $(select_actionset).append(
                        '<option value="' + resultoptions[i].ResultValue +
                        '">' + resultoptions[i].ResultText + '</option>'
                    );
                }
            }
            else{
                // If the analysis service has normal values, lets hide the discrete
                // values selector and remove its options
                //Hide the "expected result" fields
                $('.resultoptioncontainer').hide();
                $('.rangecontainer').show();
                var opts = $('.resultoptioncontainer').find('option');
                $(opts).remove();
                // Hide the fields in the action sections
                $('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete']")
                    .hide();
                // Delete old options
                $('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete'] option")
                    .remove();
                $('div.actions-set')
                    .find("input[id^='ReflexRules-setresultvalue']")
                    .show();
            }
            // Remove the old options
            select = $('.worksheet-template-section').find('select');
            $(select).find('option').remove();
            var wst = as_info.wstoptions;
            // Get the worksheet templates available for the analysis service
            $(select).append(
                '<option value=""></option>'
            );
            for (i=0; wst.length > i; i++){
                $(select).append(
                    '<option value="' + wst[i][0] +
                    '">' + wst[i][1] + '</option>'
                );
            }
        }
    }

    function remove_last_rule_set(){
        /**
        This function deletes the lates rule. It is useful to avoid user
        confusions when they open the rule's view.
        If the reflex rule object contains three actions, the widget adds an
        extra line which can cause confusion.
        */
        var del_but = $('table#ReflexRules_table').find('.rw_deletebtn');
        if(del_but.length > 1) {
            $(del_but[del_but.length - 1]).trigger( "click" );
        }
    }

    function range_controller(element){
        /**
        - range1 must be bigger than range0
        */
        var td = $(element).parent();
        var range0 = td.find('[id^="ReflexRules-range0"]');
        var range1 = td.find('[id^="ReflexRules-range1"]');
        if ($(range0).val() > $(range1).val()) {
            $(range1).val($(range0).val());
        }
    }

    function and_or_controller(element){
        /**
        The 'element' variable is the 'conditionscontainer' where the triggered
        selector belongs.
        When the value of the selectelement is 'and' or 'or', another
        conditionscontainer should be created below.
        */
        var sel = $(element).find('.and_or');
        var and_or = $(sel).find(":selected").attr('value');
        // This attribute is used to know if the selection element has changed
        // its value from 'and' to 'or' (or viceversa) and a no container
        // should be placed, or it has changed from a void value to 'and'/'or'
        var already_sel = $(sel).attr('already_sel');
        if ((and_or == 'and' || and_or == 'or') && already_sel != 'yes'){
            // create a new 'conditionscontainer' div below
            var container_clone = $(element).clone();
            var found = $(container_clone).find("input, select");
            for (var i = found.length - 1; i >= 0; i--) {
                // Increment the index id
                var prefix, nr;
                var ID = found[i].id;
                prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
                var sufix = parseInt(ID.split("-")[3]) + 1;
                nr = ID.split("-")[2];
                $(found[i]).attr('id', prefix + "-" + nr + "-" + sufix);
                // Increment the name id
                var name = found[i].name;
                prefix = name.split(":")[0];
                sufix = name.split(":")[1] + ":" + name.split(":")[2];
                var prefix_name = prefix.split('-')[0];
                var prefix_idx = parseInt(prefix.split('-')[1]) + 1;
                prefix = prefix_name + "-" + prefix_idx;
                $(found[i]).attr('name', prefix + ":" + sufix);
            }
            // clear values
            for(i=0; i<$(container_clone).children().length; i++){
                var td = $(container_clone).children()[i];
                var input = $(td).find('input').not('.addnew');
                $(input).val('');
                var sel_options = $(td).find(":selected");
                $(sel_options).prop("selected", false);
            }
            $(container_clone).insertAfter(element);
            var setupdata = $.parseJSON($('#rules-setup-data').html());
            $(sel).attr('already_sel', 'yes');
            // Binding the and_or controller
            $(container_clone).find('select[id^="ReflexRules-and_or-"]')
                .bind("change", function () {
                    and_or_controller($(this).closest('div.conditionscontainer'));
                });
        }
        else if (and_or != 'and' && and_or != 'or') {
            // Remove the 'conditionscontainer' div below
            var target = $(element).next('.conditionscontainer');
            $(target).remove();
            $(sel).attr('already_sel', 'no');
        }
    }

    function trigger_controller(element){
        /**
        If trigger option 'after verify' is selected, all action aptions
        of the set must be halt at duplicate because a repeat action after
        verifying the analysis has no sense.
        */
        var td = $(element).parent();
        var action = td.find('[id^="ReflexRules-action-"]');
        if ($(element).find(":selected").attr('value') == 'verify'){
            // Remove the repeat option from actions
            $(action).find("option[value='repeat']").remove();
        }
        else if ($(action).find("option[value='repeat']").length === 0) {
            $(action).append('<option value="repeat">Repeat</option>');
        }
    }

    function setup_addnew_buttons(){
        /**
        Bind the process trigged after clicking on a 'more' or 'add action' button
        */
        $("input[id$='_addnew']").click(function(i,e){
            if ($(this).attr("id").split("_")[1] == "action"){
                // The process to add a new action row
                add_action_row(this);
            }
            else{
                // The process to add a whole new action set
                add_action_set(this);
            }
        });
    }

    function add_action_row(element){
        /**
        :element: is the more(addnew) button
        This function defines the process to add a new action row
        */
        var row = $(element).parent().find('.action').last().clone();
        var found = $(row).find("input, select");
        for (var i = found.length - 1; i >= 0; i--) {
            // Increment the index id
            var prefix, nr;
            var ID = found[i].id;
            prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
            var sufix = parseInt(ID.split("-")[3]) + 1;
            nr = ID.split("-")[2];
            $(found[i]).attr('id', prefix + "-" + nr + "-" + sufix);
            // Increment the name id
            var name = found[i].name;
            prefix = name.split(":")[0];
            sufix = name.split(":")[1] + ":" + name.split(":")[2];
            var prefix_name = prefix.split('-')[0];
            var prefix_idx = parseInt(prefix.split('-')[1]) + 1;
            prefix = prefix_name + "-" + prefix_idx;
            $(found[i]).attr('name', prefix + ":" + sufix);
        }
        // clear values
        for(i=0; i<$(row).children().length; i++){
            var td = $(row).children()[i];
            var input = $(td).find('input').not('.addnew');
            $(input).val('');
            var sel_options = $(td).find(":selected");
            $(sel_options).prop("selected", false);
        }
        $(row).insertBefore(element);
        // Binding the otherWS controller and the controller for specific
        // actions select
        $(row).find('select[id^="ReflexRules-otherWS-"]').bind("change", function () {
            otherWS_controller(row);
        }).trigger('change');
        $(row).find('select[id^="ReflexRules-action-"]').bind("change", function () {
            action_select_controller(row, false);
        });
        $(row).find('select[id^="ReflexRules-setresulton-"]').bind("change", function () {
            setresulton_controller(row);
        });
        $(row).find('select[id^="ReflexRules-action-"]').trigger('change');
    }

    function add_action_set(element){
        /**
        :element: is the more(addnew) button
        This function defines the process to add a new whole action and
        conditions set
        */
        var fieldname = $(element).attr("id").split("_")[0];
        var table = $('#'+fieldname+"_table");
        var sets = $(".records_row_"+fieldname);
        // clone last set of actions
        var set = $(sets[sets.length-1]).clone();
        // Hide the delete button from the right of the previous set
        $(sets[sets.length-1]).find('.rw_deletebtn').hide();
        // Remove actions and empty selectors
        $(set).find("select[id^='ReflexRules-analysisservice-']").find('option').remove();
        $(set).find("div.action:gt(0)").remove();
        // after cloning, make sure the new element's IDs are unique
        var found = $(set).find(
                "input[id^='"+fieldname+"']," +
                "select[id^='"+fieldname+"']," +
                "div[id^='ReflexRules-actionsset-']");
        for (var ii = found.length - 1; ii >= 0; ii--) {
            var prefix, nr;
            var ID = found[ii].id;
            if (ID.split('-').length == 4){
                // It is an action row
                prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
                var sufix = ID.split("-")[3];
                nr = parseInt(ID.split("-")[2]) + 1;
                $(found[ii]).attr('id', prefix + "-" + nr + "-" + sufix);
            }
            else if (ID.split('-').length == 3) {
                // It is not an action row
                prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
                nr = parseInt(ID.split("-")[2]) + 1;
                $(found[ii]).attr('id', prefix + "-" + nr);
            }
        }
        // clear values
        var td = $(set).children().first();
        var input = $(td).find('input')
            .not('.addnew');
        $(input).val('');
        var sel_options = $(td).find(":selected");
        $(sel_options).prop("selected", false);
        // Adding the new set to the table
        $(set).appendTo($(table));
        // Binding the controllers
        // Range result controller
        $(set)
            .find('input[id^="ReflexRules-range"]')
            .bind("change", function () {
                range_controller($(set).find('input[id^="ReflexRules-range"]'));
                setup_del_action_button();
        });
        // Show the rw_deletebtn button
        $(set).find(".rw_deletebtn").show();
        $(set).delegate('.rw_deletebtn', 'click', function() {
            // Display the delete button from the previous derivative rule
            var tr = $(this).closest('tr').prev();
            if (!$(tr).hasClass('rulenumber-0')){
                $(tr).find('.rw_deletebtn').show();
            }
        });
        // Action trigger controller
        $(set)
            .find('select[id^="ReflexRules-trigger"]')
            .bind("change", function () {
                trigger_controller(
                        $(set).find('select[id^="ReflexRules-trigger"]'));
        }).trigger("change");
        // "Add new" button controller
        $(set).find("input[id$='_action_addnew']").click(function(i,e){
            add_action_row(this);
        });
        // Binding the otherWS controller and the controller for specific
        // actions select
        $(set).find('div[id^="ReflexRules-actionsset-"] div.action')
            .bind("change", function () {
                otherWS_controller(this);
                setresulton_controller(this);
                action_select_controller(this, false);
            }).trigger('change');
        // Binding the and_or controller
        $(set)
            .find('div.conditionscontainer select.and_or')
            .bind("change", function () {
                and_or_controller(
                        $(set).find('div.conditionscontainer'));
        }).trigger("change");
        $(set).find('select[id^="ReflexRules-and_or-"]').show();
        if($(td).hasClass('rulenumber')){
            var idx = $(td).find('input.rulenumber').attr('originalvalue');
            var new_idx = parseInt(idx) + 1;
            $(td).find('input.rulenumber').attr('originalvalue', new_idx);
            $(td).find('span').html('# ' + new_idx);
            $(td).parent('tr').removeClass('rulenumber-'+idx).addClass('rulenumber-'+new_idx);
        }
        update_analysis_selectors();
    }

    function setup_del_action_button(){
        /**
        This function defines the process to do after clicking on the
        delete button of an action row
        */
        $(".action_deletebtn").live('click', function(i,e){
            var div = $(this).parent();
            var siblings = $(div).siblings();
            if (siblings.length < 2) return;
            $(this).parent().remove();
            update_analysis_selectors();
        });
    }

    function setup_as_and_discrete_results(setupdata){
        /**
        This function checks the main analysis service and shows/hides the expected
        values fields. It also selects the saved option if the expected result
        is discrete
        */
        // Select the option
        var rules = $.parseJSON($('#rules-setup-data')
            .html()).saved_actions.rules;
        var ass = $('select[id^="ReflexRules-analysisservice-"]').first();
        var action_sets = $('div.actions-set');
        var discrete;
        $.each(ass,function(index, element){
            // Select the analysis service
            if (rules[index] !== undefined){
                var as = rules[index].conditions[0].analysisservice;
                $(element).find('option[value="'+ as + '"]')
                    .prop("selected", true);
                // Write the options
                analysiservice_change(element, setupdata);
            } else {
                analysiservice_change(element, setupdata);
            }
        });

        if (rules.length > 0) {
            discrete = rules[0].conditions[0].discreteresult;
            $('#ReflexRules-discreteresult-0-0 option[value="'+discrete+'"]').prop('selected', true);
        }

        // Updating the setresult selection list in the actions set
        /*for (var i=0; i < rules.length; i++) {
            // Need to iterate through each action
            for (var j=0; j < rules[i].actions.length; j++) {
                var discrete=rules[i].actions[j].setresultdiscrete;
                // Set the selected option to the corresponding selection list
                $('#ReflexRules-setresultdiscrete-'+i+'-'+j+' option[value="'+discrete+'"]').prop('selected', true);
            }
        }*/
        for (var i=0; rules.length > i; i++){
            discrete = rules[i].discreteresult;
            $(ass[i]).siblings('div.resultoptioncontainer')
                .find('select option[value="'+ discrete + '"]')
                .prop("selected", true);
            // Selecting the setresultdiscrete field values
            var actions_saved = rules[i].actions;
            var setresultdiscrete_fields = $(action_sets[i])
                .find('select[id^="ReflexRules-setresultdiscrete-"]');
            for (var ii=0; actions_saved.length > ii; ii++){
                var setresultdiscrete_saved = actions_saved[ii].setresultdiscrete;
                if (actions_saved[ii].setresultdiscrete !== undefined) {
                    $(setresultdiscrete_fields[ii])
                        .find('option[value="'+ actions_saved[ii].setresultdiscrete + '"]')
                        .prop("selected", true);
                }
            }
        }
        // Set the discrete results to the conditions of derivative rules
        for (var k=1; k < rules.length; k++) {
            // Need to iterate through each action
            for (var j=0; j < rules[k].conditions.length; j++) {
                var disc=rules[k].conditions[j].discreteresult;
                // Set the selected option to the corresponding selection list
                $('#ReflexRules-discreteresult-'+k+'-'+j+' option[value="'+disc+'"]').prop('selected', true);
            }
        }
    }

    function setup_as(setupdata){
        /**
        This function selects the values for the not main analysis service
        selection lists.
        */
        var rules = setupdata.saved_actions.rules;
        var rulescontainers = $('td.rulescontainer').slice(1);
        $.each(rulescontainers,function(index1, element1){
            var ass = $(element1).find('select[id^="ReflexRules-analysisservice-"]');
            var conditions = rules[index1+1].conditions;
            $.each(conditions,function(index2, element2){
                var as = element2.analysisservice;
                var input = ass[index2];
                $(input).find('option[value="'+ as + '"]')
                    .prop("selected", true);
            });
        });
    }

    /**
     * This function handles 'setvisibilityof' select elements' selected value
     * Parses setup data, and makes the proper option be selected.
     * @param {string} setupdata an object containing the setup data.
     */
    function setup_svof(setupdata){
        var rules = setupdata.saved_actions.rules;
        if(!rules || rules.length==0){
            return;
        }
        var rulescontainers = $('td.rulescontainer');

        $.each(rulescontainers,function(index1, element1){
            var action_set_div = $(element1).find('div[id^="ReflexRules-actionsset-"]');
            // 'action_divs' are "lines" of each 'action_set_div'.
            var action_divs = $(action_set_div).find('div[class="action"]');
            // This actions variable is actually actions sets.
            var actions = rules[index1].actions;

            $.each(action_divs,function(index2, element2){
                // Now from each "line", we are getting select element.
                var sv_select = $(element2).find('select[id^="ReflexRules-setvisibilityof-"]');
                sv = actions[index2].setvisibilityof;
                $(sv_select).find('option[value="'+ sv + '"]')
                    .prop("selected", true);
            });

        });
    }

    /**
     * This function looks for all worksheet template 'select' elements and
     * selects their option takeing in consideration the setupdata.
     * @param {string} setupdata an object containing the setup data.
     */
    function setup_worksheettemplate(setupdata){
        var rules = setupdata.saved_actions.rules;
        if(!rules || rules.length==0){
            return;
        }
        var rulescontainers = $('td.rulescontainer');
        $.each(rulescontainers,function(index1, element1){
            var wsts = $(element1).find('select[id^="ReflexRules-worksheettemplate-"]');
            var actions = rules[index1].actions;
            $.each(actions,function(index2, element2){
                var wst = element2.worksheettemplate;
                var input = wsts[index2];
                $(input).find('option[value="'+ wst + '"]')
                    .prop("selected", true);
            });
        });
    }

    function otherWS_controller(action_div){
        /**
        This function hide/shows the selection of an analyst and the worksheet
        template deppending on the option selected.
        */
        var selection = $(action_div).find('select[id^="ReflexRules-otherWS-"]')
            .find(":selected").attr('value');
        if (selection == "to_another" || selection == 'create_another') {
            // Showing the analyst-section div
            $(action_div).find('div.analyst-section').css('display', 'inline');
            // Showing the worksheet-template-section div
            $(action_div).find('div.worksheet-template-section').css('display', 'inline');
        }
        else{
            // Hide the options-set
            $(action_div).find('div.analyst-section').hide();
            // hide the worksheet-template-section div
            $(action_div).find('div.worksheet-template-section').hide();
        }
    }

    /**
     * This function sets local id for new action if the action is not setresult.
     * If ReflexRules-an_result_id list is empty this function will provide new local_id for the selected action
     * @param {element} action_div is initially selected element..
     */
    function set_action_select_value(action_div) {
        var local_id = '';
        var selection = $(action_div)
            .find('select[id^="ReflexRules-action-"]')
            .find(":selected").attr('value');
        if (selection != "setresult") {
            if($(action_div).find("input[id^='ReflexRules-an_result_id-']")
                .first().val() === ''){
                local_id = new_localid(selection);
                $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                    .first().val(local_id);}
        }
    }

    function action_select_controller(action_div, first_setup) {
        /**
        This function hide/shows the 'worksheet' section and 'defining analysis
        result' section deppending on the choosen action.
        - If 'define result' action is selected, hides the to_other_worksheet
        div and shows the action_define_result div.
        - If 'define result' action is NOT selected, shows the
        to_other_worksheet div and hides the action_define_result div.

        The function alse generates the local ids related to the selected action.

        @action_div: it is the division with the input actions.
        @first_setup: it is a boolean which is 'true' when the page is just
        being setting up and the local_ids do not have to be created.
        */
        var local_id = '';
        var selection = $(action_div)
            .find('select[id^="ReflexRules-action-"]')
            .find(":selected").attr('value');
        if (selection == "setresult") {
            // Hide the temporary ID for this analysis
            $(action_div).find('input[id^=ReflexRules-an_result_id-]').hide();
            // Showing the analyst-section div
            var action_define_div = $(action_div).find('div.action_define_result');
            $(action_define_div).css('display', 'inline');
            $(action_div).find('div.action_define_visibility').hide();
            $(action_div).find('div.to_other_worksheet').hide();
            $(action_div)
                .find('div.to_other_worksheet')
                .find('select[id^="ReflexRules-otherWS-"]').find(":selected")
                .prop("selected", false);
            // run the controlller for the elements contained in the 'div.action_define_result'
            action_define_div_controller(action_div);
            // Creates a new local id if a new analysis is created
            var set_new = $(action_div)
                .find("select[id^='ReflexRules-setresulton-']")
                .find(":selected").attr('value');
            if (set_new == 'new') {
                if (!first_setup){
                    local_id = new_localid(selection);
                    $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                        .first().val(local_id);
                }
                else{
                    local_id = $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                        .first().val();
                }
                update_analysis_selectors();
            }
            else{
                $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                    .first().val('');}
        }
        else if(selection=="setvisibility"){
            // Hide the temporary ID for this analysis
            $(action_div).find('input[id^=ReflexRules-an_result_id-]').hide();
            // Hide fields of the other actions
            $(action_div).find('div.action_define_result').hide();
            $(action_div).find('div.to_other_worksheet').hide();$(action_div)
                .find('div.to_other_worksheet')
                .find('select[id^="ReflexRules-otherWS-"]').find(":selected")
                .prop("selected", false);
            // Show analysis id selector
            $(action_div).find('div.action_define_visibility').show();
            local_id = $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                .first().val();
            update_analysis_selectors();
        }
        else{
            // Show the temporary ID of the analysis to be generated
            $(action_div).find('input[id^=ReflexRules-an_result_id-]').show();
            // Hide the options-set
            $(action_div).find('div.to_other_worksheet').css('display', 'inline');
            $(action_div).find('div.action_define_result').hide();
            $(action_div).find('div.action_define_visibility').hide();
            if (!first_setup){
                local_id = new_localid(selection);
                $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                    .first().val(local_id);
            }
            else{
                local_id = $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                    .first().val();
            }
            update_analysis_selectors();
        }
    }

    function action_define_div_controller(action_div){
        /**
        This functions hides/shows the input fields or selection lists depending
        on the selected analysis.
        @action_div is the div.action where the 'div.action_define_result'
        belongs to.
        */
        // Populate the analysis selection list
        var rulescontainer = $(action_div).closest('td.rulescontainer');
        // Getting the selected services inside conditions div (the first one so far)
        var as = $('select[id^="ReflexRules-analysisservice-"]')
            .first()[0];
        //Check if the selected analysis service has discrete values
        var method = $('select[id="Method"]').find(":selected").attr('value');
        var as_uid = $(as).find(":selected").attr('value');
        var setupdata = $.parseJSON($('#rules-setup-data').html());
        var as_info = setupdata[method].analysisservices[as_uid];
        if (as_info === undefined){
            var _ = window.jarn.i18n.MessageFactory("senaite.core");
            window.bika.lims.portalMessage(_('An analysis service must be selected'));
        }
        var resultoptions = as_info.resultoptions;
        if(resultoptions.length > 0){
            // If the analysis service possible results are discrete, hide the
            // input and show the selection list
            $(action_div)
                .find('input[id^="ReflexRules-setresultvalue-"]').hide().val('');
            $(action_div)
                .find('select[id^="ReflexRules-setresultdiscrete-"]').show();
        }
        else{
            // If the analysis service possible results aren't discrete, show the
            // input and hide the selection list
            $(action_div)
                .find('input[id^="ReflexRules-setresultvalue-"]').show();
            $(action_div)
                .find('select[id^="ReflexRules-setresultdiscrete-"]').hide();
        }
    }

    function setresulton_controller(action_div) {
        /**
        This function checks if the selected value in the
        'ReflexRules-setresulton' selectoin list is 'new'. If it is new, the
        function creates a new local id for the analysis.
        @action_div: the div.action
        **/
        // Creates a new local id if a new analysis is created
        var local_id = '';
        var selection = $(action_div)
            .find('select[id^="ReflexRules-action-"]')
            .find(":selected").attr('value');
        var set_new = $(action_div)
            .find("select[id^='ReflexRules-setresulton-']")
            .find(":selected").attr('value');
        if (set_new == 'new') {
            local_id = new_localid(selection);
            $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                .first().val(local_id);
        } else{
            $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                .first().val('');}
    }

    /**
     * Looks for the last on-fly-generated identifier (e.g. dup-1, dup-2, etc.)
     * with the specified prefix and returns the contiguous id (if the last
     * identifier for prefix "dup" was "dup-1", this method retursn "dup-2")
     * @param {string} prefix a string like 'rep', 'dup', 'set', 'repeat',
     *                        'setresult', 'duplicate'
     * @return {string} The next id contiguous id with the prefix indicated
     */
    function new_localid(prefix) {
        // Getting the local ids dictionary
        var rawprefix = prefix == 'duplicate' ? 'dup' : prefix;
        rawprefix = rawprefix == 'repeat' ? 'rep' : rawprefix;
        rawprefix = rawprefix == 'setresult' ? 'set' : rawprefix;
        var maxnum = 0;
        $('.derivative-id').each(function(index, element) {
            var valid = $(this).val();
            if (valid.match("^"+rawprefix+"-")) {
                var num = valid.split(/-/);
                num = parseInt(num[1]);
                maxnum = num > maxnum ? num : maxnum;
            }
        });
        return rawprefix+"-"+(maxnum+1);
    }

    /**
     * Refresh the analysis selection lists from derivative rules with
     * on-fly-generated identifiers (e.g. dup-1, rep-1, dup-2, etc.). In a
     * selection list from a derivative rule, only those identifiers generated
     * in previous derivative rules or in the main rule will be used. This is,
     * a dup-3 generated in a derivative #3 will not be available in derivative
     * rules #1 neither #2.
     */
    function update_analysis_selectors() {
        // Getting the selectors from the containers. We explicitily discard
        // the first selector cause it belongs to the top-level rule (we only
        // want to update the selectors from derivative rules).
        var selectors = $("select[id^='ReflexRules-analysisservice-']:gt(0)");
        // Add the new local-id as a new the options
        $.each($(selectors), function(index, element){
            var options = [];
            var selected = $('#'+$(element).attr('id')+" :selected").text();
            $(element).find('option').remove();
            // We fetch the local-ids from previous rows (rules)
            var prevtr = $(element).closest('tr').prev();
            while ($(prevtr).hasClass('records_row_ReflexRules')) {
                $(prevtr).find('.derivative-id').each(function(index, el2) {
                    var did = $(el2).val();
                    if (did !== '') {
                        var optd = did == selected ? " selected" : "";
                        options.push('<option value="'+did+'"'+optd+'>'+did+'</option>');
                    }
                });
                prevtr = $(prevtr).prev();
            }
            // Sort the options and add them to the selection list
            options = options.sort();
            $(element).append(options.join(''));
        });
        // Now update analysis selectors of 'setvisibility' actions.
        update_visibility_selectors();
    }

    /**
     * This function updates analysis local ids in 'setvisibilityof' options list.
     * Onnly ids form previous containers can be added. Also adding 'Orginial Analysis'
     * since it doesn't have a local id.
     */
    function update_visibility_selectors() {
        // Getting the selectors from the containers.
        var selectors = $("select[id^='ReflexRules-setvisibilityof-']");
        $.each($(selectors), function(index, element){
            var options = [];
            var selected = $('#'+$(element).attr('id')+" :selected").text();
            $(element).find('option').remove();
            // We fetch the local-ids from previous rows (rules)
            var prevtr = $(element).closest('tr').prev();
            while ($(prevtr).hasClass('records_row_ReflexRules')) {
                $(prevtr).find('.derivative-id').each(function(index, el2) {
                    var did = $(el2).val();
                    if (did !== '') {
                        var optd = did == selected ? " selected" : "";
                        options.push('<option value="'+did+'"'+optd+'>'+did+'</option>');
                    }
                });
                prevtr = $(prevtr).prev();
            }
            // Add Original analysis to the list,
            // sort the options and add them to the selection list
            options.push('<option value="original">Original Analysis</option>');
            options = options.sort();
            $(element).append(options.join(''));
        });
    }
});
