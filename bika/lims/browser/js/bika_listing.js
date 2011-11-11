jQuery( function($) {
$(document).ready(function(){

	// actions will refresh only the content table.
	function inplace_submit(){
		form = $('#folderContentsForm');
		options = {
			target: '.folderlisting-main-table',
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				$("#spinner").toggle(false);
				$('#workflow_action_submitted').remove();
			}
		}
		form.ajaxSubmit(options);
	}

	// review_state_selector clicks
	$(".review_state_selector a").click(function(){
		window.location.href = window.location.href.split("?")[0] + $.query.set("review_state", $(this).attr('value'));
		return false;
	});

	// select all (on this screen at least)
	$("#select_all").live('click', function(){
		checked = $(this).attr("checked");
		$.each($("input[id^='cb_']"), function(i,v){
			$(v).attr("checked", checked);
		});
	});

	// modify select_all checkbox when regular checkboxes are modified
	$("input[id^='cb_']").live('click', function(){
		all_selected = true;
		$.each($("input[id^='cb_']"), function(i,v){
			if($(v).attr("checked") == false){
				all_selected = false;
			}
		});
		if(all_selected){
			$("#select_all").attr("checked", true);
		} else {
			$("#select_all").attr("checked", false);
		}
	});

	// workflow action buttons submit entire form to workflow_action.
	$(".workflow_action_button").live('click', function(){
		form = $('#folderContentsForm');
		form.append("<input type='hidden' value='"+$(this).val()+"' name='workflow_action_button'/>");
		form.attr("action", "workflow_action");
		form.submit();
	})

	$(".listing_string_entry,.listing_select_entry").live('keypress', function(event) {
	  var tab = 9;
	  var enter = 13;
	  if (event.which == enter) {
		event.preventDefault();
	  }
	});


});
});
