jQuery(function($){
    $(document).ready(function(){
        // This will be a variable to be used everywhere
        var setupdata = $.parseJSON($('#rules-setup-data').html());
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
        $('select[id^="ReflexRules-analysisservice-"]')
            .bind("change", function () {
                analysiservice_change(this, setupdata);
            });
        // Setting the ws and define result stuff
        $.each($('div.action'), function(index, element){
                otherWS_controller(element);
                action_select_controller(element);
            });
        // Binding the controllers
        $('input[id^="ReflexRules-otherWS-"]').bind("change", function () {
            otherWS_controller($(this).closest('div.action'));
        });
        $('select[id^="ReflexRules-action-"]').bind("change", function () {
                action_select_controller($(this).closest('div.action'));
            });
        // Setup the local ids
        setup_local_uids();
        // Controller on 'ReflexRules-setresulton' selection list
        $('select[id^="ReflexRules-setresulton-"]').bind("change", function () {
                setresulton_controller($(this).closest('div.action'));
            });
    });

    function method_controller(setupdata){
        /**
        This function updates the options in every rule
        according to the selected method
        */
        var method = $('select[id="Method"]').find(":selected").attr('value');
        // Getting the analysis service ralated to the method
        var ass = setupdata[method].analysisservices;
        var ass_keys = setupdata[method].as_keys;
        // Remove selection options
        $('select[id^="ReflexRules-analysisservice-"]')
            .find("option").remove();
        // Create an option for each analysis service obtained for
        // the current method
        for (var i=0; ass_keys.length > i; i++){
            $('select[id^="ReflexRules-analysisservice-"]').append(
                '<option value="' + ass_keys[i] +
                '">' + ass[ass_keys[i]].as_title + '</option>'
            );
        }
        var as_dom = $('select[id^="ReflexRules-analysisservice-"]');
        $.each(as_dom,function(index, element){
            $(element).trigger("change");
        });
    }

    function analysiservice_change(as, setupdata){
        /**
        This function hides/shows the expected result fields accordingly with
        the analysis service. It also loads the available options for expected
        discrete results.
        */
        var method = $('select[id="Method"]').find(":selected").attr('value');
        //Check if the selected analysis service has discrete rules
        var as_uid = $(as).find(":selected").attr('value');
        var as_info = setupdata[method].analysisservices[as_uid];
        if (as_info === undefined){
            var _ = window.jarn.i18n.MessageFactory("bika");
            window.bika.lims.portalMessage(_('An analysis service must be selected'));
        }
        else{
            var resultoptions = as_info.resultoptions;
            if(resultoptions.length > 0){
                // If the analysis service has discrete values, lets hide the range
                // inputs and display the result selector with all the possible
                // results for the analysis service
                // "Expected results" section
                $(as).siblings('.rangecontainer').hide().find('input').val('');
                $(as).siblings('.resultoptioncontainer').show();
                // Delete old options
                var select = $(as).siblings('.resultoptioncontainer').find('select');
                $(select).find('option').remove();
                // Actions section
                var select_actionset = $(as).siblings('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete']");
                $(as).siblings('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete']")
                    .show();
                // Delete old options
                $(as).siblings('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete'] option")
                    .remove();
                $(as).siblings('div.actions-set')
                    .find("input[id^='ReflexRules-setresultvalue']")
                    .hide().val('');
                // Write the different options in both sites
                for (var i=0; resultoptions.length > i; i++){
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
                $(as).siblings('.resultoptioncontainer').hide();
                $(as).siblings('.rangecontainer').show();
                var opts = $(as).siblings('.resultoptioncontainer').find('option');
                $(opts).remove();
                // Hide the fields in the action sections
                $(as).siblings('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete']")
                    .hide();
                // Delete old options
                $(as).siblings('div.actions-set')
                    .find("select[id^='ReflexRules-setresultdiscrete'] option")
                    .remove();
                $(as).siblings('div.actions-set')
                    .find("input[id^='ReflexRules-setresultvalue']")
                    .show();
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
            // Binding the analysis service controller
            $(container_clone).find('select[id^="ReflexRules-analysisservice-"]')
                .bind("change", function () {
                analysiservice_change(this, setupdata);
            });
            // Trigger the controller
            $(container_clone).find('select[id^="ReflexRules-analysisservice-"]')
                .trigger('change');
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
        $(row).find('input[id^="ReflexRules-otherWS-"]').bind("change", function () {
            otherWS_controller(row);
        });
        $(row).find('select[id^="ReflexRules-action-"]').bind("change", function () {
            action_select_controller(row);
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
        // Analysis service change controller
        $(set)
            .find('select[id^="ReflexRules-analysisservice-"]')
            .bind("change", function (element) {
                var setupdata = $.parseJSON($('#rules-setup-data').html());
                analysiservice_change(element.target, setupdata);
            }).trigger("change");
        // Binding the otherWS controller and the controller for specific
        // actions select
        $(set).find('div[id^="ReflexRules-actionsset-"] div.action')
            .bind("change", function () {
                otherWS_controller(this);
                setresulton_controller(this);
                action_select_controller(this);
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
        }
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
        });
    }

    function setup_as_and_discrete_results(setupdata){
        /**
        This function checks each analysis service and shows/hides the expected
        values fields. It also selects the saved option if the expected result
        is discrete
        */
        // Select the option
        var rules = $.parseJSON($('#rules-setup-data')
            .html()).saved_actions.rules;
        var ass = $('select[id^="ReflexRules-analysisservice-"]');
        var action_sets = $('div.actions-set');
        $.each(ass,function(index, element){
            // Select the analysis service
            if (rules[index] !== undefined){
                var as = rules[index].analysisservice;
                $(element).find('option[value="'+ as + '"]')
                    .prop("selected", true);
                // Write the options
                analysiservice_change(element, setupdata);
            }
            else{analysiservice_change(element, setupdata);}
        });
        // Updating the setresult selection list in the actions set
        for (var i=0; rules.length > i; i++){
            var discrete = rules[i].discreteresult;
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
    }

    function otherWS_controller(action_div){
        /**
        This function hide/shows the selection of an analyst deppending on the
        checkbox state
        */
        var checkbox = $(action_div).find('input[id^="ReflexRules-otherWS-"]').attr('checked');
        if (checkbox == "checked") {
            // Showing the analyst-section div
            $(action_div).find('div.analyst-section').css('display', 'inline');
        }
        else{
            // Hide the options-set
            $(action_div).find('div.analyst-section').hide();
        }
    }

    function action_select_controller(action_div) {
        /**
        This function hide/shows the 'worksheet' section and 'defining analysis
        result' section deppending on the choosen action.
        - If 'define result' action is selected, hides the to_other_worksheet
        div and shows the action_define_result div.
        - If 'define result' action is NOT selected, shows the
        to_other_worksheet div and hides the action_define_result div.

        The function alse generates the local ids related to the selected action.
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
            $(action_div).find('div.to_other_worksheet').hide();
            $(action_div)
                .find('div.to_other_worksheet')
                .find('input[id^="ReflexRules-otherWS-"]')
                .removeAttr("checked");
            // run the controlller for the elements contained in the 'div.action_define_result'
            action_define_div_controller(action_div);
            // Creates a new local id if a new analysis is created
            var set_new = $(action_div)
                .find("select[id^='ReflexRules-setresulton-']'")
                .find(":selected").attr('value');
            if (set_new == 'new') {
                local_id = create_local_id(selection);
                $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                    .first().val(local_id);
                populate_analysis_selection(local_id);
            }
            else{
                $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                    .first().val('');}
        }
        else{
            // Show the temporary ID of the analysis to be generated
            $(action_div).find('input[id^=ReflexRules-an_result_id-]').show();
            // Hide the options-set
            $(action_div).find('div.to_other_worksheet').css('display', 'inline');
            $(action_div).find('div.action_define_result').hide();
            local_id = create_local_id(selection);
            $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                .first().val(local_id);
            populate_analysis_selection(local_id);
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
        var as = $(rulescontainer).find('select[id^="ReflexRules-analysisservice-"]')
            .first();
        //Check if the selected analysis service has discrete values
        var method = $('select[id="Method"]').find(":selected").attr('value');
        var as_uid = $(as).find(":selected").attr('value');
        var setupdata = $.parseJSON($('#rules-setup-data').html());
        var as_info = setupdata[method].analysisservices[as_uid];
        if (as_info === undefined){
            var _ = window.jarn.i18n.MessageFactory("bika");
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

    function setup_local_uids() {
        /**
        This function sets up the local ids used to identify the analysis
        resulted from the different actions
        */
        // Getting the dict of local ids
        var local_ids = $.parseJSON($('#reflex_rule_analysis_ids').val());
        // no ids means a new refles rule
        if (local_ids === null){
            var new_id = '';
            // Set up the first local id
            // Getting the first action
            var first_action = $("select[id^='ReflexRules-action-']")
                .first().find(":selected").attr('value');
            if (first_action == 'duplicate' || first_action == 'repeat'){
                // If it is a duplicate, the local id will be dup-0
                new_id = create_local_id(first_action);
            }
            else if (first_action == 'setresult' &&
                $("select[id^='id='ReflexRules-setresulton-']")
                .first().find(":selected").attr('value') == 'new') {
                // If it is a 'set result on new analysis', the local id
                // will be set-0
                new_id = create_local_id(first_action);
            }
            // If the new local id has been created, insert into the
            // 'ReflexRules-an_result_id-' input
            if (new_id) {
                $("input[id^='ReflexRules-an_result_id-']").first().val(new_id);
            }
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
            .find("select[id^='ReflexRules-setresulton-']'")
            .find(":selected").attr('value');
        if (set_new == 'new') {
            local_id = create_local_id(selection);
            $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                .first().val(local_id);
        }
        else{
            $(action_div).find("input[id^='ReflexRules-an_result_id-']")
                .first().val('');}
    }

    function create_local_id(action_type) {
        /**
        This function mainly creates a new local id.
        It gets the string 'action_type' which is one of the possible actions
        that refex rules can do: 'repeat', 'duplicate' or 'setresult'. Then the
        function creates a new name taking into account the action type and the
        are already existen ones.
        @action_type: a string 'repeat', 'duplicate' or 'setresult'
        @return: a string with the new local id
        */
        var new_local_id = '';
        var local_ids_dic = $.parseJSON($('#reflex_rule_analysis_ids').val());
        if (local_ids_dic === null){
                local_ids_dic = {'dup':[], 'rep':[], 'set':[]};
            }
        if (action_type == 'duplicate'){
            new_local_id = return_next_id('dup');
            local_ids_dic.dup.push(new_local_id);
        }
        else if (action_type == 'repeat') {
            new_local_id = return_next_id('rep');
            local_ids_dic.rep.push(new_local_id);
        }
        else if (action_type == 'setresult') {
            new_local_id = return_next_id('set');
            local_ids_dic.set.push(new_local_id);
        }
        // Update the input#reflex_rule_analysis_ids with the new local id
        $('#reflex_rule_analysis_ids').val(JSON.stringify(local_ids_dic));
        return new_local_id;
    }

    function return_next_id(prefix) {
        /**
        This function looks for the next available local id with the prefix 'prefix'
        @prefix: a string like 'rep', 'dup', 'set'
        @return: a string as the new local id
        */
        // Getting the local ids dictionary
        var local_ids_dic = $.parseJSON($('#reflex_rule_analysis_ids').val());
        if (local_ids_dic === null){
                local_ids_dic = {'dup':[], 'rep':[], 'set':[]};
            }
        var new_local_id = '', local_ids_list = [], num=0,
            list_len, not_unique = 0;
        // Getting the local ids list
        local_ids_list = local_ids_dic[prefix];
        list_len = local_ids_list.length;
        // Create a new unique local id
        while(not_unique !== -1) {
            new_local_id = prefix + '-' + list_len.toString();
            not_unique = $.inArray(new_local_id, local_ids_list);
            list_len = list_len + 1;
        }
        return new_local_id;
    }

    function remove_local_id(array, id) {
        /**
        This function removes a local id to the 'reflex_rule_analysis_ids' div.
        @array: the array where the element will be removed.
        @id: the element to remove
        @return the resultant array.
        */
        var index = array.indexOf(id);
        if (index > -1) {
            array.splice(index, 1);
        }
        return array;
    }

    function populate_analysis_selection(local_id) {
        /**
        This function adds the recently created 'local_id' to the analysis
        services selection lists.
        */
        var option = '<option value="'+local_id+'">' + local_id + '</option>';
        // Getting the selectors from the containers
        var selectors = $('td.rulescontainer').slice(1)
            .find("select[id^='ReflexRules-analysisservice-']");
        var first_created = $('input#ReflexRules-an_result_id-0-0').val();
        // Add the new local-id as a new the options
        $.each($(selectors), function(index, element){
            // The first local_id is not added to the next list by itself, we
            // need to add it manualy if not added yet
            var already_added = $(element).find(
                'option[value="' + first_created + '"]');
            if (first_created !== undefined &&
                already_added.length < 1){
                var str2 = '<option value="'+first_created+'">' +
                    first_created + '</option>';
                option = option.concat(str2);
            }
            $(element).append(option);
        });
    }
});
