// ./analysisprofileanalyseswidget.pt
// ../../../browser/widgets/analysisprofilealyseswidget.py

// copied from artemplateanalyseswidget

(function( $ ) {
"use strict";

function expand_cat(service_uid){
	var cat = $("[name='Partition."+service_uid+":records']").parents("tr").attr("cat");
	var th = $("th[cat='"+cat+"']");
	if ($(th).hasClass("collapsed")){
		var table = $(th).parents(".bika-listing-table");
		// show sub TR rows
		$(table)
			.children("tbody")
			.children("tr[cat="+cat+"]")
			.toggle(true);
		$(th).removeClass("collapsed").addClass("expanded");
	}
}


function add_Yes(dlg, element, dep_services){
	for(var i = 0; i<dep_services.length; i++){
		var service_uid = dep_services[i].Service_uid;
		if(! $("#analyses_cb_"+service_uid).prop("checked") ){
			$("#analyses_cb_"+service_uid).prop("checked",true);
			expand_cat(service_uid);
		}
	}
	$(dlg).dialog("close");
	$("#messagebox").remove();
}

function add_No(dlg, element){
	if($(element).prop("checked") ){
		$(element).prop("checked",false);
	}
	$(dlg).dialog("close");
	$("#messagebox").remove();
}

function calcdependencies(elements, auto_yes) {
	/*jshint validthis:true */
	auto_yes = auto_yes || false;
    window.jarn.i18n.loadCatalog("bika");
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
				if ($("#analyses_cb_"+dep.Service_uid).prop("checked") ){
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
				cb = $("#analyses_cb_" + dep.Service_uid);
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
						cb = $("#analyses_cb_" + dep.Service_uid);
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
									cb = $("#analyses_cb_" + dep.Service_uid);
									$(cb).prop("checked", false);
								}
								$(this).dialog("close");
								$("#messagebox").remove();
							},
							no:function(){
								service_uid = $(element).attr("value");
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

function click_uid_checkbox(){
	/*jshint validthis:true */
	calcdependencies([this]);
}

$(document).ready(function(){
	$("[name='uids:list']").live("click", click_uid_checkbox);
});

}(jQuery));
