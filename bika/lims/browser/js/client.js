(function( $ ) {
$(document).ready(function(){

	_ = window.jsi18n;

	// Confirm before resetting client specs to default lab specs
    $("a[href*=set_to_lab_defaults]").click(function(event){
		// always prevent default/
		// url is activated manually from 'Yes' below.
		url = $(this).attr("href");
		event.preventDefault();
		yes = _('Yes');
		no = _('No');
		var $confirmation = $("<div></div>")
			.html(_("This will remove all existing client analysis specifications "+
					"and create copies of all lab specifications. "+
					"Are you sure you want to do this?"))
			.dialog({
				resizable:false,
				title: _('Set to lab defaults'),
				buttons: {
					yes: function(event){
						$(this).dialog("close");
						window.location.href = url;
					},
					no: function(event){
						$(this).dialog("close");
					}
				}
			});
    });

});
}(jQuery));
