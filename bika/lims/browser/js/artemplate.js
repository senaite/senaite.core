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

function portalMessage(message){
	str = "<dl class='portalMessage error'>"+
		"<dt>"+window.jsi18n("Error")+"</dt>"+
		"<dd><ul>" + window.jsi18n(message) +
		"</ul></dd></dl>";
	$('.portalMessage').remove();
	$(str).appendTo('#viewlet-above-content');
}

function clickSaveButton(event){
	selected_analyses = $('[name$="\\.Analyses"]').filter(':checked');
	if(selected_analyses.length < 1){
		portalMessage("No analyses have been selected");
		window.scroll(0, 0);
		return false;
	}
}

$(document).ready(function(){

	_ = window.jsi18n;

	$("#SampleType").autocomplete({ minLength: 0, source: autocomplete_sampletype});
	$("#SamplePoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});

	$("input[name$=save]").addClass('allowMultiSubmit');
	$("input[name$=save]").click(clickSaveButton);

});
}(jQuery));
