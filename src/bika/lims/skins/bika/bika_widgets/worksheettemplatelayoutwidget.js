jQuery(function($){
$(document).ready(function(){

    $(".analysis_type").change(function(event){
        var this_pos = $(this).attr("pos");

        if ($(this).val() == 'a'){
            // analysis: clear b, c, d.
            $(".blank_ref_dropdown[pos='" + this_pos +"']").toggle(false);
            $(".control_ref_dropdown[pos='" + this_pos +"']").toggle(false);
            $(".duplicate_analysis_dropdown[pos='" + this_pos.toString() + "']").toggle(false);
        }
        else {
            // prevent further processing if this pos is a dup target.
            var duplicate_slots = find_slots_by_type('d');
            var dup_pos, e, src_slot;
            for (i = 0; i < duplicate_slots.length; i++) {
                dup_pos = duplicate_slots[i].toString();
                e = $(".duplicate_analysis_dropdown[pos='" + dup_pos + "']");
                dup_src = $($(e).parents("tr").find(".duplicate_analysis_dropdown")[0]).val();
                if (dup_src == this_pos && dup_pos != this_pos){
                    alert("Duplicate in position "+dup_pos+" references this, so it must be a routine analysis.");
                    $(this).val('a');
                    $(this).change();
                }
            }
            // handle b, c, d specifically.
            if ($(this).val() == 'b') {
                $(".blank_ref_dropdown[pos='" + this_pos +"']").toggle(true);
            }
            else if ($(this).val() == 'c') {
                $(".control_ref_dropdown[pos='" + this_pos +"']").toggle(true);
            }
            else if($(this).val() == 'd'){
                $(".duplicate_analysis_dropdown[pos='" + this_pos.toString() + "']").toggle(true);
                // build a list of routine analysis slots for the dup src list
                var e = $(".duplicate_analysis_dropdown[pos='" + this_pos + "']");
                $(e).show()
                $(e).empty();
                var routine_slots = find_slots_by_type('a');
                var nr;
                for (i = 0; i < routine_slots.length; ++i) {
                    nr = routine_slots[i].toString();
                    $(e).append($('<option value="'+nr+'">'+nr+'</option>'));
                }
            }
        }

    });

    function find_slots_by_type(type){
        // If an invalid slot is selected for a duplicate source,
        // and since the value is required and no blank selection is available,
        // we must find the first available "valid" slot and select it.
        var positions = [];
        for (var i=1; i < $('.analysis_type').length+1; i++){
            if ($(".analysis_type[pos='" + i.toString() + "']").val() == type){
                positions.push(i)
            }
        }
        return positions;
    }

});
});
