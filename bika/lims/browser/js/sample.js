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
	$("#DateSampled").datepicker({'dateFormat': 'dd M yy', showAnim: ''});
	$("#SampleType").autocomplete({ minLength: 0, source: autocomplete_sampletype});
	$("#SamplePoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});
	$("#ClientReference").focus();

	function portalMessage(message){
		str = "<dl class='portalMessage error'>"+
			"<dt>"+_("error")+"</dt>"+
			"<dd><ul>" + message +
			"</ul></dd></dl>";
		$('.portalMessage').remove();
		$(str).appendTo('#viewlet-above-content');
	}

	// Sample Edit ajax form submits
	$('#sample_edit_form').ajaxForm({
		url: window.location.href,
		url: window.location.href.replace("/base_edit","/sample_submit"),
		dataType:  'json',
		data: $(this).formToArray(),
		beforeSubmit: function(formData, jqForm, options) {
			$("input[class~='context']").attr('disabled',true);
		},
		success: function(responseText, statusText, xhr, $form)  {
			if (responseText['success'] != undefined) {
				window.location.replace(window.location.href.replace("/base_edit", "/base_view"));
			}
			else {
				msg = ""
				for(error in responseText['errors']){
					msg = msg + responseText['errors'][error] + "<br/>";
				};
				portalMessage(msg);
				window.scroll(0, 0);
				$("input[class~='context']").removeAttr('disabled');
			}
		},
		error: function(XMLHttpRequest, statusText, errorThrown) {
			portalMessage(statusText);
			window.scroll(0, 0);
			$("input[class~='context']").removeAttr('disabled');
		}
	});

});
});
