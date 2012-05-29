(function( $ ) {

function autocomplete_samplepoint(request,callback){
	$.getJSON(window.portal_url + "/ajax_samplepoints",
		{'term':request.term,
		 'sampletype':$("#SampleType").val(),
		 '_authenticator': $('input[name="_authenticator"]').val()},
		function(data,textStatus){
			callback(data);
		}
	);
}

function autocomplete_sampletype(request,callback){
	$.getJSON(window.portal_url + "/ajax_sampletypes",
		{'term':request.term,
		 'samplepoint':$("#SamplePoint").val(),
		 '_authenticator': $('input[name="_authenticator"]').val(),},
		function(data,textStatus){
			callback(data);
		}
	);
}

function setARProfile(){
	alert("artemplate.js setARProfile " + $(this).val());
}

$(document).ready(function(){

	_ = window.jsi18n;

	$("#SampleType").autocomplete({ minLength: 0, source: autocomplete_sampletype});
	$("#SamplePoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});
	$("#ARProfile\\:list").change(setARProfile);

});
}(jQuery));
