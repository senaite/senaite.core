jQuery( function($) {
$(document).ready(function(){

	// All actions will refresh only the content table.
	function inplace_submit(){
		form = $('#folderContentsForm');
		options = {
			target: '.folderlisting-main-table',
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				$('#filter_input_keypress').remove();
				$('#review_state_clicked').remove();
				$('#workflow_action_submitted').remove();
			}
		}
		form.ajaxSubmit(options);
	}

	$(".folderlisting-filter").live('keyup', function(key){
		if(key.which == 13) {
			$('#folderContentsForm').append("<input type='hidden' value='1' name='filter_input_keypress' id='filter_input_keypress'/>");
			inplace_submit();
			return false;
		}
	})

	$(".review_state_filter").live('change', function(){
		$('#folderContentsForm').append("<input type='hidden' value='1' name='review_state_clicked' id='review_state_clicked'/>");
		inplace_submit();
	});

	$("#clear_filters").live('click', function(){
		$('#folderContentsForm').append("<input type='hidden' value='1' name='clear_filters' id='clear_filters'/>");
		inplace_submit();
		$("#clear_filters").toggle(false);
	})

	// workflow action buttons submit entire form to workflow_action.
	$(".workflow_action_button").live('click', function(){
		form = $('#folderContentsForm');
		form.append("<input type='hidden' value='"+$(this).val()+"' name='workflow_action_button'/>");
		form.attr("action", "workflow_action");
		form.submit();
	})

});
});
