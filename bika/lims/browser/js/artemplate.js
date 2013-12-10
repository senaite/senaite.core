(function( $ ) {

	$(document).ready(function(){

		_ = jarn.i18n.MessageFactory('bika');
		PMF = jarn.i18n.MessageFactory('plone');

		function clickSaveButton(event){
			selected_analyses = $('[name^="uids\\:list"]').filter(':checked');
			if(selected_analyses.length < 1){
				window.bika.lims.portalMessage("No analyses have been selected");
				window.scroll(0, 0);
				return false;
			}
		}

		$(".portaltype-artemplate input[name$='save']").addClass('allowMultiSubmit');
		$(".portaltype-artemplate input[name$='save']").click(clickSaveButton);

	});
}(jQuery));


