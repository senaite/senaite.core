// ar.js and sample.js are nearly identical
(function( $ ) {

function openCCBrowser(event){
	event.preventDefault();
	contact_uid = $('#primary_contact').attr('value');
	cc_uids = $('#cc_uids').attr('value');
	window.open('ar_select_cc?hide_uids=' + contact_uid + '&selected_uids=' + cc_uids,
		'ar_select_cc','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=600,height=550');
}

function workflow_transition_sample(event){
	event.preventDefault()
	if ($("#DateSampled").val() != "" && $("#Sampler").val() != "") {
		requestdata = new Object();
		requestdata.workflow_action = "sample";
		$.each($("form[name=header_form]").find("input,select"), function(i,v){
			name = $(v).attr('name');
			value =  $(v).attr('type') == 'checkbox' ? $(v).attr('checked') : $(v).val();
			requestdata[name] = value;
		});
		requeststring = $.param(requestdata);
		// sending only the username, because it's all we have access to.
		href = window.location.href.split("?")[0] + "?" + requeststring;
		window.location.href = href;
	} else {
		message = "";
		if ($("#DateSampled").val() == ""){
			message = message + PMF('${name} is required, please correct.', {'name':'Date Sampled'})
		}
		if ($("#Sampler").val() == ""){
			if(message != "") { message = message + "<br/>"; }
			message = message + PMF('${name} is required, please correct.', {'name':'Sampler'})
		}
		window.bika_utils.portalMessage(message);
	}
}

function save_header(event){
	event.preventDefault();
	requestdata = new Object();
	$.each($("form[name=header_form]").find("input,select"), function(i,v){
		name = $(v).attr('name');
		value =  $(v).attr('type') == 'checkbox' ? $(v).attr('checked') : $(v).val();
		requestdata[name] = value;
	});
	requeststring = $.param(requestdata);
	href = window.location.href.split("?")[0] + "?" + requeststring;
	window.location.href = href;
}

function workflow_transition_preserve(event){
	event.preventDefault()
	message = _("You must preserve individual Sample Partitions");
	window.bika_utils.portalMessage(message);
}

$(document).ready(function(){

	_ = jarn.i18n.MessageFactory('bika');
	PMF = jarn.i18n.MessageFactory('plone');

	$('#open_cc_browser').click(openCCBrowser);

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
