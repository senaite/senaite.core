jQuery( function($) {
$(document).ready(function(){

	_ = window.jsi18n;

	function autocomplete_sampletype(request,callback){
		$.getJSON('ajax_sampletypes', {'term':request.term}, function(data,textStatus){
			callback(data);
		});
	}

	function autocomplete_samplepoint(request,callback){
		$.getJSON('ajax_samplepoints', {'term':request.term}, function(data,textStatus){
			callback(data);
		});
	}

	// XXX Datepicker format is not i18n aware (dd Oct 2011)
	$(".datepicker").datepicker({'dateFormat': 'dd M yy', showAnim: ''});
	$("#SampleType").autocomplete({ minLength: 0, source: autocomplete_sampletype});
	$("#SamplePoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});

	$("#DateSampled").change(function(){
		$.getJSON('ajax_setDateSampled', {'date':$(this).val()}, function(data,textStatus){
			callback(data);
		});

	});

	$("#ClientReference").focus();

});
});
