jQuery(function($){
    $(document).ready(function(){
        // This will be a variable to be used everywhere
        var setupdata = $.parseJSON($('#rules-setup-data').html());
        method_controller(setupdata);
        remove_last_rule_set();
        setup_addnew_buttons();
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
        This function defines the process to add a new action row
        */
        var row = $(element).prev('div').clone();
        var found = $(row).find("input, select");
        for (var i = found.length - 1; i >= 0; i--) {
            var prefix, nr;
            var ID = found[i].id;
            prefix = ID.split("-")[0] + "-" + ID.split("-")[1];
            var sufix = parseInt(ID.split("-")[3]) + 1;
            nr = ID.split("-")[2];
            $(found[i]).attr('id', prefix + "-" + nr + "-" + sufix);
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
    }

    function add_action_set(element){
        /**
        This function defines the process to add a new whole action set
        */
        var fieldname = $(element).attr("id").split("_")[0];
        var table = $('#'+fieldname+"_table");
        var rows = $(".records_row_"+fieldname);
        // clone last row
        var row = $(rows[rows.length-1]).clone();
        // after cloning, make sure the new element's IDs are unique
        var found = $(row).find(
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
        for(var i=0; i<$(row).children().length; i++){
            var td = $(row).children()[i];
            var input = $(td).find('input').not('.addnew');
            $(input).val('');
            var sel_options = $(td).find(":selected");
            $(sel_options).prop("selected", false);
        }
        // Binding the controllers
        $(row)
            .find('input[id^="ReflexRules-range"]')
            .bind("change", function () {
                range_controller(element);
                setup_del_action_button();
            });
        $(row).appendTo($(table));
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
});
