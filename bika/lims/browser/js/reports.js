jQuery( function($) {
$(document).ready(function(){

	_ = jarn.i18n.MessageFactory('bika');
	PMF = jarn.i18n.MessageFactory('plone');

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
	$("#tats_overtime_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#tats_overtime").toggle(true);
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
	$("#referenceanalysisqc_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#referenceanalysisqc").toggle(true);
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
	$("#dailysamplesreceived_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#dailysamplesreceived").toggle(true);
	});
	$("#samplereceivedvsreported_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#samplereceivedvsreported").toggle(true);
	});
	$("#analysesperdepartment_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysesperdepartment").toggle(true);
	});
	$("#analysesperformedpertotal_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysesperformedpertotal").toggle(true);
	});
	$("#analysisrequestsummary_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#analysisrequestsummary").toggle(true);
	});
	$("#dataentrydaybook_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#dataentrydaybook").toggle(true);
	});
	
	$("#usershistory_selector").click(function(event){
		$(".criteria").toggle(false);
		event.preventDefault();
		$("#usershistory").toggle(true);
	});


	// AJAX: Set ReferenceSamples dropdown when Supplier is selected
	$("#ReferenceSupplierUID").change(function(){
		val = $(this).val();
		$.getJSON('referenceanalysisqc_samples',
				{'ReferenceSupplierUID':val,
				 '_authenticator': $('input[name="_authenticator"]').val()},
				 function(data,textStatus){
					 $("#ReferenceSampleUID").empty().append("<option value=''></option>");
					 if(data){
						 for(i=0;i<data.length;i++){
							 sample = data[i];
							 $("#ReferenceSampleUID").append("<option value='"+sample[0]+"'>"+sample[1]+"</option>")
						 }
					 }
				 }
		);
	})

	// AJAX: Set ReferenceServices dropdown when ReferenceSample is selected
	$("#ReferenceSampleUID").change(function(){
		val = $(this).val();
		$.getJSON('referenceanalysisqc_services',
				{'ReferenceSampleUID':val,
				 '_authenticator': $('input[name="_authenticator"]').val()},
				 function(data,textStatus){
					 $("#ReferenceServiceUID").empty().append("<option value=''></option>");
					 if(data){
						 for(i=0;i<data.length;i++){
							 service = data[i];
							 $("#ReferenceServiceUID").append("<option value='"+service[0]+"'>"+service[1]+"</option>")
						 }
					 }
				 }
		);
	})

	// Reference QC: reset the dropdowns on page reload
	$("#ReferenceSupplierUID").val("");

});
});
