jQuery( function($) {
$(document).ready(function(){

	// if collection gets something worth submitting,
	// it's sent to utils.getObject here.
	function redirect(code){
		$.ajax({
			type: 'POST',
			url: 'getObject',
			data: {'id':code,
					'_authenticator': $('input[name="_authenticator"]').val()},
			success: function(responseText, statusText, xhr, $form) {
				if (responseText) {
					window.location.href = responseText;
				}
			}
		});
	}

	var collecting = false;
	var code = ""

	$(document).keypress(function(event) {
		// 42 = *
		if (collecting) {
			code = code + String.fromCharCode(event.which);
			if(event.which == 55) { //
				collecting = false;
				redirect(code);
			}
		} else {
			if(event.which == 54) {
				collecting = true;
				code = String.fromCharCode(event.which);
				setTimeout(function(){
					if(collecting == true && code != ""){
						collecting = false;
						redirect(code);
					}
				}, 500)
			}
		}
	});

    $.each($(".barcode"), function(i,v){
		$(v).barcode('*'+$(v).attr('value')+'*', "code39");
	});


});
});


