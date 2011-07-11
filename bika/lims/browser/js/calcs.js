jQuery( function($) {
$(document).ready(function(){

	$(".analysis_entry").live('change', function(){
		uid = $(this).attr('uid');
		field = $(this).attr('field');
		value = $(this).attr('value');
		// collect all results for back-dependant calculations
		var results = {};
		$.each($("input[field='Result']"), function(i, e){
			results[$(e).attr("uid")] = $(e).val();
		});
		options = {
			type: 'POST',
			url: 'analysis_entry',
			async: false,
			data: {
				'uid': uid,
				'field': field,
				'value': value,
				'results': $.toJSON(results),
				'item_data': $('#'+uid+"_item_data").val(),
				'_authenticator': $('input[name="_authenticator"]').val()
			},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				// Update TR's interim_fields value to reflect new input field results
				if('item_data' in data){
					$('#'+uid+"_item_data").val($.toJSON(data.item_data));
				}
				// clear out all row alerts
				$(".alert").empty();
				// print alert icons / errors
				for(i=0;i<$(data['alerts']).length;i++){
					lert = $(data['alerts'])[i];
					$("span[uid='"+lert.uid+"']")
					  .filter("span[field='"+lert.field+"']")
					  .append("<img src='++resource++bika.lims.images/"	+lert.icon +".png' title='"+lert.msg+"'/>");
					// on error? remove value from result fields, to be re-filled below
					$("input[uid='"+uid+"']").filter("input[field='Result']").val('');
					$("input[uid='"+uid+"']").filter("input[field='Result_display']").val('');
				}
				// put result values in their boxes
				for(i=0;i<$(data['results']).length;i++){
					result = $(data['results'])[i];
					$("input[uid='"+result.uid+"']")
						.filter("input[field='Result']").val(result.result);
					$("input[uid='"+result.uid+"']")
						.filter("input[field='Result_display']").val(result.result_display);
				}
			}
		}
		$.ajax(options);
	});

});
});
