jQuery( function($) {
$(document).ready(function(){

	// Confirm before resetting client specs to default lab specs
    $(".set_to_lab_defaults").click(function(event){
		// always prevent default/
		// url is activated manually from 'Yes' below.
		event.preventDefault();
		var $confirmation = $("<div></div>")
			.html(
				"This will remove all Client analysis specifications "+
				"and add copies of all Lab specifications. "+
				"Are you sure you want to do this?")
			.dialog({
				resizable:false,
				title: 'Confirm',
				buttons: {
					'Yes': function(event){
						$(this).dialog("close");
						window.location.href = $(".set_to_lab_defaults").attr("href");
					},
					'No': function(event){
						$(this).dialog("close");
					}
				}
			});
    });

});
});
