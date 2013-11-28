window.jarn.i18n.loadCatalog("bika");
window.jarn.i18n.loadCatalog("plone");

(function( $ ) {
"use strict";

function portalMessage(message) {
	var _ = window.jarn.i18n.MessageFactory("bika");
	var str = "<dl class='portalMessage error'>"+
		"<dt>"+_("Error")+"</dt>"+
		"<dd><ul>" + _(message) +
		"</ul></dd></dl>";
	$(".portalMessage").remove();
	$(str).appendTo("#viewlet-above-content");
}

function log(e) {
	var message = "JS: " + e.message + " url: " + window.location.url;
	$.ajax({
		type: "POST",
		url: "js_log",
		data: {"message":message,
				"_authenticator": $("input[name='_authenticator']").val()}
	});
}

var bika_utils = bika_utils || {

	init: function () {
        bika_utils.resolve_uid_cache = {};
		if ("localStorage" in window && window.localStorage !== null) {
			bika_utils.storage = window.localStorage;
		} else {
			bika_utils.storage = {};
		}
		var t = new Date().getTime();
		var stored_counter = bika_utils.storage.bika_bsc_counter;
		$.getJSON(window.portal_url+"/bika_bsc_counter?"+t, function(counter) {
			if (counter != stored_counter){
				$.getJSON(window.portal_url+"/bika_browserdata?"+t, function(data){
					bika_utils.storage.bika_bsc_counter = counter;
					bika_utils.storage.bika_browserdata = $.toJSON(data);
					bika_utils.data = data;
				});
			} else {
				var data = $.parseJSON(bika_utils.storage.bika_browserdata);
				bika_utils.data = data;
			}
		});
	},

	portalMessage: portalMessage

};

bika_utils.init();
window.bika_utils = bika_utils;

function jsonapi_read(request_data, handler) {
	window.jsonapi_cache = window.jsonapi_cache || {};
	var jsonapi_cacheKey = $.param(request_data);
	var jsonapi_read_handler = handler;
	if (window.jsonapi_cache[jsonapi_cacheKey] === undefined){
		$.ajax({
			type: "POST",
			dataType: "json",
			url: window.portal_url + "/@@API/read",
			data: request_data,
			success: function(data) {
				window.jsonapi_cache[jsonapi_cacheKey] = data;
				jsonapi_read_handler(data);
			}
		});
	} else {
		jsonapi_read_handler(window.jsonapi_cache[jsonapi_cacheKey]);
	}
}
window.jsonapi_read = jsonapi_read;
window.jsonapi_cache = {};

/*
function enableAddAttachment(this_field) {
	// XX move this to worksheet or AR or wherever it actually belongs
	var attachfile = document.getElementById("AttachFile").value;
	var service = document.getElementById("Service").value;
	var analysis = document.getElementById("Analysis").value;
	if (this_field == "Analysis") {
		document.getElementById("Service").value = "";
	}
	if (this_field == "Service") {
		document.getElementById("Analysis").value = "";
	}
	document.getElementById("addButton").disabled = false;
	if (attachfile === "") {
		document.getElementById("addButton").disabled = true;
	} else {
		if ((service === "") && (analysis === "")) {
			document.getElementById("addButton").disabled = true;
		}
	}
	return;
}

*/


$(document).ready(function(){

	var _ = window.jarn.i18n.MessageFactory("bika");

	var curDate = new Date();
	var y = curDate.getFullYear();
	var limitString = "1900:" + y;
	var dateFormat = _("date_format_short_datepicker");

	$("input.datepicker").live("click", function() {
		$(this).datepicker({
			showOn:"focus",
			showAnim:"",
			changeMonth:true,
			changeYear:true,
			dateFormat: dateFormat,
			yearRange: limitString
		})
		.click(function(){$(this).attr("value", "");})
		.focus();

	});

	$("input.datepicker_nofuture").live("click", function() {
		$(this).datepicker({
			showOn:"focus",
			showAnim:"",
			changeMonth:true,
			changeYear:true,
			maxDate: curDate,
			dateFormat: dateFormat,
			yearRange: limitString
		})
		.click(function(){$(this).attr("value", "");})
		.focus();
	});

	$("input.datepicker_2months").live("click", function() {
		$(this).datepicker({
			showOn:"focus",
			showAnim:"",
			changeMonth:true,
			changeYear:true,
			maxDate: "+0d",
			numberOfMonths: 2,
			dateFormat: dateFormat,
			yearRange: limitString
		})
		.click(function(){$(this).attr("value", "");})
		.focus();
	});

	// Analysis Service popup trigger
	$(".service_title").live("click", function(){
		var dialog = $("<div></div>");
		dialog
			.load(window.portal_url + "/analysisservice_popup",
				{"service_title":$(this).text(),
				"analysis_uid":$(this).parents("tr").attr("uid"),
				"_authenticator": $("input[name='_authenticator']").val()}
			)
			.dialog({
				width:450,
				height:450,
				closeText: _("Close"),
				resizable:true,
				title: $(this).text()
			});
	});

	$(".numeric").live("keypress", function(event) {
		// Backspace, tab, enter, end, home, left, right, ., <, >, and -
		// We don't support the del key in Opera because del == . == 46.
		var allowedKeys = [8, 9, 13, 35, 36, 37, 39, 46, 60, 62, 45];
		// IE doesn't support indexOf
		var isAllowedKey = allowedKeys.join(",").match(new RegExp(event.which));
		// Some browsers just don't raise events for control keys. Easy.
		// e.g. Safari backspace.
		if (!event.which || // Control keys in most browsers. e.g. Firefox tab is 0
			(48 <= event.which && event.which <= 57) || // Always 0 through 9
			isAllowedKey) { // Opera assigns values for control keys.
			return;
		} else {
			event.preventDefault();
		}
	});

	// Archetypes :int and IntegerWidget inputs get filtered
	$("input[name*='\\:int'], .ArchetypesIntegerWidget input").keyup(function(e) {
		if (/\D/g.test(this.value)) {
			this.value = this.value.replace(/\D/g, "");
		}
	});

	// Archetypes :float and DecimalWidget inputs get filtered
	$("input[name*='\\:float'], .ArchetypesDecimalWidget input").keyup(function(e) {
		if (/[^.\d]/g.test(this.value)) {
			this.value = this.value.replace(/[^.\d]/g, "");
		}
	});

});
}(jQuery));

