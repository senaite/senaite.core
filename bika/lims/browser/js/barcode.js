jQuery( function($) {
$(document).ready(function(){

	jarn.i18n.loadCatalog('bika');
	_ = jarn.i18n.MessageFactory('bika');

	// if collection gets something worth submitting,
	// it's sent to utils.getObject here.
	function redirect(code){
		code = code.replace("*","");
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
		if(event.target == document.documentElement){
			if (collecting) {
				code = code + String.fromCharCode(event.which);
			} else {
				// valid barcodes start with "*"
				if (event.which == "42") {
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
		}
	});

// XXX This doesn't work for me unless the javascript gets inserted directly into the outputted HTM.
//    barcodes = $(".barcode");
//	for (e = 0; e < barcodes.length; e++){
//		$(barcodes[e]).barcode('*'+$(barcodes[e]).attr('value').split('_')[1]+'*', "code39",
//			{'barHeight':15, addQuietZone:false, showHRI: false });
//
//	}


});
});


