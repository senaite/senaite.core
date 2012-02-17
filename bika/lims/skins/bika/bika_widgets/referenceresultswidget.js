jQuery(function($){
$(document).ready(function(){

	function calc_min_max(){
		uid = $(this).attr('uid');
		result = $("input[name='result."+uid+":records']").val();
		error = $("input[name='error."+uid+":records']").val();
		min_field = $("input[name='min."+uid+":records']")
		max_field = $("input[name='max."+uid+":records']")
		if (result != "" && error != ""){
			min_field.val(parseFloat(result) - parseFloat(result)/100 * parseFloat(error));
			max_field.val(parseFloat(result) + parseFloat(result)/100 * parseFloat(error));
		}
	}

	// "Result" and "Error" trigger min/max recalculation
	$("input[name*='result\\.']").live('change', calc_min_max);
	$("input[name*='error\\.']").live('change', calc_min_max);

});
});
