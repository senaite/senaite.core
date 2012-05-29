(function ($) {
$(document).ready(function(){

	_ = window.jsi18n;

	// If any required fields are missing, then we hide the Plone UI
	// transitions for Sampled and Preserved, and use our own buttons instead
	// (Save)
	if ($("#DateSampled").val() == "" || $("#Sampler").val() == "") {
		$("#workflow-transition-sampled").parent().toggle(false);
	}
	$("#workflow-transition-preserved").parent().toggle(false);

	function autocomplete_sampletype(request,callback){
		$.getJSON('ajax_sampletypes',
			{'term':request.term,
			 '_authenticator': $('input[name="_authenticator"]').val()},
			function(data,textStatus){
				callback(data);
			}
		);
	}
	function autocomplete_samplepoint(request,callback){
		$.getJSON('ajax_samplepoints',
			{'term':request.term,
			 '_authenticator': $('input[name="_authenticator"]').val()},
			function(data,textStatus){
				callback(data);
			}
		);
	}
	$("#SampleType").autocomplete({ minLength: 0, source: autocomplete_sampletype});
	$("#SamplePoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});

});
}(jQuery));
