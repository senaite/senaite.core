jQuery( function($) {
$(document).ready(function(){

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


