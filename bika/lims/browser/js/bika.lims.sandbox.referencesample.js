(function( $ ) {
$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
	_ = jarn.i18n.MessageFactory('bika');
    window.jarn.i18n.loadCatalog("plone");
	PMF = jarn.i18n.MessageFactory('plone');

	// a reference definition is selected from the dropdown
	// (../../skins/bika/bika_widgets/referenceresultswidget.js)
	$('#ReferenceDefinition\\:list').change(function(){
		authenticator = $('input[name="_authenticator"]').val();
		uid = $(this).val();
		option = $(this).children(":selected").html();

		if (uid == '') {
			// No reference definition selected;
			// render empty widget.
			$("#Blank").prop('checked',false);
			$("#Hazardous").prop('checked',false);
			$('.bika-listing-table')
				.load('referenceresults', {'_authenticator': authenticator});
			return;
		}

		if(option.search(_("(Blank)")) > -1){
			$("#Blank").prop('checked',true);
		} else {
			$("#Blank").prop('checked',false);
		}

		if(option.search(_("(Hazardous)")) > -1){
			$("#Hazardous").prop('checked',true);
		} else {
			$("#Hazardous").prop('checked',false);
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
}(jQuery));
