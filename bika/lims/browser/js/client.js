jQuery( function($) {
$(document).ready(function(){

	jarn.i18n.loadCatalog('bika');
	_ = jarn.i18n.MessageFactory('bika')

	// Confirm before resetting client specs to default lab specs
    $(".set_to_lab_defaults").click(function(event){
		// always prevent default/
		// url is activated manually from 'Yes' below.
		event.preventDefault();
		var $confirmation = $("<div></div>")
			.html(_("This will remove all existing client analysis specifications "+
					"and create copies of all lab specifications. "+
					"Are you sure you want to do this?"))
			.dialog({
				resizable:false,
				title: _('Set to lab defaults'),
				buttons: {
					_('Yes'): function(event){
						$(this).dialog("close");
						window.location.href = $(".set_to_lab_defaults").attr("href");
					},
					_('No'): function(event){
						$(this).dialog("close");
					}
				}
			});
    });

});
});
