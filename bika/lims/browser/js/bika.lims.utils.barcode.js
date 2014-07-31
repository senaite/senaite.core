(function( $ ) {
$(document).ready(function(){

    jarn.i18n.loadCatalog('bika');
	_ = jarn.i18n.MessageFactory('bika');
    jarn.i18n.loadCatalog('plone');
	PMF = jarn.i18n.MessageFactory('plone');

	// if collection gets something worth submitting,
	// it's sent to utils.barcode_entry here.
	function redirect(code){
		$.ajax({
			type: 'POST',
			url: 'barcode_entry',
			data: {'entry':code.replace("*",""),
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

	$(window).keypress(function(event) {
		if (collecting) {
			// short-circuit tineout when ending * is reached
			if (event.which == "42"){
				collecting = false;
				redirect(code);
			}
			code = code + String.fromCharCode(event.which);
		} else {
			// valid barcodes will start and end with "*"
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
	});

// XXX This doesn't work for me unless the javascript gets inserted directly into the outputted HTM.
//    barcodes = $(".barcode");
//	for (e = 0; e < barcodes.length; e++){
//		$(barcodes[e]).barcode('*'+$(barcodes[e]).attr('value').split('_')[1]+'*', "code128",
//			{'barHeight':15, addQuietZone:false, showHRI: false });
//
//	}


});
}(jQuery));
