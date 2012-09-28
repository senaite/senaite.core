jQuery( function($) {
$(document).ready(function(){
	dateFormat = window.jsi18n_bika('date_format_short_datepicker');
	$('[datepicker=1]').datepicker({
		dateFormat: dateFormat,
		changeMonth:true,
		changeYear:true
	});
});
});
