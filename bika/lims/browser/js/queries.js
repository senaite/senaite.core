jQuery( function($) {
$(document).ready(function(){

	_ = window.jsi18n;

	$("#analysisrequests_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysisrequests").toggle(true);
	});
	$("#orders_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#orders").toggle(true);
	});
	$("#invoices_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#invoices").toggle(true);
	});

});
});
