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
		if(event.target != document.documentElement){ return; }
//		$("input, textarea, select").live('keypress', function(event) {
		// 42 = *
		if (collecting) {
			code = code + String.fromCharCode(event.which);
//			if(event.which == 55) { //
//				collecting = false;
//				redirect(code);
//			}
		} else {
//			if(event.which == 54) {
				collecting = true;
				code = String.fromCharCode(event.which);
				setTimeout(function(){
					if(collecting == true && code != ""){
						collecting = false;
						//console.log("redirect: " + code)
						redirect(code);
					}
				}, 500)
//			}
		}
	});

// XXX ended up putting this inline from python view.  ?
//    barcodes = $(".barcode");
//	for (e = 0; e < barcodes.length; e++){
//		$(barcodes[e]).barcode('*'+$(barcodes[e]).attr('value').split('_')[1]+'*', "code39",
//			{'barHeight':15, addQuietZone:false, showHRI: false });
//
//	}


});
});


