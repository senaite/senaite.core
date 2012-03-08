jQuery( function($) {
$(document).ready(function(){

	_ = window.jsi18n;

	// Hide the "Sampled" transition until Sampler fields completed
	if ($("#DateSampled").val() == "" || $("#Sampler").val() == "") {
		$("#workflow-transition-sampled").parent().toggle(false);
	}

	// Hide the "Preserved" transition until Preserver fields completed
	if ($("#DatePreserved").val() == "" || $("#Preserver").val() == "") {
		$("#workflow-transition-preserved").parent().toggle(false);
	}

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
	$("#SampleType").autocomplete({ minLength: 0, source: autocomplete_sampletype});
	$("#SamplePoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});

	$("#DateSampled").datepicker({'dateFormat': 'dd M yy', showAnim: '', maxDate: '+0d'});
	$("#DatePreserved").datepicker({'dateFormat': 'dd M yy', showAnim: '', maxDate: '+0d'});

	// DateSampled is set immediately
	$("#DateSampled").change(function(){
		base_url = window.location.href.replace("/base_view", "");
		$.ajax({
			type: 'POST',
			url:base_url + "/setDateSampled",
			data: {'value': $(this).val(),
			       '_authenticator': $('input[name="_authenticator"]').val()},
			success: function(responseText, statusText, xhr, $form) {
				if(responseText == "ok"){
					$("#DateSampled").after("&nbsp;<img id='setDateSampled_ok' style='height:1.3em;' src='"+base_url+"/++resource++bika.lims.images/ok.png'/>");
					setTimeout(function(){ $('#setDateSampled_ok').remove(); }, 2000);
					// Perhaps the Sampled transition can be shown again
					if ($("#DateSampled").val() != "" && $("#Sampler").val() != "") {
						$("#workflow-transition-sampled").parent().toggle(true);
						$(".empty_sampler_option").remove();
					}
				}
			}
		});
	});

	// Sampler is set immediately
	$("#Sampler").change(function(){
		base_url = window.location.href.replace("/base_view", "");
		$.ajax({
			type: 'POST',
			url: base_url + "/setSampler",
			data: {'value': $(this).val(),
			       '_authenticator': $('input[name="_authenticator"]').val()},
			success: function(responseText, statusText, xhr, $form) {
				if(responseText == "ok"){
					$("#Sampler").after("&nbsp;<img id='setSampler_ok' style='height:1.3em;' src='"+base_url+"/++resource++bika.lims.images/ok.png'/>");
					setTimeout(function(){ $('#setSampler_ok').remove(); }, 2000);
					// Perhaps the Sampled transition can be shown again
					if ($("#DateSampled").val() != "" && $("#Sampler").val() != "") {
						$("#workflow-transition-sampled").parent().toggle(true);
						$(".empty_sampler_option").remove();
					}
				}
			}
		});
	});

	$("#ClientReference").focus();

});
});
