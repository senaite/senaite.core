jQuery(function($){
    /** A variable to save the old selection to improve user exp
     It format will be:
     {'method-0':[{'analysisservice':'xas_uidx'}, {...}, ...], 'method-1':[...], ...}
     */
    var old_rules_selections = {};
    // This variable saves the last method uid selected. Must be updated
    // every time the user selects another method.
    var last_method = '';
    $(document).ready(function(){
        // This will be a variable to be used everywhere
        var setupdata = $.parseJSON($('#rules-setup-data').html());
        last_method = $('select[id="Method"]').find(":selected").attr('value');
        method_controller(setupdata);
        remove_last_rule();
        setup(setupdata);
        $('select#Method').bind("change", function () {
            save_old_method();
            // Updates the new method
            last_method = $('select[id="Method"]')
                .find(":selected").attr('value');
            $.each($('table#ReflexRules_table').find('.rw_deletebtn'),
                function(index, element){
                    $(element).trigger( "click" );
                });
            setupdata = $.parseJSON($('#rules-setup-data').html());
            method_controller(setupdata);
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
            // Write the old values if the user selects the previous method again
            $('select[id^="ReflexRules-analysisservice-"]').append(
                '<option value="' + ass_keys[i] +
                '">' + ass[ass_keys[i]].as_title + '</option>'
            );
        }
        if (old_rules_selections[method] !== undefined &&
            old_rules_selections[method].length > 0) {
            var rules_list = old_rules_selections[method];
            for (i=1; rules_list.length > i; i++) {
                $('#ReflexRules_more').click();
            }
            // Selecting the option
            set_ans_options(rules_list);
        }
    }

    function save_old_method(){
        // Save the current rules to be retrived if there is the need
        var ans = $('select[id^="ReflexRules-analysisservice-"]');
        var range0 = $('input[id^="ReflexRules-range0-"]');
        var range1 = $('input[id^="ReflexRules-range1-"]');
        var list = [];
        for (var i=0; ans.length > i; i++){
            var items = {
                analysisservice: ans[i].value,
                range0: range0[i].value,
                range1: range1[i].value,
            };
            list.push(items);
        }
        old_rules_selections[last_method] = list;

    }

    function set_ans_options(actions_list) {
        // Set the option to each analysis service select list using
        // the as_uids
        var rules_set = $('tr.records_row_ReflexRules');
        var ans = $('select[id^="ReflexRules-analysisservice-"]');
        var range0 = $('input[id^="ReflexRules-range0-"]');
        var range1 = $('input[id^="ReflexRules-range1-"]');
        if (rules_set.length !== 0){
            for (var i=0; rules_set.length > i; i++) {
                $("select#" + ans[i].id +
                    " option[value='" + actions_list[i].analysisservice + "']")
                    .prop('selected', true);
                $("input#" + range0[i].id).val(actions_list[i].range0);
                $("input#" + range1[i].id).val(actions_list[i].range1);
            }
        }
    }

    function setup(setupdata) {
        // This function retrives the data contained in the reflex rule
        // object and fill up the fields
        var actions_list = setupdata.saved_actions.actions;
        set_ans_options(actions_list);
    }

    function remove_last_rule(){
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
});
