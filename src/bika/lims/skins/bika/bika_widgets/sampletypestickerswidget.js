jQuery(function($){
    $(document).ready(function(){
        // Controller for admitted stickers multi selection input.
        $("#AdmittedStickerTemplates-admitted-0")
            .bind('change', function(){
                on_admitted_change();
            }
         );
    });
    /**
    * When "admitted sticker selection" input changes, "default small" and
    * "default large" selector options must be updated in acordance with the
    * new admitted options.
    * @return {None} nothing.
    */
    function on_admitted_change(){
        // Get admitted options
        var admitted_ops = $("#AdmittedStickerTemplates-admitted-0")
            .find('option:selected');

        // Clean small/large select options
        $("#AdmittedStickerTemplates-small_default-0").find('option').remove();
        $("#AdmittedStickerTemplates-large_default-0").find('option').remove();

        // Set small/large options from admitted ones
        var i;
        var small_opt_clone;
        var large_opt_clone;
        for(i=0; admitted_ops.length > i; i++){
            small_opt_clone = $(admitted_ops[i]).clone();
            $("#AdmittedStickerTemplates-small_default-0")
                .append(small_opt_clone);
            large_opt_clone = $(admitted_ops[i]).clone();
            $("#AdmittedStickerTemplates-large_default-0")
                .append(large_opt_clone);
        }
        // Select the last cloned option. This way we give a value to the
        // selected input.
        if (small_opt_clone != undefined){
            $(small_opt_clone).attr('selected', 'selected');
        }
        if (large_opt_clone != undefined){
            $(large_opt_clone).attr('selected', 'selected');
        }
    }

});
