jQuery(function($){
    $(document).ready(function(){
        // This will be a variable to be used everywhere
        var setupdata = $.parseJSON($('#rules-setup-data').html());
        method_controller(setupdata);
        remove_last_rule_set();
        setup_as_and_discrete_results(setupdata);
        setup_addnew_buttons();
        setup_del_action_button();
        $.each($('div.action'), function(index, element){
                otherWS_controller(element);
            });
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
        $('select[id^="ReflexRules-analysisservice-"]')
            .bind("change", function () {
                analysiservice_change(this, setupdata);
            });
        $('input[id^="ReflexRules-otherWS-"]').bind("change", function () {
            otherWS_controller($(this).closest('div.action'));
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
        var resultoptions = as_info.resultoptions;
        if(resultoptions.length > 0){
            // If the analysis service has discrete values, lets hide the range
            // inputs and display the result selector with all the possible
            // results for the analysis service
            $(as).siblings('.rangecontainer').hide().find('input').val('');
            $(as).siblings('.resultoptioncontainer').show();
            // Delete old options
            var select = $(as).siblings('.resultoptioncontainer').find('select');
            $(select).find('option').remove();
            // Write the different options
            for (var i=0; resultoptions.length > i; i++){
                $(select).append(
                    '<option value="' + resultoptions[i].ResultValue +
                    '">' + resultoptions[i].ResultText + '</option>'
                );
            }
        }
        else{
            // If the analysis service has normal values, lets hide the discrete
            // values selector and remove its options
            $(as).siblings('.resultoptioncontainer').hide();
            $(as).siblings('.rangecontainer').show();
            var opts = $(as).siblings('.resultoptioncontainer').find('option');
            $(opts).remove();
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

    function setup_addnew_buttons(){
        /**
        Bind the process trigged after clicking on a 'more' button
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
        // Binding the otherWS controller
        $(row).bind("change", function () {
            otherWS_controller(this);
        });
    }

    function add_action_set(element){
        /**
        :element: is the more(addnew) button
        This function defines the process to add a new whole action set
        */
        var fieldname = $(element).attr("id").split("_")[0];
        var table = $('#'+fieldname+"_table");
        var sets = $(".records_row_"+fieldname);
        // clone last set of actions
        var set = $(sets[sets.length-1]).clone();
        // after cloning, make sure the new element's IDs are unique
        var found = $(set).find(
                "input[id^='"+fieldname+"']," +
                "select[id^='"+fieldname+"']");
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
            .not('.addnew')
            .not('[id^=ReflexRules-repetition_max-]');
        $(input).val('');
        var sel_options = $(td).find(":selected");
        $(sel_options).prop("selected", false);
        // Adding the new set to the table
        $(set).appendTo($(table));
        // Binding the controllers
        $(set)
            .find('input[id^="ReflexRules-range"]')
            .bind("change", function () {
                range_controller(element);
                setup_del_action_button();
            });
        $(set).find("input[id$='_action_addnew']").click(function(i,e){
            add_action_row(this);
        });
        $(set)
            .find('select[id^="ReflexRules-analysisservice-"]')
            .bind("change", function (element) {
                var setupdata = $.parseJSON($('#rules-setup-data').html());
                analysiservice_change(element.target, setupdata);
            }).trigger("change");
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
        for (var i=0; rules.length > i; i++){
            var discrete = rules[i].discreteresult;
            var ops = $(ass[i]).siblings('.resultoptioncontainer select option');
            $(ops).find('[value="'+ discrete + '"]').prop("selected", true);
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
});
