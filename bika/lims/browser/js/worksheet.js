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

	// selecting an analyst changes the Add Worksheet href (on worksheet list screen)
	$(".wsanalyst").change(function(){
		old_url = $(".worksheet_add").attr("href").split("?");
		url_pt1 = old_url[0];
		rest_of_it = old_url[1].split("&");
		url_pt2 = rest_of_it[0];
		url_pt3 = rest_of_it[1];
		$(".worksheet_add").attr("href", url_pt1 + "?wsanalyst=" + $(this).val()) + "&" + url_pt3;
	});

	// selecting a template changes the Add Worksheet href (on worksheet list screen)
	$(".wstemplate").change(function(){
		old_url = $(".worksheet_add").attr("href").split("?");
		url_pt1 = old_url[0];
		rest_of_it = old_url[1].split("&");
		url_pt2 = rest_of_it[0];
		url_pt3 = rest_of_it[1];
		$(".worksheet_add").attr("href", url_pt1 + "?" + url_pt2 + "&wstemplate=" + $(this).val());
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
			url: window.location.href.split("?")[0].replace("/add_analyses","") + "/getServices",
			type: 'POST',
			data: {'_authenticator': $('input[name="_authenticator"]').val(),
			       'getCategoryUID': val},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				$("#ServiceSelector").empty();
				$("#ServiceSelector").append("<option value='any'>Any</option>");
				for(i=0; i< data.length; i++){
					// but make sure that ?list_getServiceUID still sets selected item
					if (data[i][0] == $.query.get('list_getServiceUID')){
						selected = 'selected="selected" ';
					} else {
						selected = '';
					}
					$("#ServiceSelector").append("<option "+selected+"value='"+data[i][0]+"'>"+data[i][1]+"</option>");
				}
			}
		});
	});
	$("#CategorySelector").trigger("change");


	// adding Controls and Blanks - selecting services re-renders the list
	// of applicable reference samples
	function get_updated_controls(){
		$("#ajax_spinner").toggle(true);
		selected_service_uids = [];
		$.each($("input:checked"), function(i,e){
			selected_service_uids.push($(e).val());
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
	$("#worksheet_services input[id*='_cb_']").live('click', function(){
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
			selected_service_uids.push($(e).val());
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

	// add_analyses analysis search is handled by bika_listing default __call__
	$(".ws-listing-filter-button").click(function(event){
		event.preventDefault();
		// default form_id in add_analyses
		form_id = "list";
		// Grab values for all class=listing-filter fields
		qstr = $.query.toString();
		$.each($(".listing-filter"), function(i,v){
			qstr = $.query
					.load(qstr)
					.set(form_id + "_" + $(v).attr('name'), $(v).val())
					.toString();
		});
		// redirect to search
		window.location.href = window.location.href.split("?")[0] + qstr;
	});

});
});
