jQuery( function($) {
$(document).ready(function(){

	// Hide remarks field if this object is in portal_factory
	// I will cheat: in Batch context, lemoene wants Remarks to be displayed during object
	// creation.  However this means the form cannot get ajax submitted - the value must
	// be sent directly through like a normal field.
	if(window.location.href.search("portal_factory") > -1
	  && $(".portaltype-batch.template-base_edit").length == 0) {
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


