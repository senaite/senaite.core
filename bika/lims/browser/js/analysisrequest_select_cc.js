jQuery( function($) {
$(document).ready(function(){

	$(".workflow_action_buttons")
		.append("<input type='submit' value='Save' class='select_cc_save'/>");

	$.each(window.opener.$("#cc_uids").val().split(","), function(i,e){
		$("#cb_"+e).click();
	});

	// return selected references from the CC popup window back into the widget
	$('.select_cc_save').live('click', function(){
		uids = [];
		titles = [];
		$.each($('input[id^="cb_"]:checked'), function(i, e){
			uids.push(e.id.split("_")[1]);
			titles.push($(e).attr('alt').split('elect ')[1]);
		});
		window.opener.$("#cc_titles").val(titles.join(','));
		window.opener.$("#cc_uids").val(uids.join(','));
		window.close();
	});




});
});
