jQuery( function($) {
$(document).ready(function(){

	$(".analysis_entry").live('change', function(){
		options = {
			type: 'POST',
			url: 'analysis_entry',
			data: {
				'uid': $(this).attr('uid'),
				'field': $(this).attr('field'),
				'value': $(this).attr('value'),
				'item_data': $('#folder-contents-item-' + $(this).attr('uid')).attr('item_data'),
				'_authenticator': $('input[name="_authenticator"]').val()
			},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				if('error' in data){
					$("span[uid='"+data.uid+"']")
					  .empty();
					$("span[uid='"+data.uid+"']")
					  .filter("span[field='"+data.field+"']")
					  .empty()
					  .append("<img src='++resource++bika.lims.images/exclamation.png' alt='!' title='"+data.error+"'/>");
				}
			}
		}
		$.ajax(options);
	});

});
});
