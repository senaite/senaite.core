jQuery(function($){

// When a reference definition is selected during edit,
// the code which transposes the definition onto this widget
// us in browser/js/referencesample.js

function calc_min_max(){
	tds = $($(this).parent().parent()[0]).children();
	result = $($(tds).children()[1]).val(); // 0 is hidden child with uid in it
	error = $($(tds).children()[2]).val();
	min_field = $($(tds).children()[3]);
	max_field = $($(tds).children()[4]);
	if (result != "" && error != ""){
		min_field.val(parseFloat(result) - parseFloat(result)/100 * parseFloat(error));
		max_field.val(parseFloat(result) + parseFloat(result)/100 * parseFloat(error));
	}
}

$(document).ready(function(){

	// "Result" and "Error" trigger min/max recalculation
	$("input[name='ReferenceResults.result:records:ignore_empty']")
		.live('change', calc_min_max);
	$("input[name='ReferenceResults.error:records:ignore_empty']")
		.live('change', calc_min_max);

});
});
