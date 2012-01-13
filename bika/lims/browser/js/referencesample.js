jQuery( function($) {
$(document).ready(function(){

	// a reference definition is selected from the dropdown
	// see referenceresultswidget.js
	$('#ReferenceDefinition\\:list').change(function(){
		authenticator = $('input[name="_authenticator"]').val();
		uid = $(this).val();
		option = $(this).children(":selected").html();

		if (uid == '') {
			// No reference definition selected;
			// render empty widget.
			$("#Blank").attr("checked", false);
			$("#Hazardous").attr("checked", false);
			$('.bika-listing-table')
				.load('referenceresults', {'_authenticator': authenticator});
			return;
		}

		indicator_blank = $.trim($("#i18n_strings").attr("indicator_blank"));
		indicator_hazardous = $.trim($("#i18n_strings").attr("indicator_hazardous"));

		if(option.search(indicator_blank) > -1){
			$("#Blank").attr("checked", true);
		} else {
			$("#Blank").attr("checked", false);
		}

		if(option.search(indicator_hazardous) > -1){
			$("#Hazardous").attr("checked", true);
		} else {
			$("#Hazardous").attr("checked", false);
		}

		$('.bika-listing-table')
			.load('referenceresults',
				{'_authenticator': authenticator,
				 'uid':uid});
	});

	// If validation failed, and user is returned to page - requires reload.
	if ($('#ReferenceDefinition\\:list').val() != ''){
		$('#ReferenceDefinition\\:list').change();
	}

});
});
