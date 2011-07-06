jQuery( function($) {
$(document).ready(function(){

	$(".analysis_entry").live('change', function(){
		uid = $(this).attr('uid');
		field = $(this).attr('field');
		value = $(this).attr('value');
		options = {
			type: 'POST',
			url: 'analysis_entry',
			data: {
				'uid': uid,
				'field': field,
				'value': value,
				'item_data': $('#folder-contents-item-'+uid).attr('item_data'),
				'_authenticator': $('input[name="_authenticator"]').val()
			},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				// allow Python code to reset item_data (interim_fields)
				if('item_data' in data){
					$('#folder-contents-item-'+uid).attr('item_data', $.toJSON(data.item_data));
				}
				// clear out all row alerts
				$("span[uid='"+uid+"']").empty();
				if('error' in data){
					$("span[uid='"+uid+"']")
					  .filter("span[field='"+data.field+"']")
					  .append("<img src='++resource++bika.lims.images/exclamation.png' title='"+data.error+"'/>");
					// error: remove value from result field
					$("input[uid='"+uid+"']").filter("input[field='Result']").val('');
				}
				if('result' in data){
					$("input[uid='"+uid+"']").filter("input[field='Result']").val(data.result);
					if('formula' in data){
						$("span[uid='"+uid+"']")
						  .filter("span[name='formula']")
						  .append("<img src='++resource++bika.lims.images/calculation.png' title='"+data.formula+"'/>");
					}
				}
			}
		}
		$.ajax(options);
	});

});
});
