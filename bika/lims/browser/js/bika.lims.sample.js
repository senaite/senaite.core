(function ($) {

function workflow_transition_sample(event) {
	event.preventDefault();
	var date = $("#DateSampled").val();
	var sampler = $("#Sampler").val();
	if (date != "" && date != undefined && date != null
			&& sampler != "" && sampler != undefined && sampler != null) {
		var form = $("form[name='header_form']");
		// this 'transition' key is scanned for in header_table.py/__call__
		form.append("<input type='hidden' name='transition' value='sample'/>")
		form.submit();
	}
	else {
		var message = "";
		if (date == "" || date == undefined || date == null) {
			message = message + PMF('${name} is required, please correct.',
									{'name': _("Date Sampled")})
		}
		if (sampler == "" || sampler == undefined || sampler == null) {
			if (message != "") {
				message = message + "<br/>";
			}
			message = message + PMF('${name} is required, please correct.',
									{'name': _("Sampler")})
		}
		if ( message != "") {
			window.bika.lims.portalMessage(message);
		}
	}
}

function save_header(event){
	event.preventDefault();
	requestdata = new Object();
	$.each($("form[name='header_form']").find("input,select"), function(i,v){
		name = $(v).attr('name');
		value =  $(v).attr('type') == 'checkbox' ? $(v).prop('checked') : $(v).val();
		requestdata[name] = value;
	});
	requeststring = $.param(requestdata);
	href = window.location.href.split("?")[0] + "?" + requeststring;
	window.location.href = href;
}

function workflow_transition_preserve(event){
	event.preventDefault()
	message = _("You must preserve individual Sample Partitions");
	window.bika.lims.portalMessage(message);
}

$(document).ready(function(){

	jarn.i18n.loadCatalog('plone');
	var PMF = window.jarn.i18n.MessageFactory("plone");
	window.jarn.i18n.loadCatalog("bika");
	var _ = window.jarn.i18n.MessageFactory("bika");

	// Plone "Sample" transition is only available when Sampler and DateSampled
	// are completed
	$("#workflow-transition-sample").click(workflow_transition_sample);

	// Trap the save button
	$("input[name='save']").click(save_header);

	// Disable Plone UI for preserve transition
	$("#workflow-transition-preserve").click(workflow_transition_preserve);

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
