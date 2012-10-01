jQuery( function($) {
$(document).ready(function(){

	// Hide remarks field if this object is in portal_factory
	if(window.location.href.search("portal_factory") > -1) {
		$("#archetypes-fieldname-Remarks").toggle(false);
	}

	$('.saveRemarks').live('click', function(event){
		event.preventDefault();
		if ($("#Remarks").val() == '' ||
		    $("#Remarks").val() == undefined) {
			return false;
		}

		$("#archetypes-fieldname-Remarks fieldset span").load(
			$('#setRemarksURL').val() + "/setRemarksField",
			{'value': $("#Remarks").val(),
			 '_authenticator': $('input[name="_authenticator"]').val()}
		);
		$("#Remarks").val("");
		return false;
	});
	$("#Remarks").empty();

});
});


