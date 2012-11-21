(function( $ ) {
$(document).ready(function(){

	_ = jarn.i18n.MessageFactory('bika');
	PMF = jarn.i18n.MessageFactory('plone');

	// ##cc_uids is the parent AR form's CC contacts box
	$.each(window.opener.$("#cc_uids").attr('value').split(","), function(i,e){
		form_id = $(this).parents("form").attr("id");
		$("#"+form_id+"_cb_"+e).click();
	});

	// return selected references from the CC popup window back into the widget
	$('[transition=save_selection_button]').click(function(){
		uids = [];
		titles = [];
		$.each($("[name='uids:list']").filter(":checked"), function(i, e){
			uids.push($(e).val());
			titles.push($(e).attr('item_title'));
		});
		window.opener.$("#cc_titles").attr('value', titles.join('; '));
		window.opener.$("span[id=cc_titles]").empty().append(titles.join('; '));
		window.opener.$("#cc_uids").attr('value', uids.join(','));

		window.close();
		return false;
	});

});
}(jQuery));
