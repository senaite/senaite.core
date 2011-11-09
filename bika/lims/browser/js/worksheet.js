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

		if (window.location.href.indexOf("blank") > -1) {
		  control_type = 'b';
		} else {
		  control_type = 'c';
		}

		url = window.location.href
			.replace("/add_blank", "")
			.replace("/add_control", "") + "/getWorksheetReferences"
		$("#reference_samples").load(url,
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
	get_updated_controls();

	// clicking service categories in add_control and add_blank expand and
	// collapse service TRs.
	$("th.collapsed").live("click", function(){
		cat = $(this).attr('cat');
		$("tr[cat='"+cat+"']").toggle(true);
		$(this).removeClass("collapsed").addClass("expanded");
	});
	$("th.expanded").live("click", function(){
		cat = $(this).attr('cat');
		$("tr[cat='"+cat+"']").toggle(false);
		$(this).removeClass("expanded").addClass("collapsed");
	});

	// click reference sample TR in add_blank or add_control
	$("#reference_samples tr").live('click', function(){
		selected_service_uids = [];
		$.each($("input:checked"), function(i,e){
			selected_service_uids.push($(e).attr('uid'));
		});
		ssuids = selected_service_uids.join(",");
		$('#folderContentsForm').append("<input type='hidden' value='"+ssuids+"' name='selected_service_uids'/>");
		$('#folderContentsForm').append("<input type='hidden' value='"+$(this).attr("uid")+"' name='reference_uid'/>");
		$('#folderContentsForm').submit();
	})

	// click AR TR in add_duplicate
	$("#worksheet_ars tr").live('click', function(){
		$('#folderContentsForm').append("<input type='hidden' value='"+$(this).attr("uid")+"' name='ar_uid'/>");
		$('#folderContentsForm').submit();
	})

});
});
