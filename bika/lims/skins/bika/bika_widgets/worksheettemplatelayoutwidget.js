jQuery(function($){
$(document).ready(function(){

	$(".analysis_type").change(function(){
		pos = $(this).attr('pos');
		val = $(this).val();
		if(val == 'b') {
			$(".blank_ref_dropdown_" + pos).toggle(true);
		} else {
			$(".blank_ref_dropdown_" + pos).toggle(false);
		}
		if (val == 'c'){
			$(".control_ref_dropdown_" + pos).toggle(true);
		} else {
			$(".control_ref_dropdown_" + pos).toggle(false);
		}
		if(val == 'd'){
			$(".duplicate_analysis_dropdown_" + pos).toggle(true);
		} else {
			$(".duplicate_analysis_dropdown_" + pos).toggle(false);
		}
	});

});
});
