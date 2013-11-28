(function( $ ) {
"use strict";

function validate_spec_field_entry(element) {
	var uid = $(element).attr("uid");
	// no spec selector here yet!
	// $("[name^='ar\\."+sb_col+"\\.Specification']").val("");
	// $("[name^='ar\\."+sb_col+"\\.Specification_uid']").val("");
	var min_element = $("[name='min\\."+uid+"\\:records']");
	var max_element = $("[name='max\\."+uid+"\\:records']");
	var error_element = $("[name='error\\."+uid+"\\:records']");
	var min = parseFloat($(min_element).val(), 10);
	var max = parseFloat($(max_element).val(), 10);
	var error = parseFloat($(error_element).val(), 10);

	if($(element).attr("name") == $(min_element).attr("name")){
		if(isNaN(min)) {
			$(min_element).val("");
		} else if ((!isNaN(max)) && min > max) {
			$(max_element).val("");
		}
	} else if($(element).attr("name") == $(max_element).attr("name")){
		if(isNaN(max)) {
			$(max_element).val("");
		} else if ((!isNaN(min)) && max < min) {
			$(min_element).val("");
		}
	} else if($(element).attr("name") == $(error_element).attr("name")){
		if(isNaN(error) || error < 0 || error > 100){
			$(error_element).val("");
		}
	}
}

////////////////////////////////////////
function check_service(service_uid){
	var new_element, element;

	// Add partition dropdown
	element = $("[name='Partition."+service_uid+":records']");
	new_element = "" +
		"<select class='listing_select_entry' "+
		"name='Partition."+service_uid+":records' "+
		"field='Partition' uid='"+service_uid+"' "+
		"style='font-size: 100%'>";
	$.each($("td.PartTitle"), function(i,v){
		var partid = $($(v).children()[1]).text();
		new_element = new_element + "<option value='"+partid+"'>"+partid+"</option>";
	});
	new_element = new_element + "</select>";
	$(element).replaceWith(new_element);

	// Add price field
	var logged_in_client = $("input[name='logged_in_client']").val();
	if (logged_in_client != "1") {
		element = $("[name='Price."+service_uid+":records']");
		new_element = "" +
			"<input class='listing_string_entry numeric' "+
			"name='Price."+service_uid+":records' "+
			"field='Price' type='text' uid='"+service_uid+"' "+
			"autocomplete='off' style='font-size: 100%' size='5' "+
			"value='"+$(element).val()+"'>";
		$($(element).siblings()[1]).remove();
		$(element).replaceWith(new_element);
	}

	// spec fields
	var specfields = ["min", "max", "error"];
	for(var i in specfields) {
		element = $("[name='"+specfields[i]+"."+service_uid+":records']");
		new_element = "" +
			"<input class='listing_string_entry numeric' type='text' size='5' " +
			"field='"+specfields[i]+"' value='"+$(element).val()+"' " +
			"name='"+specfields[i]+"."+service_uid+":records' " +
			"uid='"+service_uid+"' autocomplete='off' style='font-size: 100%'>";
		$(element).replaceWith(new_element);
	}

}

////////////////////////////////////////
function uncheck_service(service_uid){
	var new_element, element;

	element = $("[name='Partition."+service_uid+":records']");
	new_element = "" +
		"<input type='hidden' name='Partition."+service_uid+":records' value=''/>";
	$(element).replaceWith(new_element);

	var logged_in_client = $("input[name='logged_in_client']").val();
	if (logged_in_client != "1") {
		element = $("[name='Price."+service_uid+":records']");
		$($(element).siblings()[0])
			.after("<span class='state-active state-active '>"+$(element).val()+"</span>");
		new_element = "" +
			"<input type='hidden' name='Price."+service_uid+":records' value='"+$(element).val()+"'/>";
		$(element).replaceWith(new_element);
	}

	var specfields = ["min", "max", "error"];
	for(var i in specfields) {
		element = $("[name='"+specfields[i]+"."+service_uid+":records']");
		new_element = "" +
			"<input type='hidden' field='"+specfields[i]+"' value='"+element.val()+"' " +
			"name='"+specfields[i]+"."+service_uid+":records' uid='"+service_uid+"'>";
		$(element).replaceWith(new_element);
	}

}

////////////////////////////////////////
function calcdependencies(elements, auto_yes) {
	/*jshint validthis:true */
	var affected_titles = [];
	var affected_services = [];
	var yes, no;
	var _ = window.jarn.i18n.MessageFactory("bika");

	// elements is a list of jquery checkbox objects
	var element = elements.shift();
	if(auto_yes === undefined){ auto_yes = false ; }

	var service_uid = $(element).attr("id").split("_cb_")[1];
	var service_data = window.bika_utils.data.services[service_uid];

	if (service_data === undefined || service_data === null){
		// if service_uid is not in bika_utils.data.services, there are no deps.
		return;
	}
	var deps = service_data.deps;
	var backrefs = service_data.backrefs;

	if ($(element).prop("checked") === true){
		// selecting a service; discover services it depends on.
		// actions are discovered and stored in dep_args, until confirmation dialog->Yes.
		var dep_args = [];

		var pocdata;
		if (deps === undefined || deps === null) {
			pocdata = [];
		} else {
			pocdata = deps;
		}
		$.each(pocdata, function(pocid_poctitle, catdata){
			var poc = pocid_poctitle.split("_");
			$.each(catdata, function(catid_cattitle, servicedata){
				var cat = catid_cattitle.split("_");
				var services = [];
				$.each(servicedata, function(i, serviceuid_servicetitle){
					var service = serviceuid_servicetitle.split("_");
					// if the service is already checked, skip it.
					if (! $("#list_cb_"+service[0]).prop("checked") ){
						// this one is for the current category
						services.push(service[0]);
						// and this one decides if the confirmation box gets shown at all.
						affected_services.push(service[0]);
						// this one is for the pretty message box.
						affected_titles.push(service[1] + " ("+cat[1]+")");
					}
				});
				// we want to confirm, then process these all at once
				if(services.length > 0){
					dep_args.push([poc[0], cat[0], services]);
				}
			});
		});

		if (affected_services.length > 0) {
			$("body").append(
				"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
				_("<p>${service} requires the following services to be selected:</p><br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
					{service: $(element).attr("item_title"), deps: affected_titles.join("<br/>") })+"</div>");

			if (auto_yes) {
				$.each(dep_args, function(i,args){
					$.each(args[2], function(x,serviceUID){
						if(! $("#list_cb_"+serviceUID).prop("checked") ){
							check_service(serviceUID);
							$("#list_cb_"+serviceUID).prop("checked",true);
						}
					});
				});
				$(this).dialog("close");
				$("#messagebox").remove();
			} else {
				yes = _("Yes");
				no = _("No");
				$("#messagebox").dialog({
					width:450,
					modal: true,
					resizable: false,
					closeOnEscape: false,
					buttons:{
						yes: function(){
							$.each(dep_args, function(i,args){
								$.each(args[2], function(x,serviceUID){
									if(! $("#list_cb_"+serviceUID).prop("checked") ){
										check_service(serviceUID);
										$("#list_cb_"+serviceUID).prop("checked",true);
									}
								});
							});
							$(this).dialog("close");
							$("#messagebox").remove();
						},
						no: function(){
							if($(element).prop("checked") ){
								uncheck_service($(element).attr("value"));
								$(element).prop("checked",false);
							}
							$(this).dialog("close");
							$("#messagebox").remove();
						}
					}
				});
			}
		}
	}
	else {
		// unselecting a service; discover back dependencies

		var s_uids = backrefs;
		if (s_uids === undefined || s_uids === null) {
			s_uids = [];
		}
		if (s_uids.length > 0){
			$.each(s_uids, function(i, serviceUID){
				var cb = $("#list_cb_" + serviceUID);
				if (cb.prop("checked")){
					affected_services.push(serviceUID);
					affected_titles.push(cb.attr("item_title"));
				}
			});
			$("body").append(
				"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
				_("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
					{
						service:$(element).attr("item_title"),
						deps: affected_titles.join("<br/>")})+"</div>");
			yes = _("Yes");
			no = _("No");
			if (affected_services.length > 0) {
				$("#messagebox").dialog(
					{
						width:450,
						modal: true,
						resizable:false,
						closeOnEscape: false,
						buttons:{
							yes: function(){
								$.each(affected_services, function(i,serviceUID){
									var se = $("#list_cb_"+serviceUID);
									uncheck_service(serviceUID);
									$(se).prop("checked", false);
								});
								$(this).dialog("close");
								$("#messagebox").remove();
							},
							no:function(){
								service_uid = $(element).attr("value");
								check_service(service_uid);
								$(element).prop("checked", true);
								$(this).dialog("close");
								$("#messagebox").remove();
					}
				}});
			} else {
				$("#messagebox").remove();
			}
		}
	}
}

$(document).ready(function(){

	$("[name^='min\\.'], [name^='max\\.'], [name^='error\\.']").live("change", function(){
		validate_spec_field_entry(this);
	});

	////////////////////////////////////////
	// disable checkboxes for eg verified analyses.
	$.each($("[name='uids:list']"), function(x,cb){
		var uid = $(cb).val();
		var row_data = $.parseJSON($("#"+uid+"_row_data").val());
		if (row_data.disabled === true){
			// disabled fields must be shadowed by hidden fields,
			// or they don't appear in the submitted form.
			$(cb).prop("disabled", true);
			var cbname = $(cb).attr("name");
			var cbid = $(cb).attr("id");
			$(cb).removeAttr("name").removeAttr("id");
			$(cb).after("<input type='hidden' name='"+cbname+"' value='"+uid+"' id='"+cbid+"'/>");

			var el = $("[name='Price."+uid+":records']");
			var elname = $(el).attr("name");
			var elval = $(el).val();
			$(el).after("<input type='hidden' name='"+elname+"' value='"+elval+"'/>");
			$(el).prop("disabled", true);

			el = $("[name='Partition."+uid+":records']");
			elname = $(el).attr("name");
			elval = $(el).val();
			$(el).after("<input type='hidden' name='"+elname+"' value='"+elval+"'/>");
			$(el).prop("disabled", true);

			var specfields = ["min", "max", "error"];
			for(var i in specfields) {
				var element = $("[name='"+specfields[i]+"."+service_uid+":records']");
				var new_element = "" +
					"<input type='hidden' field='"+specfields[i]+"' value='"+element.val()+"' " +
					"name='"+specfields[i]+"."+service_uid+":records' uid='"+service_uid+"'>";
				$(element).replaceWith(new_element);
			}
		}
	});

	////////////////////////////////////////
	// checkboxes in services list
	$("[name='uids:list']").live("click", function(){
		calcdependencies([this]);

		var service_uid = $(this).val();
		if ($(this).prop("checked")){
			check_service(service_uid);
		}
		else {
			uncheck_service(service_uid);
		}
	});

});
}(jQuery));
