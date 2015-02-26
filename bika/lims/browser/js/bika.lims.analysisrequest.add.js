/**
 * Controller class for AnalysisRequestAddView
 */
function AnalysisRequestAddView() {

	var that = this;

	that.load = function () {

		ar_rename_elements();
		ar_referencewidget_lookups();
		ar_set_tabindexes();

		$("input[type=text]").prop("autocomplete", "off")

		$(".copyButton").live("click", copyButton);

		$("th[class^='analysiscategory']").click(clickAnalysisCategory);
		expand_default_categories();

		$("input[name^='Price']").live("change", recalc_prices);

		$("input[id*='_ReportDryMatter']").change(changeReportDryMatter);

		$(".spec_bit").live("change", function () {
			validate_spec_field_entry(this);
		});

		// AR Add/Edit ajax form submits
		loadAjaxSubmitHandler();

		// these go here so that popup windows can access them in our context
		window.recalc_prices = recalc_prices;
		window.calculate_parts = calculate_parts;
		window.toggleCat = toggleCat;

		// Filter data by the selected client
		filterByClient();

		// the copy_to_new button passes a copy_from request parameter
		// which is a UID or comma separated list oif UIDs.
		var copy_from = window.location.href.split("copy_from=");
		if (copy_from.length > 1) {
			copy_from = copy_from[1].split("&")[0];
			copy_from = copy_from.split(",");
			for (var column = 0; column < copy_from.length; column++) {
				// use this to pass column nr to the fill_column callback
				window.bika.ar_copy_from_col = column;
				// XXX async.
				$.ajaxSetup({async: false});
				window.bika.lims.jsonapi_read({
												  catalog_name: "uid_catalog",
												  UID: copy_from[column]
											  }, fill_column);
				$.ajaxSetup({async: true});
			}
		}
	}


	/**
	 *  AR Add/Edit ajax form submits
	 */
	function loadAjaxSubmitHandler() {
		var ar_edit_form = $("#analysisrequest_edit_form");
		var options = {
			url: window.location.href.split("/portal_factory")[0] + "/analysisrequest_submit",
			dataType: "json",
			data: {"_authenticator": $("input[name='_authenticator']").val()},
			beforeSubmit: function() {
				$("input[class~='context']").prop("disabled",true);
			},
			success: function(responseText) {
				var destination;
				if(responseText.success !== undefined){
					if(responseText.stickers !== undefined){
						destination = window.location.href
								.split("/portal_factory")[0];
						var ars = responseText.stickers;
						var template = responseText.stickertemplate;
						var q = "/sticker?template="+template+"&items=";
						q = q + ars.join(",");
						window.location.replace(destination+q);
					} else {
						destination = window.location.href
								.split("/portal_factory")[0];
						window.location.replace(destination);
					}
				} else {
					var msg = "";
					for(var error in responseText.errors){
						var x = error.split(".");
						var e;
						if (x.length == 2){
							e = x[1] + ", Column " + (+x[0]) + ": ";
						} else {
							e = "";
						}
						msg = msg + e + responseText.errors[error] + "<br/>";
					}
					window.bika.lims.portalMessage(msg);
					window.scroll(0,0);
					$("input[class~='context']").prop("disabled", false);
				}
			},
			error: function(XMLHttpRequest, statusText) {
				window.bika.lims.portalMessage(statusText);
				window.scroll(0,0);
				$("input[class~='context']").prop("disabled", false);
			}
		};
		$("#analysisrequest_edit_form").ajaxForm(options);
	}

	/**
	 * Show only the data (contacts, templates, etc.) for the selected
	 * client.   This is the initial filter, but the filters are re-applied
	 * each time a Client field is modified.
	 */
	function filterByClient() {
		// Iterate all the columns to filtrate by client
		for (var col = 0; col < parseInt($("#col_count").val(), 10); col++) {
			var element = $("#ar_" + col + "_Contact");
			var clientuid = $("#ar_" + col + "_Client_uid").val();
			// Initial value of contact list, set by the page's hidden ClientUID.
			applyComboFilter(element, "getParentUID", clientuid);
			element = $("#ar_" + col + "_CCContact");
			applyComboFilter(element, "getParentUID", clientuid);
			// Filter sample points by client
			element = $("#ar_" + col + "_SamplePoint");
			applyComboFilter(element, "getClientUID",
							 [clientuid, $("#bika_setup").attr("bika_samplepoints_uid")]);
			// Filter template by client
			element = $("#ar_" + col + "_Template");
			applyComboFilter(element, "getClientUID",
							 [clientuid, $("#bika_setup").attr("bika_artemplates_uid")]);
			// Filter Analysis Profile by client
			element = $("#ar_" + col + "_Profile");
			applyComboFilter(element, "getClientUID",
							 [clientuid, $("#bika_setup").attr("bika_analysisprofiles_uid")]);
			// Filter Analysis Spec by client
			element = $("#ar_" + col + "_Specification");
			applyComboFilter(element, "getClientUID",
							 [clientuid, $("#bika_setup").attr("bika_analysisspecs_uid")]);
		}
	}

	function destroy(arr, val) {
		for (var i = 0; i < arr.length; i++) if (arr[i] === val) arr.splice(i, 1);
		return arr;
	}

	function _set_specs(column){
		// This will set specs directly from the #specs or #copy_to_new_specs fields
		/* Specs are taken from the Specification element values (#specs).
		 If a spec is defined in copy_to_new_specs, it is used instead, and the
		 values in #specs have no effect. */
		var copy_to_new_specs = $.parseJSON($("#copy_to_new_specs").val());
		var specs = $.parseJSON($("#specs").val());
		var rr = copy_to_new_specs[column];
		if (rr == undefined || rr.length < 1) {
			rr = specs[column];
		}
		// Set values for selected analyses
		if (rr != undefined && rr.length > 0) {
			for (var i = 0; i < rr.length; i++) {
				var this_min = "[name='ar." + column + ".min." + rr[i].uid + "']";
				var this_max = "[name='ar." + column + ".max." + rr[i].uid + "']";
				var this_error = "[name='ar." + column + ".error." + rr[i].uid + "']";
				if ($(this_min).length > 0) {
					if ($(this_min).val() == "") {
						$(this_min).val(rr[i].min);
					}
					if ($(this_max).val() == "") {
						$(this_max).val(rr[i].max);
					}
					if ($(this_error).val() == "") {
						$(this_error).val(rr[i].error);
					}
				}
			}
		}
	}

	function set_specs(column){
		// Get the spec for this column, and check if the hidden #spec input must be updated
		var spec_uid = $("#ar_" + column + "_Specification_uid").val();
		if (spec_uid == "" || spec_uid == undefined || spec_uid == null) {
			_set_specs(column)
		}
		var request_data = {
			catalog_name: 'bika_setup_catalog',
			UID: spec_uid
		};
		window.bika.lims.jsonapi_read(request_data, function (data) {
			if (data.success && data.objects.length > 0) {
				// Update the #specs value.
				var element = $("#specs");
				var form_rr = $.parseJSON($(element).val());
                // If The Analysis Specification doesn't have results range, the form_rr[column]
                // should be a void dictionary
                if (data.objects[0]['ResultsRange'].length == 0) {
                    form_rr[column] = {};
                }
                else {
                    form_rr[column] = data.objects[0]['ResultsRange'];
                }
				$(element).val($.toJSON(form_rr));
				_set_specs(column)
			}
		});
	}

	function reset_spec_fields(arnum) {
		$("[name^='ar." + arnum + ".min']").val("");
		$("[name^='ar." + arnum + ".max']").val("");
		$("[name^='ar." + arnum + ".error']").val("");
	}

	function toggle_spec_fields(element) {
		// This flag disables spec inputs
		if (!$("#bika_setup").attr("EnableARSpecs")) {
			return;
		}
		// Specifications not allowed if ResultOptions used for service
		if (element.attr("has_resultoptions") == "True") {
			return;
		}

		var column = $(element).attr("column");
		var service_uid = $(element).attr("value");
		var min_name = "ar." + column + ".min." + service_uid;
		var max_name = "ar." + column + ".max." + service_uid;
		var error_name = "ar." + column + ".error." + service_uid;

		if ($(element).prop("checked") &&
				$(element).siblings().filter("[name='" + min_name + "']").length == 0) {
			var min = $("<input class='spec_bit min' type='text' size='3' uid='" + service_uid + "' value='' name='" + min_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='&gt;'/>");
			var max = $("<input class='spec_bit max' type='text' size='3' uid='" + service_uid + "' value='' name='" + max_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='&lt;'/>");
			var error = $("<input class='spec_bit error' type='text' size='3' uid='" + service_uid + "' value='' name='" + error_name + "' keyword='" + $(element).attr("keyword") + "' autocomplete='off' placeholder='%'/>");
			$(element).after(error).after(max).after(min);
		} else {
			$("input[name='" + min_name + "']").remove();
			$("input[name='" + max_name + "']").remove();
			$("input[name='" + error_name + "']").remove();
		}
		set_specs(column);
	}

	function validate_spec_field_entry(element) {
		var column = $(element).attr("name").split(".")[1];
		var uid = $(element).attr("uid");
		$("[name^='ar\\."+column+"\\.Specification']").val("");
		$("[name^='ar\\."+column+"\\.Specification_uid']").val("");
		var min_element = $("[name='ar."+column+".min."+uid+"']");
		var max_element = $("[name='ar."+column+".max."+uid+"']");
		var error_element = $("[name='ar."+column+".error."+uid+"']");
		var min = parseFloat($(min_element).val(), 10);
		var max = parseFloat($(max_element).val(), 10);
		var error = parseFloat($(error_element).val(), 10);
		if($(element).hasClass("min")){
			if(isNaN(min)) {
				$(min_element).val("");
			} else if ((!isNaN(max)) && min > max) {
				$(max_element).val("");
			}
		} else if($(element).hasClass("max")){
			if(isNaN(max)) {
				$(max_element).val("");
			} else if ((!isNaN(min)) && max < min) {
				$(min_element).val("");
			}
		} else if($(element).hasClass("error")){
			if(isNaN(error) || error < 0 || error > 100){
				$(error_element).val("");
			}
		}
	}

	function set_cc_contacts(column) {
		var contact_uid = $("#ar_"+column+"_Contact_uid").val();
		var fieldName = "ar."+column+".CCContact";
		// clear the CC widget
		$("input[name='"+fieldName+":record']").val("");
		$("input[name='"+fieldName+":record']").attr("uid", "");
		$("input[name='"+fieldName+"_uid']").val("");
		$("#ar_"+column+"_CCContact-listing").empty();
		if(contact_uid !== ""){
			var request_data = {
				portal_type: "Contact",
				UID: contact_uid
			};
			window.bika.lims.jsonapi_read(request_data, function(data) {
				if(data.objects && data.objects.length < 1) {
					return;
				}
				var ob = data.objects[0];
				var cc_titles = ob.CCContact;
				var cc_uids = ob.CCContact_uid;
				if(!cc_uids) {
					return;
				}
				$("input[name='"+fieldName+"_uid']").val(cc_uids.join(","));
				for (var i = 0; i < cc_uids.length; i++) {
					var title = cc_titles[i];
					var uid = cc_uids[i];
					var del_btn_src = window.portal_url+"/++resource++bika.lims.images/delete.png";
					var del_btn = "<img class='ar_deletebtn' src='"+del_btn_src+"' fieldName='"+fieldName+"' uid='"+uid+"'/>";
					var new_item = "<div class='reference_multi_item' uid='"+uid+"'>"+del_btn+title+"</div>";
					$("#ar_"+column+"_CCContact-listing").append($(new_item));
				}
			});
		}
	}

	function modify_Specification_field_filter(column) {
		// when a SampleType is selected I will allow only specs to be selected
		// which 1- (have the same Sample Types)
		// 2- (have no sample type at all)
		var sampletype_title = $("#ar_"+column+"_SampleType").val();
		var e = $("#ar_"+column+"_Specification");
		var query_str = $(e).attr("search_query");
		var query_obj = $.parseJSON(query_str);
		if (    query_obj.hasOwnProperty("getSampleTypeTitle") ){
			delete query_obj.getSampleTypeTitle;
		}
		query_obj.getSampleTypeTitle = [encodeURIComponent(sampletype_title), ""];
		query_str = $.toJSON(query_obj);
		$(e).attr("search_query", query_str);
	}

	function set_Specification_from_SampleType(column) {
		st_title = $("#ar_" + column + "_SampleType").val();
		st_uid = $("#ar_" + column + "_SampleType_uid").val();
		if (st_uid == undefined || st_uid == null || st_uid == "") {
			return;
		}
		spec_element = $("#ar_" + column + "_Specification");
		spec_uid_element = $("#ar_" + column + "_Specification_uid");
		var request_data = {
			catalog_name: "bika_setup_catalog",
			portal_type: "AnalysisSpec",
			getSampleTypeTitle: st_title,
			include_fields: ["Title", "UID"]
		};
		window.bika.lims.jsonapi_read(request_data, function (data) {
			if (data.objects.length > 0) {
				var spec = data.objects[0];
				// set spec values for this column
				$(spec_element).val(spec.Title);
				$(spec_uid_element).val(spec.UID);
				reset_spec_fields(column);
				set_specs(column);
			}
		});
	}

	function ar_set_tabindexes() {
		// Sets the tab index to the elements. Tab flow top to bottom instead of left
		// to right.
		// Keyboard tab flow top to bottom instead of left to right
		var index = 10;
		var count = $("input[id='col_count']").val();
		for (var i=0; i<count; i++) {
			var elements = $("td[column="+i+"]").find("input[type!=hidden]").not("[disabled]");
			for (var j=0; j<elements.length; j++) {
				$(elements[j]).attr("tabindex",index);
				index++;
			}
		}
	}

	// Configure the widgets that archetypes built:
	// set id and name to ar-col-fieldName formats
	// un-set the readonly attribute on the fields (so that we can search).
	function ar_rename_elements(){
		var i, e, elements, column;
		elements = $("td[ar_add_column_widget]").find("input[type!='hidden']").not("[disabled]");
		for (i = elements.length - 1; i >= 0; i--) {
			e = elements[i];
			column = $($(e).parents("td")).attr("column");
			// not :ignore_empty, widgets each get submitted to their own form handlers
			$(e).attr("name", "ar."+column+"."+$(e).attr("name")+":record");
			$(e).attr("id", "ar_"+column+"_"+e.id);
			$(e).removeAttr("required");
		}
		elements = $("td[ar_add_column_widget]").find("input[type='hidden']");
		for (i = elements.length - 1; i >= 0; i--) {
			e = elements[i];
			column = $($(e).parents("td")).attr("column");
			$(e).attr("id", "ar_"+column+"_"+e.id);
			// not :ignore_empty, widgets each get submitted to their own form handlers
			$(e).attr("name", "ar."+column+"."+$(e).attr("name")+":record");
		}
		elements = $(".multiValued-listing");
		for (i = elements.length - 1; i >= 0; i--) {
			e = elements[i];
			var eid = e.id.split("-listing")[0];
			column = $($(e).parents("td")).attr("column");
			$(e).attr("id", "ar_"+column+"_"+eid+"-listing");
			// not :ignore_empty, widgets each get submitted to their own form handlers
			$(e).attr("name", "ar."+column+"."+eid+"-listing");
			$(e).attr("fieldName", "ar."+column+"."+eid);
		}
		//Adding a unique identification to the widget's add button.
		elements = $("a.add_button_overlay");
		for (i = elements.length - 1; i >= 0; i--) {
			e = elements[i];
			column = $($(e).parents("td")).attr("column");
			var line = $(e).parents("div").attr("data-fieldname");
			$(e).attr("id", "ar_"+column+"_"+ e.id);
		}
	}

	// The columnar referencewidgets that we reconfigure use this as their
	// select handler.
	function ar_referencewidget_select_handler(event, ui){
		/*jshint validthis:true */
		event.preventDefault();

		// Set form values in activated element (must exist in colModel!)
		var column = $(this).attr("id").split("_")[1];
		var fieldName = $(this).attr("name").split(".")[2].split(":")[0];
		var skip;

		var uid_element = $("#ar_"+column+"_"+fieldName+"_uid");
		var listing_div = $("#ar_"+column+"_"+fieldName+"-listing");
		if(listing_div.length > 0) {
			// Add selection to textfield value
			var existing_uids = $(uid_element).val().split(",");
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
				var del_btn_src = portal_url+"/++resource++bika.lims.images/delete.png";
				var del_btn = "<img class='deletebtn' src='"+del_btn_src+"' fieldName='ar."+column+"."+fieldName+"' uid='"+selected_uid+"'/>";
				var new_item = "<div class='reference_multi_item' uid='"+selected_uid+"'>"+del_btn+selected_value+"</div>";
				$(listing_div).append($(new_item));
				$(uid_element).attr("skip_referencewidget_lookup", true)
			}
			skip = $(uid_element).attr("skip_referencewidget_lookup");
			$(this).next("input").focus();
		} else {
			// Set value in activated element (must exist in colModel!)
			$(this).val(ui.item[$(this).attr("ui_item")]);
			$(this).attr("uid", ui.item.UID);
			$(uid_element).val(ui.item.UID);
			skip = $(uid_element).attr("skip_referencewidget_lookup");
			if (skip !== true){
				$(this).trigger("selected", ui.item.UID);
			}
			$(uid_element).removeAttr("skip_referencewidget_lookup");
			$(this).next("input").focus();
		}

		if (fieldName == "Client") {
			var element = $("#ar_" + column + "_Contact");
			var clientuid = $(this).attr("uid");
			applyComboFilter(element, "getParentUID", clientuid);
			element = $("#ar_" + column + "_CCContact");
			applyComboFilter(element, "getParentUID", clientuid);
			// Filter sample points by client
			element = $("#ar_" + column + "_SamplePoint");
			applyComboFilter(element, "getClientUID",
							 [clientuid,
							  $("#bika_setup").attr("bika_samplepoints_uid")]);
			// Filter template by client
			element = $("#ar_" + column + "_Template");
			applyComboFilter(element, "getClientUID",
							 [clientuid,
							  $("#bika_setup").attr("bika_artemplates_uid")]);
			// Filter Analysis Profile by client
			element = $("#ar_" + column + "_Profile");
			applyComboFilter(element, "getClientUID",
							 [clientuid,
							  $("#bika_setup").attr("bika_analysisprofiles_uid")]);
			// Filter Analysis Spec by client
			element = $("#ar_" + column + "_Specification");
			applyComboFilter(element, "getClientUID",
							 [clientuid,
							  $("#bika_setup").attr("bika_analysisspecs_uid")]);
		}
		if(fieldName == "Contact"){
			set_cc_contacts(column);
		}
		if(fieldName == "SampleType"){
			//// selecting a Sampletype - jiggle the SamplePoint element.
			//var sp_element = $("#ar_"+column+"_SamplePoint");
			//sp_element
			//    .removeClass( "cg-autocomplete-input" )
			//    .removeAttr( "autocomplete" )
			//    .removeAttr( "role" )
			//    .removeAttr( "aria-autocomplete" )
			//    .removeAttr( "aria-haspopup" );
			//var new_sp_element = $(sp_element[0]).clone();
			//var sp_parent_node = $(sp_element).parent();
			//$(sp_element).remove();
			//$(sp_parent_node).append(new_sp_element);
			//var sp_search_query = {"getSampleTypeTitle": [encodeURIComponent(ui.item[$(this).attr("ui_item")]), ""]};
			//sp_search_query = $.toJSON(sp_search_query);
			//sp_element.attr("search_query", sp_search_query);
			//ar_referencewidget_lookups(sp_element);
			// Template gets removed, as it no longer matches the SampleType.
			unsetTemplate(column);
			// Discover if we have a Specification linked to the SampleType
			set_Specification_from_SampleType(column);
			// Fix filter for Specs to exclude Spec with non matching sample type
			modify_Specification_field_filter(column);
			// Fix the spec values to reflect the new specification ranges
			set_specs(column);
			calculate_parts(column);
		}
		if(fieldName == "SamplePoint"){
			// selecting a Samplepoint - jiggle the SampleType element.
			var st_element = $("#ar_"+column+"_SampleType");
			st_element
					.removeClass( "cg-autocomplete-input" )
					.removeAttr( "autocomplete" )
					.removeAttr( "role" )
					.removeAttr( "aria-autocomplete" )
					.removeAttr( "aria-haspopup" );
			var new_st_element = $(st_element[0]).clone();
			var st_parent_node = $(st_element).parent();
			$(st_element).remove();
			$(st_parent_node).append(new_st_element);
			st_element = $("#ar_"+column+"_SampleType");
			// cut kwargs into the base_query
//            var st_base_query = $(st_element).attr("base_query");
//            st_base_query = $.parseJSON(st_base_query);
//            st_base_query = $.toJSON(st_base_query);
			var st_search_query = {"getRawSamplePoints": $(this).attr("uid")};
			st_search_query = $.toJSON(st_search_query);
			st_element.attr("search_query", st_search_query);
			ar_referencewidget_lookups(st_element);
		}

		// Selected a Profile
		if(fieldName == "Profile"){
			unsetTemplate(column);
			setAnalysisProfile(column, $(this).val());
			calculate_parts(column);
			reset_spec_fields(column);
			set_specs()
		}

		// Selected a Template
		if(fieldName == "Template"){
			setTemplate(column, $(this).val());
			reset_spec_fields(column);
			set_specs(column);
		}

		// Selected a sample to create a secondary AR.
		if(fieldName == "Sample"){
			// var e = $("input[name^='ar\\."+column+"\\."+fieldName+"']");
			// var Sample = $("input[name^='ar\\."+column+"\\."+fieldName+"']").val();
			// var Sample_uid = $("input[name^='ar\\."+column+"\\."+fieldName+"_uid']").val();
			// Install the handler which will undo the changes I am about to make
			$(this).blur(function(){
				if($(this).val() === ""){
					// clear and un-disable everything
					var disabled_elements = $("[ar_add_column_widget] [id*='ar_"+column+"']:disabled");
					$.each(disabled_elements, function(x,disabled_element){
						$(disabled_element).prop("disabled", false);
						if($(disabled_element).attr("type") == "checkbox"){
							$(disabled_element).prop("checked", false);
						} else {
							$(disabled_element).val("");
						}
					});
				}
			});
			// Then populate and disable sample fields
			$.getJSON(window.location.href.replace("/ar_add","") + "/secondary_ar_sample_info",
					  {
						  "Sample_uid": $(this).attr("uid"),
						  "_authenticator": $("input[name='_authenticator']").val()},
					  function(data){
						  for (var x = data.length - 1; x >= 0; x--) {
							  var fieldname = data[x][0];
							  var fieldvalue = data[x][1];
							  var uid_element = $("#ar_"+column+"_"+fieldname+"_uid");
							  $(uid_element).val("");
							  var sample_element = $("#ar_"+column+"_"+fieldname);
							  $(sample_element).val("").prop("disabled", true);
							  if($(sample_element).attr("type") == "checkbox" && fieldvalue){
								  $(sample_element).prop("checked", true);
							  } else {
								  $(sample_element).val(fieldvalue);
							  }
						  }
					  }
			);
		}

		// Selected a Specification
		if(fieldName == "Specification"){
			reset_spec_fields(column);
			set_specs(column);
		}

		// Triggers 'selected' event (as reference widget)
		if (!skip){
		$(this).trigger("selected", ui.item.UID);
		}
	}

	function add_path_filter_to_spec_lookups(){
		for (var col=0; col<parseInt($("#col_count").val(), 10); col++) {
			var element = $("#ar_"+col+"_Specification");
			var bq = $.parseJSON($(element).attr("base_query"));
			bq.path = [$("#bika_setup").attr("bika_analysisspecs_path"),
					   $("#PhysicalPath").attr("here")];
			$(element).attr("base_query", $.toJSON(bq));
		}
	}

	// we do the referencewidget_lookups differently to the widget default.
	// We also include a bunch of ar_add specific on-change stuff, since the
	// popup widget takes over the .change event completely.
	function ar_referencewidget_lookups(elements){
		add_path_filter_to_spec_lookups();
		var inputs;
		if(elements === undefined){
			inputs = $("input.referencewidget").not(".has_combogrid_widget");
		} else {
			inputs = elements;
		}
		for (var i = inputs.length - 1; i >= 0; i--) {
			var element = inputs[i];
			var options = $.parseJSON($(element).attr("combogrid_options"));
			if(options === "" || options === undefined){
				continue;
			}
			options.select = ar_referencewidget_select_handler;

			if(window.location.href.search("ar_add") > -1){
				options.url = window.location.href.split("/ar_add")[0] + "/" + options.url;
			}
			options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
			options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
			options.url = options.url + "&base_query=" + $(element).attr("base_query");
			options.url = options.url + "&search_query=" + $(element).attr("search_query");
			options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(element).attr("combogrid_options")).colModel);
			options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
			options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
			$(element).combogrid(options);
			$(element).addClass("has_combogrid_widget");
			$(element).attr("search_query", "{}");
		}
	}

	function recalc_prices(column){
		if(column){
			// recalculate just this column
			var subtotal = 0.00;
			var discount_amount = 0.00;
			var vat = 0.00;
			var total = 0.00;
			var discount = parseFloat($("#member_discount").val());
			$.each($("input[name='ar."+column+".Analyses:list:ignore_empty:record']"), function(){
				var disabled = $(this).prop("disabled");
				// For some browsers, `attr` is undefined; for others, its false.  Check for both.
				if (typeof disabled !== "undefined" && disabled !== false) {
					disabled = true;
				} else {
					disabled = false;
				}
				if(!(disabled) && $(this).prop("checked")){
					var serviceUID = this.id;
					var form_price = parseFloat($("#"+serviceUID+"_price").val());
					var vat_amount = parseFloat($("#"+serviceUID+"_price").attr("vat_amount"));
					var price;
					if(discount){
						price = form_price - ((form_price / 100) * discount);
					} else {
						price = form_price;
					}
					subtotal += price;
					discount_amount += ((form_price / 100) * discount);
					vat += ((price / 100) * vat_amount);
					total += price + ((price / 100) * vat_amount);
				}
			});
			$("#ar_"+column+"_subtotal").val(subtotal.toFixed(2));
			$("#ar_"+column+"_subtotal_display").val(subtotal.toFixed(2));
			$("#ar_"+column+"_discount").val(discount_amount.toFixed(2));
			$("#ar_"+column+"_vat").val(vat.toFixed(2));
			$("#ar_"+column+"_vat_display").val(vat.toFixed(2));
			$("#ar_"+column+"_total").val(total.toFixed(2));
			$("#ar_"+column+"_total_display").val(total.toFixed(2));
		} else {
			// recalculate the entire form
			for (var col=0; col<parseInt($("#col_count").val(), 10); col++) {
				recalc_prices(String(col));
			}
		}
	}

	function changeReportDryMatter(){
		/*jshint validthis:true */
		var dm = $("#getDryMatterService");
		var uid = $(dm).val();
		var cat = $(dm).attr("cat");
		var poc = $(dm).attr("poc");
		var column = $(this).parents("td").attr("column");
		if ($(this).prop("checked")){
			// only play with service checkboxes when enabling dry matter
			unsetAnalysisProfile(column);
			$.ajaxSetup({async:false});
			toggleCat(poc, cat, column, [uid], true);
			$.ajaxSetup({async:true});
			var dryservice_cb = $("input[column='"+column+"']:checkbox").filter("#"+uid);
			$(dryservice_cb).prop("checked",true);
			calcdependencies([$(dryservice_cb)], true);
			calculate_parts(column);
		}
		recalc_prices();
	}

	function copy_service(copybutton){
		var e = $("input[column='0']").filter("#" + copybutton.id);
		var kw = $(e).attr("keyword");
		var service_uid = $(e).prop("value");
		// get column 0 values
		var first_val = $(e).prop("checked");
		var first_min = $("[name='ar.0.min." + service_uid + "']").prop("value");
		var first_max = $("[name='ar.0.max." + service_uid + "']").prop("value");
		var first_error = $("[name='ar.0.error." + service_uid + "']").prop("value");

		var col_count = parseInt($("#col_count").val(), 10);
		var affected_elements = [];
		// 0 is the first column; we only want to change cols 1 onward.
		for (var column = 1; column < col_count; column++) {
			unsetTemplate(column);
			unsetAnalysisProfile(column);
			var other_elem = $("input[column='" + column + "']").filter("#" + copybutton.id);
			if ((!other_elem.prop("disabled")) && (other_elem.prop("checked") != first_val)) {
				other_elem.prop("checked", first_val ? true : false);
				toggle_spec_fields(other_elem);
				affected_elements.push(other_elem);
			}
			if (first_val) {
				$(".spec_bit.min[column='" + column + "']").filter("[keyword='" + kw + "']")
						.prop("value", first_min);
				$(".spec_bit.max[column='" + column + "']").filter("[keyword='" + kw + "']")
						.prop("value", first_max);
				$(".spec_bit.error[column='" + column + "']").filter("[keyword='" + kw + "']")
						.prop("value", first_error);
			}
			calculate_parts(column);
		}
		calcdependencies(affected_elements, true);
		recalc_prices();
	}

	function copy_checkbox(copybutton){
		var fieldName = $(copybutton).attr("name");
		var first_val = $("input[name^='ar\\.0\\."+fieldName+"']").prop("checked");
		var col_count = parseInt($("#col_count").val(), 10);
		// col starts at 1 here; we don't copy into the the first row
		for (var col=1; col<col_count; col++) {
			var other_elem = $("#ar_" + col + "_" + fieldName);
			if ((other_elem.prop("checked")!=first_val)) {
				other_elem.prop("checked",first_val?true:false);
				other_elem.trigger("change");
			}
		}
		$("[id*='_" + fieldName + "']").change();
	}

	function copyButton(){
		/*jshint validthis:true */
		var fieldName = $(this).attr("name");
		var col_count = parseInt($("#col_count").val(), 10);

		if ($(this).parent().attr("class") == "service"){
			copy_service(this);
		}

		else if ($("input[name^='ar\\.0\\."+fieldName+"']").attr("type") == "checkbox") {
			copy_checkbox(this);
		}

		// Anything else

		else{
			var first_val = $("input[name^='ar\\.0\\."+fieldName+"']").filter("[type=text]").val();
			// Reference fields have a hidden *_uid field
			var first_uid = $("input[name^='ar\\.0\\."+fieldName+"_uid']").val();
			// multi-valued fields: selection is in {fieldname}-listing
			var first_multi_html = $("div[name^='ar\\.0\\."+fieldName+"-listing']").html();
			// col starts at 1 here; we don't copy into the the first row
			for (var col=1; col<col_count; col++) {
				var other_uid_elem = $("#ar_" + col + "_" + fieldName + "_uid");
				if (first_uid !== undefined && first_uid !== null){
					other_uid_elem.val(first_uid);
				}
				var other_multi_div = $("div[name^='ar\\."+col+"\\."+fieldName+"-listing']");
				if (first_multi_html !== undefined && first_multi_html !== null){
					other_multi_div.html(first_multi_html.replace(".0.", "."+col+"."));
				}
				// Actual field value
				var other_elem = $("#ar_" + col + "_" + fieldName);
				if (!(other_elem.prop("disabled"))) {
					$(other_elem).attr("skip_referencewidget_lookup", true);
					other_elem.val(first_val);
					other_elem.trigger("change");

					if(fieldName == "Contact") {
						set_cc_contacts(col);
					}

					if(fieldName == "Profile"){
						unsetTemplate(col);
						setAnalysisProfile(col, first_val);
						calculate_parts(col);
					}

					if(fieldName == "Template"){
						setTemplate(col, first_val);
					}

					if(fieldName == "SampleType"){
						unsetTemplate(col);
						calculate_parts(col);
						set_specs(col);
					}

					if(fieldName == "Specification"){
						set_specs(col);
						reset_spec_fields(col);
					}

				}
			}
			//$('[id*=_' + fieldName + "]").change();
		}
	}



	function toggleCat(poc, category_uid, column, selectedservices, force_expand, disable) {
		// selectedservices and column are optional.
		// disable is used for field analyses - secondary ARs should not be able
		// to select these
		force_expand = force_expand || false;
		disable = disable || -1;
		if(!column && column !== 0) { column = ""; }

		var th = $("th[poc='"+poc+"']").filter("[cat='"+category_uid+"']");
		var tbody = $("#"+poc+"_"+category_uid);

		if($(tbody).hasClass("expanded")){
			// displaying an already expanded category:
			if(selectedservices){
				var rows = tbody.children();
				for(var i = 0; i < rows.length; i++){
					var service = rows[i];
					var service_uid = $(service).attr("id");
					if(selectedservices.indexOf(service_uid) > -1){
						var cb = $("input[value="+service_uid+"]").filter("[column='"+column+"']");
						$(cb).prop("checked",true);
						toggle_spec_fields(cb);
					}
				}
				recalc_prices(column);
			} else {
				if (force_expand){ $(tbody).toggle(true); }
				else { $(tbody).toggle(); }
			}
		} else {
			if(!selectedservices) selectedservices = [];
			$(tbody).removeClass("collapsed").addClass("expanded");
			var options = {
				"selectedservices": selectedservices.join(","),
				"categoryUID": category_uid,
				"column": column,
				"disable": disable > -1 ? column : -1,
				"col_count": $("#col_count").attr("value"),
				"poc": poc
			};
			// possibly remove the fake ar context
			var url = window.location.href.split("/ar_add")[0] + "/analysisrequest_analysisservices";
			$(tbody).load(url, options, function(){
				// analysis service checkboxes
				$("input[name*='Analyses']").unbind();
				$("input[name*='Analyses']").bind("change", service_checkbox_change);
				if(selectedservices!=[]){
					recalc_prices(column);
					for(i=0;i<selectedservices.length;i++){
						var service_uid = selectedservices[i];
						var e = $("input[value=" + service_uid + "]").filter("[column='" + column + "']");
						toggle_spec_fields(e);
					}
				}
			});
		}
	}

	function calc_parts_handler(column, data){
		// Set new part numbers in hidden form field
		var formparts = $.parseJSON($("#parts").val());
		var parts = data.parts;
		formparts[column] = parts;
		$("#parts").val($.toJSON(formparts));
		// write new part numbers next to checkboxes
		for(var p in parts) { if(!parts.hasOwnProperty(p)){ continue; }
			for (var s in parts[p].services) {
				if (!parts[p].services.hasOwnProperty(s)) { continue; }
				$(".partnr_"+parts[p].services[s]).filter("[column='"+column+"']").empty().append(p+1);
			}
		}
	}

	function calculate_parts(column) {
		// Template columns are not calculated
		if ($("#ar_"+column+"_Template").val() !== ""){
			return;
		}
		var st_uid = $("#ar_"+column+"_SampleType_uid").val();
		var checked = $("[name^='ar\\."+column+"\\.Analyses']").filter(":checked");
		var service_uids = [];
		for(var i=0;i<checked.length;i++){
			var uid = $(checked[i]).attr("value");
			service_uids.push(uid);
		}
		// if no sampletype or no selected analyses:  remove partition markers
		if (st_uid === "" || service_uids.length === 0) {
			$("[class*='partnr_']").filter("[column='"+column+"']").empty();
			return;
		}
		var request_data = {
			services: service_uids.join(","),
			sampletype: st_uid,
			_authenticator: $("input[name='_authenticator']").val()
		};
		window.jsonapi_cache = window.jsonapi_cache || {};
		var cacheKey = $.param(request_data);
		if (typeof window.jsonapi_cache[cacheKey] === "undefined") {
			$.ajax({
					   type: "POST",
					   dataType: "json",
					   url: window.portal_url + "/@@API/calculate_partitions",
					   data: request_data,
					   success: function(data) {
						   // Check if calculation succeeded
						   if (data.success == false) {
							   alert('Error while calculating partitions: ' + data.message);
						   } else {
							   window.jsonapi_cache[cacheKey] = data;
							   calc_parts_handler(column, data);
						   }
					   }
				   });
		} else {
			var data = window.jsonapi_cache[cacheKey];
			calc_parts_handler(column, data);
		}
	}

	function add_Yes(dlg, element, dep_services){
		/*jshint validthis:true */
		var column = $(element).attr("column");
		var key, json_key, dep, i;
		var keyed_deps = {};
		for(i = 0; i<dep_services.length; i++){
			dep = dep_services[i];
			key = {
				col: column,
				poc: dep.PointOfCapture,
				cat_uid: dep.Category_uid
			};
			json_key = $.toJSON(key);
			if(!keyed_deps[json_key]){
				keyed_deps[json_key] = [];
			}
			keyed_deps[json_key].push(dep.Service_uid);
		}

		var modified_cols = [];
		for(json_key in keyed_deps){
			if (!keyed_deps.hasOwnProperty(json_key)){ continue; }
			key = $.parseJSON(json_key);
			if(!modified_cols[key.col]){
				modified_cols.push(key.col);
			}
			var service_uids = keyed_deps[json_key];
			var tbody = $("#"+key.poc+"_"+key.cat_uid);
			if($(tbody).hasClass("expanded")) {
				// if cat is already expanded, manually select service checkboxes
				$(tbody).toggle(true);
				for(i=0; i<service_uids.length; i++){
					var service_uid = service_uids[i];
					var e = $("input[column='"+key.col+"']").filter("#"+service_uid);
					$(e).prop("checked",true);
					toggle_spec_fields(e);
					set_specs(col)
				}
			} else {
				// otherwise, toggleCat will take care of everything for us
				$.ajaxSetup({async:false});
				toggleCat(key.poc, key.cat_uid, key.col, service_uids);
				$.ajaxSetup({async:true});
				set_specs(col)
			}
		}
		recalc_prices();
		for(i=0; i<modified_cols.length; i+=1){
			calculate_parts(modified_cols[i]);
		}
		$(dlg).dialog("close");
		$("#messagebox").remove();


	}

	function add_No(dlg, element){
		/*jshint validthis:true */
		$(element).prop("checked",false);
		$(dlg).dialog("close");
		$("#messagebox").remove();
	}

	function calcdependencies(elements, auto_yes) {
		/*jshint validthis:true */
		auto_yes = auto_yes || false;
		jarn.i18n.loadCatalog('bika');
		var _ = window.jarn.i18n.MessageFactory("bika");

		var dep;
		var dep_i, cb;

		var lims = window.bika.lims;

		for(var elements_i = 0; elements_i < elements.length; elements_i++){
			var dep_services = [];  // actionable services
			var dep_titles = [];
			var element = elements[elements_i];
			var column = $(element).attr("column");
			var service_uid = $(element).attr("id");
			var modified_cols = [];
			// selecting a service; discover dependencies
			if ($(element).prop("checked")){
				var Dependencies = lims.AnalysisService.Dependencies(service_uid);
				for(dep_i = 0; dep_i<Dependencies.length; dep_i++) {
					dep = Dependencies[dep_i];
					if ($("input[column='"+column+"']").filter("#"+dep.Service_uid).prop("checked")){
						continue; // skip if checked already
					}
					dep_services.push(dep);
					dep_titles.push(dep.Service);
				}

				if (dep_services.length > 0) {
					if(!modified_cols[column]){
						modified_cols.push(column);
					}
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
				if (Dependants.length > 0){
					for (i=0; i<Dependants.length; i++){
						dep = Dependants[i];
						cb = $("input[column='"+column+"']").filter("#"+dep.Service_uid);
						if (cb.prop("checked")){
							dep_titles.push(dep.Service);
							dep_services.push(dep);
						}
					}
					if(dep_services.length > 0){
						if (auto_yes) {
							for(dep_i=0; dep_i<dep_services.length; dep_i+=1) {
								dep = dep_services[dep_i];
								service_uid = dep.Service_uid;
								cb = $("input[column='"+column+"']").filter("#"+service_uid);
								$(cb).prop("checked", false);
								toggle_spec_fields($(cb));
								$(".partnr_"+service_uid).filter("[column='"+column+"']").empty();
								if ($(cb).val() == $("#getDryMatterService").val()) {
									$("#ar_"+column+"_ReportDryMatter").prop("checked",false);
								}
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
															Yes: function(){
																for(dep_i=0; dep_i<dep_services.length; dep_i+=1) {
																	dep = dep_services[dep_i];
																	service_uid = dep.Service_uid;
																	cb = $("input[column='"+column+"']").filter("#"+service_uid);
																	$(cb).prop("checked", false);
																	toggle_spec_fields($(cb));
																	$(".partnr_"+service_uid).filter("[column='"+column+"']").empty();
																	if ($(cb).val() == $("#getDryMatterService").val()) {
																		$("#ar_"+column+"_ReportDryMatter").prop("checked",false);
																	}
																}
																$(this).dialog("close");
																$("#messagebox").remove();
															},
															No:function(){
																$(element).prop("checked",true);
																toggle_spec_fields($(element));
																$(this).dialog("close");
																$("#messagebox").remove();
															}
														}
													});
						}
					}
				}
			}
			recalc_prices();
			for(var i=0; i<modified_cols.length; i+=1){
				calculate_parts(modified_cols[i]);
			}
		}
	}

	function unsetAnalyses(column){
		$.each($("input[name^='ar."+column+".Analyses']"), function(){
			if($(this).prop("checked")) {
				$(this).prop("checked",false);
				toggle_spec_fields($(this));
			}
			$(".partnr_"+this.id).filter("[column='"+column+"']").empty();
		});
	}
	// function uncheck_partnrs(column){
	//  // all unchecked services have their part numbers removed
	//  var ep = $("[class^='partnr_']").filter("[column='"+column+"']").not(":empty");
	//  for(var i=0;i<ep.length;i++){
	//      var em = ep[i];
	//      var uid = $(ep[0]).attr("class").split("_")[1];
	//      var cb = $("#"+uid);
	//      if ( ! $(cb).prop("checked") ){
	//          $(em).empty();
	//      }
	//  }
	// }

	function unsetAnalysisProfile(column){
		if($("#ar_"+column+"_Profile").val() !== ""){
			$("#ar_"+column+"_Profile").val("");
		}
	}


	function unsetTemplate(column){
		if($("#ar_"+column+"_Template").val() !== ""){
			$("#ar_"+column+"_Template_uid").val("");
		}
	}


	function setTemplate(column, template_title){
		unsetAnalyses(column);
		var request_data = {
			portal_type: "ARTemplate",
			title: template_title,
			include_fields: [
				"SampleType",
				"SampleTypeUID",
				"SamplePoint",
				"SamplePointUID",
				"ReportDryMatter",
				"AnalysisProfile",
				"Partitions",
				"Analyses"]
		};
		window.bika.lims.jsonapi_read(request_data, function(data){
			var template = data.objects[0];
			var request_data, x, i;
			// set our template fields
			$("#ar_"+column+"_SampleType").val(template.SampleType)
			$("#ar_"+column+"_SampleType_uid").val(template.SampleTypeUID)
			set_Specification_from_SampleType(column)
			$("#ar_"+column+"_SamplePoint").val(template.SamplePoint)
			$("#ar_"+column+"_SamplePoint_uid").val(template.SamplePointUID)
			$("#ar_"+column+"_reportdrymatter").prop("checked", template.reportdrymatter)

			// lookup AnalysisProfile
			if(template.AnalysisProfile) {
				request_data = {
					portal_type: "AnalysisProfile",
					title: template.AnalysisProfile,
					include_fields: ["UID"]
				};
				window.bika.lims.jsonapi_read(request_data, function(data){
					$("#ar_"+column+"_Profile").val(template.AnalysisProfile);
					$("#ar_"+column+"_Profile_uid").val(data.objects[0].UID);
				});
			} else {
				$("#ar_"+column+"_Profile").val("");
				$("#ar_"+column+"_Profile_uid").val("");
			}

			// scurrel the parts into hashes for easier lookup
			var parts_by_part_id = {};
			var parts_by_service_uid = {};
			for (x in template.Partitions) {
				if (!template.Partitions.hasOwnProperty(x)){ continue; }
				var P = template.Partitions[x];
				P.part_nr = parseInt(P.part_id.split("-")[1], 10);
				P.services = [];
				parts_by_part_id[P.part_id] = P;
			}
			for (x in template.Analyses) {
				if(!template.Analyses.hasOwnProperty(x)){ continue; }
				i = template.Analyses[x];
				parts_by_part_id[i.partition].services.push(i.service_uid);
				parts_by_service_uid[i.service_uid] = parts_by_part_id[i.partition];
			}
			// this one goes through with the form submit
			var parts = [];
			for(x in parts_by_part_id){
				if(!parts_by_part_id.hasOwnProperty(x)){ continue; }
				parts.push(parts_by_part_id[x]);
			}
			var formparts = $.parseJSON($("#parts").val());
			formparts[column] = parts;
			$("#parts").val($.toJSON(formparts));

			// lookup the services specified in the template
			request_data = {
				portal_type: "AnalysisService",
				UID: [],
				include_fields: ["PointOfCapture", "CategoryUID", "UID"]
			};
			for (x in template.Analyses) {
				if (!template.Analyses.hasOwnProperty(x)){ continue; }
				request_data.UID.push(template.Analyses[x].service_uid);
			}
			// save services in hash for easier lookup this
			window.bika.lims.jsonapi_read(request_data, function(data) {
				var e;
				var poc_cat_services = {};
				for(var x in data.objects) {
					if(!data.objects.hasOwnProperty(x)){ continue; }
					var service = data.objects[x];
					var poc_title = service.PointOfCapture;
					if (!(poc_title in poc_cat_services)) {
						poc_cat_services[poc_title] = {};
					}
					if (!(service.CategoryUID in poc_cat_services[poc_title])) {
						poc_cat_services[poc_title][service.CategoryUID] = [];
					}
					poc_cat_services[poc_title][service.CategoryUID].push(service.UID);
				}
				// expand categories, select, and enable controls for template services
				for (var p in poc_cat_services) {
					if (!poc_cat_services.hasOwnProperty(p)){ continue; }
					var poc = poc_cat_services[p];
					for (var cat_uid in poc) {
						if (!poc.hasOwnProperty(cat_uid)) {continue; }
						var service_uids = poc[cat_uid];
						var tbody = $("tbody[id='"+p+"_"+cat_uid+"']");
						var service_uid;
						// expand category
						if(!($(tbody).hasClass("expanded"))) {
							$.ajaxSetup({async:false});
							toggleCat(p, cat_uid, 0);
							$.ajaxSetup({async:true});
						}
						$(tbody).toggle(true);
						// select checkboxes
						for(i=0;i<service_uids.length;i++){
							service_uid = service_uids[i];
							e = $("input[column='"+column+"']").filter("#"+service_uid);
							$(e).prop("checked", true);
							toggle_spec_fields(e);
						}
						// set part number indicators
						for(i=0;i<service_uids.length;i++){
							service_uid = service_uids[i];
							var partnr = parseInt(parts_by_service_uid[service_uid].part_nr, 10);
							e = $(".partnr_"+service_uid).filter("[column='"+column+"']");
							$(e).empty().append(partnr);
						}
						recalc_prices(column);
					}
				}
			});
		});

		recalc_prices(column);

	}

	function setAnalysisProfile(column, profile_title){
		var request_data = {
			portal_type: "AnalysisProfile",
			title: profile_title
		};
		window.bika.lims.jsonapi_read(request_data, function(data){
			var profile_objects = data.objects;
			var request_data = {
				portal_type: "AnalysisService",
				title: profile_objects[0].Service,
				include_fields: ["PointOfCapture", "Category", "UID", "title"]
			};
			window.bika.lims.jsonapi_read(request_data, function(data){
				var i;
				unsetAnalyses(column);
				$("#ar_"+column+"_ReportDryMatter").prop("checked",false);

				var service_objects = data.objects;
				if (service_objects.length === 0) return;
				var categorised_services = {};
				for (i in service_objects){
					var key = service_objects[i].PointOfCapture + "_" +
							service_objects[i].Category;
					if(categorised_services[key] === undefined)
						categorised_services[key] = [];
					categorised_services[key].push(service_objects[i]);
				}

				for (var poc_cat in categorised_services) {
					var services = categorised_services[poc_cat];
					var th = $("th#cat_"+poc_cat);
					if($(th).hasClass("expanded")){
						for (i in services){
							var service_uid = services[i].UID;
							var e = $("input[column='"+column+"']").filter("#"+service_uid);
							$(e).prop("checked", true);
						}
						recalc_prices(column);
					} else {
						var poc = poc_cat.split("_")[0];
						var cat_uid = services[0].Category_uid;
						var service_uids = [];
						for(var x = 0; x<services.length;x++){
							service_uids.push(services[x].UID);
						}
						$.ajaxSetup({async:false});
						toggleCat(poc, cat_uid, column, service_uids);
						$.ajaxSetup({async:true});
					}
					$(th).removeClass("collapsed").addClass("expanded");
				}
				calculate_parts(column);
			});
		});
	}

	function service_checkbox_change(){
		/*jshint validthis:true */
		var column = $(this).attr("column");
		var element = $(this);
		unsetAnalysisProfile(column);
		unsetTemplate(column);

		// Unselecting Dry Matter Service unsets 'Report Dry Matter'
		if ($(this).val() == $("#getDryMatterService").val() && !$(this).prop("checked")) {
			$("#ar_"+column+"_ReportDryMatter").prop("checked",false);
		}

		// unselecting service: remove part number.
		if (!$(this).prop("checked")){
			$(".partnr_"+this.id).filter("[column='"+column+"']").empty();
		}

		calcdependencies([element]);
		recalc_prices();
		calculate_parts(column);
		toggle_spec_fields(element);

	}

	function clickAnalysisCategory(){
		/*jshint validthis:true */
		// cat is a category uid, and no column is required here.
		toggleCat($(this).attr("poc"), $(this).attr("cat"));
		if($(this).hasClass("expanded")){
			$(this).addClass("collapsed");
			$(this).removeClass("expanded");
		} else {
			$(this).removeClass("collapsed");
			$(this).addClass("expanded");
		}
	}

	function applyComboFilter(element, filterkey, filtervalue) {
		// If the element is not visible it is probably not worth creating a dropdown query.
		if (!$(element).is(':visible')){
			return;
		}
		var base_query=$.parseJSON($(element).attr("base_query"));
		base_query[filterkey] = filtervalue;
		$(element).attr("base_query", $.toJSON(base_query));
		var options = $.parseJSON($(element).attr("combogrid_options"));
		options.url = window.location.href.split("/ar_add")[0] + "/" + options.url;
		options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
		options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name");
		options.url = options.url + "&base_query=" + $.toJSON(base_query);
		options.url = options.url + "&search_query=" + $(element).attr("search_query");
		options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(element).attr("combogrid_options")).colModel);
		options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields);
		options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty);
		options.force_all="false";
		$(element).combogrid(options);
		$(element).addClass("has_combogrid_widget");
		$(element).attr("search_query", "{}");
	}

	function fill_column(data) {
		// fields which should not be completed from the source AR
		var skip_fields = ['Sample',
						   'Sample_uid',
						   'SamplingDate',
						   'DateSampled',
						   'Sampler']
		// if the jsonapi read data did not include any objects, abort
		// obviously, shouldn't happen
		if ((!data.success) || data.objects.length < 1) {
			return;
		}
		var obj = data.objects[0];
		// this is the column containing the elements we will write into
		var col = window.bika.ar_copy_from_col;
		// set field values from data into respective elements.  data does include
		// *_uid entries for reference field values, so the corrosponding *_uid
		// hidden elements are written here
		for (var fieldname in obj) {
			if (!obj.hasOwnProperty(fieldname)) { continue; }
			if (skip_fields.indexOf(fieldname) > -1) { continue; }
			var fieldvalue = obj[fieldname];
			var el = $("#ar_" + col + "_" + fieldname);
			if (el.length > 0) {
				$(el).val(fieldvalue);
			}
		}

		var services = {};
		var specs = {};
		var poc_name, cat_uid, service_uid, service_uids;
		var i, key;

		for (i = obj.Analyses.length - 1; i >= 0; i--) {
			var analysis = obj.Analyses[i];
			cat_uid = analysis.CategoryUID;
			service_uid = analysis.ServiceUID;
			key = analysis.PointOfCapture + "__" + analysis.CategoryUID;
			if (!(key in services)) {
				services[key] = [];
			}
			services[key].push(service_uid);
		}
		for (key in services) {
			if (!services.hasOwnProperty(key)) {
				continue;
			}
			poc_name = key.split("__")[0];
			cat_uid = key.split("__")[1];
			service_uids = services[key];
			window.toggleCat(poc_name, cat_uid, col, service_uids, true);
		}
		setTimeout(function(){ set_specs(col) }, 350)
	}

	function expand_default_categories() {
		$("th.prefill").click();
	}
}
