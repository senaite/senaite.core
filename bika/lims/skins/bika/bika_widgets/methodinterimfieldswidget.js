jQuery(function($){
$(document).ready(function(){

	$(".analysis_type").change(function(){
		pos = $(this).attr('pos');
		val = $(this).val();
		if(val == 'b' || val == 'c'){
			$(".sst_" + pos).toggle(true);
		} else {
			$(".sst_" + pos).toggle(false);
		}
		if(val == 'd'){
			$(".dup_" + pos).toggle(true);
		} else {
			$(".dup_" + pos).toggle(false);
		}
	});
	
});
});
