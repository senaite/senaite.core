jQuery( function($) {

	$(document).ready(function(){
		// If we're in the worksheet folder listing
		//place the profile selector next to the add worksheet button.
		$('input[name="add_Worksheet"]').after("&nbsp;&nbsp;Using template: <Dropdown>");
	});

});
