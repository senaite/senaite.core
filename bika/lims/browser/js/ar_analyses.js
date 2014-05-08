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

function add_Yes(dlg, element, dep_services){
	for(var i = 0; i<dep_services.length; i++){
		var service_uid = dep_services[i].Service_uid;
		if(! $("#list_cb_"+service_uid).prop("checked") ){
			check_service(service_uid);
			$("#list_cb_"+service_uid).prop("checked",true);
		}
	}
	$(dlg).dialog("close");
	$("#messagebox").remove();
}

function add_No(dlg, element){
	if($(element).prop("checked") ){
		uncheck_service($(element).attr("value"));
		$(element).prop("checked",false);
	}
	$(dlg).dialog("close");
	$("#messagebox").remove();
}

function calcdependencies(elements, auto_yes) {
	/*jshint validthis:true */
	auto_yes = auto_yes || false;
    jarn.i18n.loadCatalog('bika');
	var _ = window.jarn.i18n.MessageFactory("bika");

	var dep;
	var i, cb;

	var lims = window.bika.lims;

	for(var elements_i = 0; elements_i < elements.length; elements_i++){
		var dep_services = [];  // actionable services
		var dep_titles = [];
		var element = elements[elements_i];
		var service_uid = $(element).attr("value");
		// selecting a service; discover dependencies
		if ($(element).prop("checked")){
			var Dependencies = lims.AnalysisService.Dependencies(service_uid);
			for(i = 0; i<Dependencies.length; i++) {
				dep = Dependencies[i];
				if ($("#list_cb_"+dep.Service_uid).prop("checked") ){
					continue; // skip if checked already
				}
				dep_services.push(dep);
				dep_titles.push(dep.Service);
			}
			if (dep_services.length > 0) {
				if (auto_yes) {
					add_Yes(this, element, dep_services);
				} else {
					var html = "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>";
					html = html + _("<p>${service} requires the following services to be selected:</p>"+
													"<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
													{
														service: $(element).attr("title"),
														deps: dep_titles.join("<br/>")
													});
					html = html + "</div>";
					$("body").append(html);
					$("#messagebox").dialog({
						width:450,
						resizable:false,
						closeOnEscape: false,
						buttons:{
							yes: function(){
								add_Yes(this, element, dep_services);
							},
							no: function(){
								add_No(this, element);
							}
						}
					});
				}
			}
		}
		// unselecting a service; discover back dependencies
		else {
			var Dependants = lims.AnalysisService.Dependants(service_uid);
			for (i=0; i<Dependants.length; i++){
				dep = Dependants[i];
				cb = $("#list_cb_" + dep.Service_uid);
				if (cb.prop("checked")){
					dep_titles.push(dep.Service);
					dep_services.push(dep);
				}
			}
			if(dep_services.length > 0){
				if (auto_yes) {
					for(i=0; i<dep_services.length; i+=1) {
						dep = dep_services[i];
						service_uid = dep.Service_uid;
						cb = $("#list_cb_" + dep.Service_uid);
						uncheck_service(dep.Service_uid);
						$(cb).prop("checked", false);
					}
				} else {
					$("body").append(
						"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
						_("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
							{service:$(element).attr("title"),
							deps: dep_titles.join("<br/>")})+"</div>");
					$("#messagebox").dialog({
						width:450,
						resizable:false,
						closeOnEscape: false,
						buttons:{
							yes: function(){
								for(i=0; i<dep_services.length; i+=1) {
									dep = dep_services[i];
									service_uid = dep.Service_uid;
									cb = $("#list_cb_" + dep.Service_uid);
									$(cb).prop("checked", false);
									uncheck_service(dep.Service_uid);
								}
								$(this).dialog("close");
								$("#messagebox").remove();
							},
							no:function(){
								service_uid = $(element).attr("value");
								check_service(service_uid);
								$(element).prop("checked", true);
								$("#messagebox").remove();
								$(this).dialog("close");
							}
						}
					});
				}
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
		var service_uid = $(cb).val();
		var row_data = $.parseJSON($("#"+service_uid+"_row_data").val());
		if (row_data.disabled === true){
			// disabled fields must be shadowed by hidden fields,
			// or they don't appear in the submitted form.
			$(cb).prop("disabled", true);
			var cbname = $(cb).attr("name");
			var cbid = $(cb).attr("id");
			$(cb).removeAttr("name").removeAttr("id");
			$(cb).after("<input type='hidden' name='"+cbname+"' value='"+service_uid+"' id='"+cbid+"'/>");

			var el = $("[name='Price."+service_uid+":records']");
			var elname = $(el).attr("name");
			var elval = $(el).val();
			$(el).after("<input type='hidden' name='"+elname+"' value='"+elval+"'/>");
			$(el).prop("disabled", true);

			el = $("[name='Partition."+service_uid+":records']");
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
