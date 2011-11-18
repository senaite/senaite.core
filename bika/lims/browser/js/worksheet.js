jQuery( function($) {
$(document).ready(function(){

	function portalMessage(message){
		str = "<dl class='portalMessage error'>"+
			"<dt i18n:translate='error'>Error</dt>"+
			"<dd><ul>" + message +
			"</ul></dd></dl>";
		$('.portalMessage').remove();
		$(str).appendTo('#viewlet-above-content');
	}

	// selecting a template changes the Add Worksheet href
	$(".wstemplate").change(function(){
		$(".worksheet_add").attr("href", $(".worksheet_add").attr("href").split("?")[0] + $.query.set("wstemplate",$(this).val()));
	});

	// search form - selecting a category fills up the service selector
	$("#CategorySelector").live("change", function(){
		val = $("#CategorySelector").val();
		if(val == 'any'){
			$("#ServiceSelector").empty();
			$("#ServiceSelector").append("<option value='any'>Any</option>");
			return;
		}
		$.ajax({
			url: window.location.href.replace("/add_analyses","") + "/getServices",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val(),
			       'getCategoryUID': val},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				$("#ServiceSelector").empty();
				$("#ServiceSelector").append("<option value='any'>Any</option>");
				for(i=0; i< data.length; i++){
					$("#ServiceSelector").append("<option value='"+data[i][0]+"'>"+data[i][1]+"</option>");
				}
			}
		});
	});
	$("#CategorySelector").trigger("change");

	// search form - selecting a category, service, or client, sets the profile
	// dropdown to empty value
	$("#CategorySelector, #ServiceSelector, #ClientSelector").live("change", function(){
		$("#ProfileSelector").val('');
	});

	// search form - selecting a profile sets the category, service, and client
	// dropdowns to empty values
	$("#ProfileSelector").live("change", function(){
		$("#CategorySelector").val('');
		$("#ServiceSelector").val('').empty().append("<option value='any'>Any</option>");
		$("#ClientSelector").val('');
	});

	// instant update of analyst when selection is made in dropdown
	$("#analyst").change(function(){
		url = window.location.href
				.replace("/manage_results", "")
				.replace("/add_analyses", "") + "/setAnalyst";
		$.ajax({
			type:'POST',
			url: url,
			data: {'value': $("#analyst").val(),
				'_authenticator': $('input[name="_authenticator"]').val()},
			success: function(responseText, statusText, xhr, $form) {
				$('#analyst_changed').toggle(true);
				setTimeout(function(){$('#analyst_changed').toggle(false);}, 1000)
			}
		});
	});

	// adding Controls and Blanks - selecting services re-renders the list
	// of applicable reference samples
	function get_updated_controls(){
		$("#ajax_spinner").toggle(true);
		selected_service_uids = [];
		$.each($("input:checked"), function(i,e){
			selected_service_uids.push($(e).attr('uid'));
		});

		if (window.location.href.search('add_control') > -1) {
		  control_type = 'c';
		} else {
		  control_type = 'b';
		}

		url = window.location.href
			.replace("/add_blank", "")
			.replace("/add_control", "") + "/getWorksheetReferences"
		$("#worksheet_add_references").load(url,
			{'service_uids': selected_service_uids.join(","),
			 'control_type': control_type,
			 '_authenticator': $('input[name="_authenticator"]').val()},
			function(responseText, statusText, xhr, $form) {
				$("#ajax_spinner").toggle(false);
			}
		);
	}
	$("#worksheet_services input[id*='cb_']").live('click', function(){
		get_updated_controls();
	});
	// get references for selected services on first load
	get_updated_controls();

	// click a Reference Sample in add_control or add_blank
	$("#worksheet_add_references tr").live('click', function(){
		// we want to submit to the worksheet.py/add_control or add_blank views.
		if(window.location.href.search('add_control') > -1){
			$(this).parents('form').attr("action", "add_control");
		} else {
			$(this).parents('form').attr("action", "add_blank");
		}
		// tell the form handler which services were selected
		selected_service_uids = [];
		$.each($("input:checked"), function(i,e){
			selected_service_uids.push($(e).attr('uid'));
		});
		ssuids = selected_service_uids.join(",");
		$(this).parents('form').append("<input type='hidden' value='"+ssuids+"' name='selected_service_uids'/>");
		// tell the form handler which refernece UID was clicked
		$(this).parents('form').append("<input type='hidden' value='"+$(this).attr("uid")+"' name='reference_uid'/>");
		// add the position dropdown's value to the form before submitting.
		$(this).parents('form').append("<input type='hidden' value='"+$('#position').val()+"' name='position'/>");
		$(this).parents('form').submit();
	})

	// click an AR in add_duplicate
	$("#worksheet_add_duplicate_ars tr").live('click', function(){
		// we want to submit to the worksheet.py/add_duplicate view.
		$(this).parents('form').attr("action", "add_duplicate");
		// add the position dropdown's value to the form before submitting.
		$(this).parents('form')
			.append("<input type='hidden' value='"+$(this).attr("uid")+"' name='ar_uid'/>")
			.append("<input type='hidden' value='"+$('#position').val()+"' name='position'/>");
		$(this).parents('form').submit();
	})

});
});
