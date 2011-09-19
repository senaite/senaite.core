jQuery( function($) {
$(document).ready(function(){

	// XXX when should this run...?
	$(".listing_string_entry").live('change', function(){
		uid = $(this).attr('uid');
		objectId = $(this).attr('objectId');
		field = $(this).attr('field');
		value = $(this).attr('value');
		// check the item's checkbox
		$('#cb_'+uid).attr('checked', true);
		// collect all results for back-dependant calculations
		var results = {};
		$.each($("input[field='Result']"), function(i, e){
			results[$(e).attr("uid")] = $(e).val();
		});
		// collect all interims by UID for back-dependant calculations
		var interims = {};
		$.each($("input[id$='_item_data']"), function(i, e){
			interims[e.id.split("_")[0]] = $.parseJSON($(e).val());
		});
		interims = $.toJSON(interims);

		options = {
			type: 'POST',
			url: 'listing_string_entry',
			async: false,
			data: {
				'uid': uid,
				'field': field,
				'value': value,
				'results': $.toJSON(results),
				'specification': $("input[name='specification']")
					.filter(":checked").val(),
				'item_data': interims,
				'_authenticator': $('input[name="_authenticator"]').val()
			},
			dataType: "json",
			success: function(data,textStatus,$XHR){
				// Update TR's interim_fields value to reflect
				// new input field results
				if('item_data' in data){
					$('#'+uid+"_item_data").val($.toJSON(data.item_data[uid]));
				}
				// clear out all row alerts for rows with fresh results
				for(i=0;i<$(data['results']).length;i++){
					result = $(data['results'])[i];
					$(".alert").filter("span[uid='"+result.uid+"']").empty();
				}
				// clear out all row alerts for rows with fresh alerts!
				for(i=0;i<$(data['alerts']).length;i++){
					lert = $(data['alerts'])[i];
					$("span[uid='"+lert.uid+"']")
					  .filter("span[field='"+lert.field+"']")
					  .empty();
				}
				// Update uncertainty value
				for(i=0;i<$(data['uncertainties']).length;i++){
					u = $(data['uncertainties'])[i];
					$('#'+u.uid+"-uncertainty").val(u.uncertainty);
				}
				// print alert icons / errors
				for(i=0;i<$(data['alerts']).length;i++){
					lert = $(data['alerts'])[i];
					$("span[uid='"+lert.uid+"']")
					  .filter("span[field='"+lert.field+"']")
					  .append("<img src='++resource++bika.lims.images/"	+
						lert.icon +".png' title='"+
						lert.msg+"' uid='"+
						lert.uid+"' icon='"+
						lert.icon+"'/>");
					// remove value from result fields to be re-inserted below
					$("input[uid='"+uid+"']")
						.filter("input[field='Result']").val('');
					$("input[uid='"+uid+"']")
						.filter("input[field='formatted_result']").val('');
				}
				// put result values in their boxes
				for(i=0;i<$(data['results']).length;i++){
					result = $(data['results'])[i];
					$("input[uid='"+result.uid+"']")
						.filter("input[field='Result']")
						.val(result.result);
					$("input[uid='"+result.uid+"']")
						.filter("input[field='formatted_result']")
						.val(result.formatted_result);
					$("span[uid='"+result.uid+"']")
						.filter("span[field='formatted_result']")
						.empty()
						.append(result.formatted_result);
					// check the item's checkbox
					$('#cb_'+result.uid).attr('checked', true);
				}
			}
		}
		$.ajax(options);
	});

	// range specification radio clicks
	$("input[name='specification']").click(function(){
		result_elements = $("input[field='Result']");
		for(i=0; i<result_elements.length; i++){
			re = result_elements[i];
			result = $(re).val();
			if (result == ''){
				continue
			}
			uid = $(re).attr('uid');
			// remove old alerts
			$("img[uid='"+uid+"']").filter("img[icon='warning']").remove();
			$("img[uid='"+uid+"']").filter("img[icon='exclamation']").remove();
			// get spec data from TR
			specs = $.parseJSON($('#folder-contents-item-'+uid).attr('specs'));
			specification = $("input[name='specification']")
				.filter(":checked").val();
			if (!specification in specs){
				continue;
			}

			spec = specs[specification];
			if (spec.length == 0){
				continue;
			}
			result = parseFloat(result);
			spec_min = parseFloat(spec.min);
			spec_max = parseFloat(spec.max);

			// shoulder first
            error_amount =  (result/100)*parseFloat(spec['error'])
            error_min = result - error_amount
            error_max = result + error_amount
            if (((result < spec_min) && (error_max >= spec_min)) ||
				((result > spec_max) && (error_min <= spec_max)) ){
				$("span[uid='"+uid+"']")
				  .filter("span[field='Result']")
				  .append("<img src='++resource++bika.lims.images/warning.png' uid='"+uid+"' icon='warning' title='Out Of Range: in shoulder'/>");
				continue;
			}

			// then check if in range
            if (result >= spec_min && result <= spec_max) {
				continue;
			}

			// fall to here; set red
			$("span[uid='"+uid+"']")
			  .filter("span[field='Result']")
			  .append("<img src='++resource++bika.lims.images/exclamation.png' uid='"+uid+"' icon='exclamation' title='Out Of Range'/>");

		}
	});

});
});
