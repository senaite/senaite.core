jQuery( function($) {
$(document).ready(function(){

	_ = window.jsi18n;

	$("#analysestotals_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysestotals").toggle(true);
	});
	$("#analysespersampletype_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysespersampletype").toggle(true);
	});
	$("#analysesperclient_selector, #memberanalysesperclient_selector")
		.click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysesperclient").toggle(true);
	});
	$("#tats_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#tats").toggle(true);
	});
	$("#attachments_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#attachments").toggle(true);
	});
	$("#analysesoutofrange_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysesoutofrange").toggle(true);
	});
	$("#analysesrepeated_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysesrepeated").toggle(true);
	});
	$("#resultspersamplepoint_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#resultspersamplepoint").toggle(true);
	});
	$("#standardanalysisqc_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#standardanalysisqc").toggle(true);
	});
	$("#duplicateanalysisqc_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#duplicateanalysisqc").toggle(true);
	});
	$("#arsnotinvoiced_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#arsnotinvoiced").toggle(true);
	});

});
});
