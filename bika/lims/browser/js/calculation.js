jQuery( function($) {
$(document).ready(function(){

	$(".analysis_entry").live('change', function(){
		options = {
			type: 'POST',
			url = 'analysis_entry',
			async: false,
			data: {
				'uid': $(element).attr('id'),
				'_authenticator': $('input[name="_authenticator"]').val()},
			dataType: "json",
			success = function(pocdata,textStatus,$XHR){
			}
		}
	});

});
});
