jQuery(function($){

function calc_min_max(){
	tds = $($(this).parent().parent()[0]).children();
	result = $($(tds).children()[1]).val(); // 0 is hidden child with uid in it
	error = $($(tds).children()[2]).val();
	min_field = $($(tds).children()[3]);
	max_field = $($(tds).children()[4]);
	if (result != "" && error != ""){
		min_field.val(parseFloat(result) - parseFloat(result)/100 * parseFloat(error));
		max_field.val(parseFloat(result) + parseFloat(result)/100 * parseFloat(error));
	}
}

function expand_analysisservices(cat_key){
	html = "";
	cat_uid = cat_key.split("_")[0];
	selectedservices = $.parseJSON($("#selected_services").val());
	allservices = $.parseJSON($("#all_services").val());
	$.each(allservices[cat_key], function(i,val){
		if(selectedservices != null &&
			selectedservices[cat_key] != undefined &&
			selectedservices[cat_key][val.uid] != undefined ){
				ref = selectedservices[cat_key][val.uid];
				uid = ref.uid;			if (uid == undefined){ uid = ""; }
				error = ref.error;		if (error == undefined){ error = ""; }
				result = ref.result;	if (result == undefined){ result = ""; }
				min = ref.min;			if (min == undefined){ min = ""; }
				max = ref.max;			if (max == undefined){ max = ""; }
				if (uid == undefined){ uid = ""; }
				html = html + "<tr id='"+ref.uid+"'>" +
					"<td>"+ref.title+"<input name='ReferenceResults.uid:records:ignore_empty' type='hidden' value='"+uid+"'/></td>"+
					"<td><input class='numeric rr_entry' name='ReferenceResults.result:records:ignore_empty' type='text' size='6' value='"+result+"'/></td>"+
					"<td><input class='numeric rr_entry' name='ReferenceResults.error:records:ignore_empty' type='text' size='6' value='"+error+"'/></td>"+
					"<td><input class='numeric rr_entry' name='ReferenceResults.min:records:ignore_empty' type='text' size='6' value='"+min+"'/></td>"+
					"<td><input class='numeric rr_entry' name='ReferenceResults.max:records:ignore_empty' type='text' size='6' value='"+max+"'/></td>";
		} else {
			html = html + "<tr id='"+val.uid+"'>" +
				"<td>"+val.title+"<input name='ReferenceResults.uid:records:ignore_empty' type='hidden' value='"+val.uid+"'/></td>"+
				"<td><input class='numeric rr_entry' name='ReferenceResults.result:records:ignore_empty' type='text' size='6'/></td>"+
				"<td><input class='numeric rr_entry' name='ReferenceResults.error:records:ignore_empty' type='text' size='6'/></td>"+
				"<td><input class='numeric rr_entry' name='ReferenceResults.min:records:ignore_empty' type='text' size='6'/></td>"+
				"<td><input class='numeric rr_entry' name='ReferenceResults.max:records:ignore_empty' type='text' size='6'/></td>";
		}
	});
	return html;
}

$(document).ready(function(){

	// auto-expand 'prefill' categories
	$.each($('tr[class~="prefill"]'), function() {
		target = $('#'+$(this).attr("name"));
		target.html(expand_analysisservices($(this).attr("key")));
		$(this).removeClass("initial");
		$(this).removeClass("prefill");
		$(this).addClass("expanded");
	});

	// initial category expansion
	$('tr[class~="initial"]').live('click', function(){
		target = $('#'+$(this).attr("name"));
		target.html(expand_analysisservices($(this).attr("key")));
		$(this).removeClass("initial");
		$(this).addClass("expanded");
	});

	// collapsed category expansion
	$('tr[class~="collapsed"]').live('click', function(){
		target = $('#'+$(this).attr("name"));
		$(target).toggle();
		cat_uid = $(this).attr("name");
		$(this).removeClass("collapsed");
		$(this).addClass("expanded");
	});

	// expanded category collapsion
	$('tr[class~="expanded"]').live('click', function(){
		target = $('#'+$(this).attr("name"));
		$(target).toggle();
		cat_uid = $(this).attr("name");
		$(this).removeClass("expanded");
		$(this).addClass("collapsed");
	});

	// "Result" and "Error" trigger min/max recalculation
	$("input[name='ReferenceResults.result:records:ignore_empty']")
		.live('change', calc_min_max);
	$("input[name='ReferenceResults.error:records:ignore_empty']")
		.live('change', calc_min_max);

});
});
