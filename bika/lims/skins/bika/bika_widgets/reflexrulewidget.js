jQuery(function($){
    $(document).ready(function(){
        // This will be a global variable to be used everywhere
        method_controller();
        $('select#Method').bind("change", function () {
            method_controller();
        });
    });
    var method_analysis = $.parseJSON($('#methods-analysis').html());
    function method_controller(){
        /**
        This function updates the options in the analysis service selectors
        according to the selected method
        */
        var method = $('select[id="Method"]').find(":selected").attr('value');
        var ass = method_analysis[method].analysisservices;
        var ass_keys = method_analysis[method].as_keys;
        // Remove selection options
        $('select[id="ReflexRules-analysisservice-0"]')
            .find("option").remove();
        // Create an option for each analysis service obtained for
        // the current method
        for (var i=0; ass_keys.length > i; i++){
            $('select[id="ReflexRules-analysisservice-0"]').append(
                '<option value="' + ass_keys[i] +
                '">' + ass[ass_keys[i]].as_title + '</option>'
            );
        }
    }
});
