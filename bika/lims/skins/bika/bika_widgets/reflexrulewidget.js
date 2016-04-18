jQuery(function($){
    /** A variable to save the old selection to improve user exp
     It format will be:
     {'method-0':[{'as_uid':'xxx'}, {...}, ...], 'method-1':[...], ...}
     */
     var old_method_selections = {};
    $(document).ready(function(){
        // This will be a global variable to be used everywhere
        var method_analysis = $.parseJSON($('#methods-analysis').html());
        method_controller(method_analysis);
        $('select#Method').bind("change", function () {
            save_old_method();
            $.each($('table#ReflexRules_table').find('.rw_deletebtn'),
                function(index, element){
                    $(element).trigger( "click" );
                });
            method_controller();
        });
    });
    function method_controller(method_analysis){
        /**
        This function updates the options in the analysis service selectors
        according to the selected method
        */
        var method = $('select[id="Method"]').find(":selected").attr('value');
        // Getting the analysis service ralated to the method
        var ass = method_analysis[method].analysisservices;
        var ass_keys = method_analysis[method].as_keys;
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
        if (old_method_selections[method] !== null &&
            old_method_selections[method].length > 0) {
                var ans_list = old_method_selections[method];
                for (i=0; ans_list.length > i; i++) {
                    $('#ReflexRules_more').click();
                }
                var ans = $('select[id^="ReflexRules-analysisservice-"]');
                for (i=0; ans.length > i; i++) {
                    $(ans[i] + ' option[value="' + ans_list[i].as_uid + '"]')
                        .prop('selected', true);
                }
            }
        }
    }

    function save_old_method(){
        // Save the current rules to be retrived if there is the need
        var method = $('select[id="Method"]').find(":selected").attr('value');
        if (old_method_selections[method] === null ||
            old_method_selections[method].length === 0) {
                var ans = $('select[id^="ReflexRules-analysisservice-"]');
                var list = [];
                for (var i=0; ans.length > i; i++){
                    var as = {
                        as_uid: ans[i].value,
                    };
                    list.push(as);
                }
                old_method_selections[method] = list;
            }
    }
});
