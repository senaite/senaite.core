(function ($) {

function destroy(arr, val) {
	for (var i = 0; i < arr.length; i++) if (arr[i] === val) arr.splice(i, 1);
	return arr;
}

function referencewidget_lookups(elements){
	// Any reference widgets that don't already have combogrid widgets
	var inputs;
	if(elements === undefined){
		inputs = $(".ArchetypesReferenceWidget [combogrid_options]").not(".has_combogrid_widget");
	} else {
		inputs = elements;
	}
	for (var i = inputs.length - 1; i >= 0; i--) {
		var element = inputs[i];
		var options = $.parseJSON($(element).attr("combogrid_options"));
		if(!options){
			continue;
		}

		// Prevent from saving previous record when input value is empty
		// By default, a recordwidget input element gets an empty value
		// when receives the focus, so the underneath values must be
		// cleared too.
		// var elName = $(element).attr("name");
		// $("input[name='"+elName+"']").live("focusin", function(){
		// 	var fieldName = $(this).attr("name");
		// 	if($(this).val() || $(this).val().length===0){
		// 		var val = $(this).val();
		// 		var uid = $(this).attr("uid");
		// 		$(this).val("");
		// 		$(this).attr("uid", "");
		// 		$("input[name='"+fieldName+"_uid']").val("");
		// 		$(this).trigger("unselected", [val,uid]);
		// 	}
		// });

		options.select = function(event, ui){
			event.preventDefault();
			var fieldName = $(this).attr("name");
			var skip;
			var uid_element = $("input[name='"+fieldName+"_uid']");
			var listing_div = $("div#"+fieldName+"-listing");
			if($("#"+fieldName+"-listing").length > 0) {
				// Add selection to textfield value
				var existing_uids = $("input[name='"+fieldName+"_uid']").val().split(",");
				destroy(existing_uids,"");
				destroy(existing_uids,"[]");
				var selected_value = ui.item[$(this).attr("ui_item")];
				var selected_uid = ui.item.UID;
				if (existing_uids.indexOf(selected_uid) == -1) {
					existing_uids.push(selected_uid);
					$(this).val("");
					$(this).attr("uid", existing_uids.join(","));
					$(uid_element).val(existing_uids.join(","));
					// insert item to listing
					var del_btn_src = window.portal_url+"/++resource++bika.lims.images/delete.png";
					var del_btn = "<img class='deletebtn' src='"+del_btn_src+"' fieldName='"+fieldName+"' uid='"+selected_uid+"'/>";
					var new_item = "<div class='reference_multi_item' uid='"+selected_uid+"'>"+del_btn+selected_value+"</div>";
					$(listing_div).append($(new_item));
				}
				skip = $(element).attr("skip_referencewidget_lookup");
				if (skip !== true){
					$(this).trigger("selected", ui.item.UID);
				}
				$(element).removeAttr("skip_referencewidget_lookup");
				$(this).next("input").focus();
			} else {
				// Set value in activated element (must exist in colModel!)
				$(this).val(ui.item[$(this).attr("ui_item")]);
				$(this).attr("uid", ui.item.UID);
				$("input[name='"+fieldName+"_uid']").val(ui.item.UID);
				skip = $(element).attr("skip_referencewidget_lookup");
				if (skip !== true){
					$(this).trigger("selected", ui.item.UID);
				}
				$(element).removeAttr("skip_referencewidget_lookup");
				$(this).next("input").focus();
			}
		};

		if(window.location.href.search("portal_factory") > -1){
			options.url = window.location.href.split("/portal_factory")[0] + "/" + options.url;
		}
		options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
		options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
		options.url = options.url + "&base_query=" + $(element).attr("base_query");
		options.url = options.url + "&search_query=" + $(element).attr("search_query");
		options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(element).attr("combogrid_options")).colModel);
		options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
		options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
		options.url = options.url + "&force_all=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).force_all);
		$(element).combogrid(options);
		$(element).addClass("has_combogrid_widget");
		$(element).attr("search_query", "{}");
	}
}

$(document).ready(function(){
	referencewidget_lookups();

	$(".reference_multi_item .deletebtn").live('click', function(){
		var fieldName = $(this).attr("fieldName");
		var uid = $(this).attr("uid");
		var existing_uids = $("input[name^='"+fieldName+"_uid']").val().split(",");
		destroy(existing_uids, uid);
		$("input[name^='"+fieldName+"_uid']").val(existing_uids.join(","));
		$("input[name='"+fieldName+"']").attr("uid", existing_uids.join(","));
		$(this).parent().remove();
	});

	// handle custom event "unselected" from jquery.ui.combogrid
	$(".ArchetypesReferenceWidget").live("unselected", function(){
		var e = $(this).children("input.referencewidget");
		fieldName = $(e).attr("name").split(":")[0];
		$(e).attr("uid", "");
		$("input[name^='"+fieldName+"_uid']").val("");
		$("div[name='"+fieldName+"-listing']").empty();
	});

});

}(jQuery));
