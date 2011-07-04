jQuery( function($) {
$(document).ready(function(){

	$(".analysis_entry").live('change', function(){
		options = {
			type: 'POST',
			url: 'analysis_entry',
			data: {
				'uid': $(this).attr('uid'),
				'field': $(this).attr('field'),
				'value': $(this).attr('value'),
				'_authenticator': $('input[name="_authenticator"]').val()
			},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				alert(data);
			}
		}
		$.ajax(options);
	});

});
});
