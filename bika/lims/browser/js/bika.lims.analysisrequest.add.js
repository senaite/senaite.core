/**
 * Controller class for AnalysisRequestAddView
 */
function AnalysisRequestAddView() {

	var that = this

	that.load = function () {

		$('input[type=text]').prop('autocomplete', 'off')

		state_init()
		configure_at_widgets()  // includes filter_all_by_client

		state_onchange_reference()
		state_onchange_selectwidget()
		state_onchange_textinput()

		copybutton_click()
		client_selected()
		contact_selected()
		samplepoint_selected()
		sampletype_selected()
		specification_selected()
		profile_selected()
		template_selected()
		sample_selected()

	}

	///////////////////////////
	// initialisation and utils
	///////////////////////////

	function state_init() {
		bika.lims.ar_add = {}
		bika.lims.ar_add.analysisrequests = {}
		for (var arnum = 0; arnum < $('input[id="ar_count"]').val(); arnum++) {
			bika.lims.ar_add.analysisrequests[arnum] = {}
		}
	}

	function state_set(arnum, fieldname, value) {
		// Use this function to set state.
		bika.lims.ar_add.analysisrequests[arnum][fieldname] = value
	}

	function configure_at_widgets() {
		// Multiple AT widgets may be rendered for each field.
		// rename them here, so their IDs and names do not conflict.
		var i, element, elements, arnum, name
		elements = $("td[ar_add_ar_widget]").find("input[type!='hidden']")
				.not("[disabled]")
		for (i = elements.length - 1; i >= 0; i--) {
			element = elements[i]
			$(element).attr("fieldname", element.id)
			arnum = $($(element).parents("td")).attr("arnum")
			name = $(element).attr("name")
			$(element).attr("name", "ar." + arnum + "." + name)
			$(element).attr("id", "ar_" + arnum + "_" + element.id)
			$(element).removeAttr("required")
		}
		elements = $("td[ar_add_ar_widget]").find("input[type='hidden']")
		for (i = elements.length - 1; i >= 0; i--) {
			element = elements[i]
			$(element).attr("fieldname", element.id)
			arnum = $($(element).parents("td")).attr("arnum")
			name = $(element).attr("name")
			$(element).attr("id", "ar_" + arnum + "_" + element.id)
			$(element).attr("name", "ar." + arnum + "." + name)
		}
		elements = $(".multiValued-listing")
		for (i = elements.length - 1; i >= 0; i--) {
			element = elements[i]
			$(element).attr("fieldname", element.id)
			var eid = element.id.split("-listing")[0]
			arnum = $($(element).parents("td")).attr("arnum")
			name = $(element).attr("name")
			// '.' format for both:
			$(element).attr("id", "ar." + arnum + "." + eid + "-listing")
			$(element).attr("name", "ar." + arnum + "." + eid + "-listing")
			$(element).attr("fieldName", "ar." + arnum + "." + eid)
		}
		elements = $("td[ar_add_ar_widget]").find("select")
		for (i = elements.length - 1; i >= 0; i--) {
			element = elements[i]
			$(element).attr("fieldname", element.id)
			arnum = $($(element).parents("td")).attr("arnum")
			name = $(element).attr("name")
			$(element).attr("id", "ar_" + arnum + "_" + element.id)
			$(element).attr("name", "ar." + arnum + "." + name)
		}
		/**
		 * Show only the data (contacts, templates, etc.) for the selected
		 * client.   This is the initial filter, but the filters are re-applied
		 * each time a Client field is modified.
		 */
		setTimeout(function () {
			var nr_ars = parseInt($("#ar_count").val(), 10)
			for (arnum = 0; arnum < nr_ars; arnum++) {
				filter_by_client(arnum)
			}
		}, 250)
	}

	function filter_combogrid(element, filterkey, filtervalue) {
		// If the element is not visible, do nothinge
		if (!$(element).is(':visible')) {
			return
		}

		var base_query = $.parseJSON($(element).attr("base_query"))
		base_query[filterkey] = encodeURIComponent(filtervalue)
		$(element).attr("base_query", $.toJSON(base_query))
		var options = $.parseJSON($(element).attr("combogrid_options"))
		options.url = window.location.href.split("/ar_add")[0] + "/" + options.url
		options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val()
		options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name")
		options.url = options.url + "&base_query=" + $.toJSON(base_query)
		options.url = options.url + "&search_query=" + $(element).attr("search_query")
		options.url = options.url + "&colModel=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).colModel)
		options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).search_fields)
		options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).discard_empty)
		options.force_all = "false"
		$(element).combogrid(options)
		$(element).addClass("has_combogrid_widget")
		$(element).attr("search_query", "{}")
	}

	function filter_by_client(arnum) {
		var element = $("#ar_" + arnum + "_Contact")
		var clientuid = $("#ar_" + arnum + "_Client_uid").val()
		filter_combogrid(element[0], "getParentUID", clientuid)
		element = $("#ar_" + arnum + "_CCContact")
		filter_combogrid(element[0], "getParentUID", clientuid)
		element = $("#ar_" + arnum + "_InvoiceContact")
		filter_combogrid(element[0], "getParentUID", clientuid)
		// Filter sample points by client
		element = $("#ar_" + arnum + "_SamplePoint")
		filter_combogrid(element[0], "getClientUID", [
			clientuid, $("#bika_setup").attr("bika_samplepoints_uid")])
		// Filter template by client
		element = $("#ar_" + arnum + "_Template")
		filter_combogrid(element[0], "getClientUID", [
			clientuid, $("#bika_setup").attr("bika_artemplates_uid")])
		// Filter Analysis Profile by client
		element = $("#ar_" + arnum + "_Profile")
		filter_combogrid(element[0], "getClientUID", [
			clientuid, $("#bika_setup").attr("bika_analysisprofiles_uid")])
		// Filter Analysis Spec by client
		element = $("#ar_" + arnum + "_Specification")
		filter_combogrid(element[0], "getClientUID", [
			clientuid, $("#bika_setup").attr("bika_analysisspecs_uid")])
	}

	function analysis_unset_all(arnum) {
		$.each($('td.ar\\.' + arnum).find("[type='checkbox']"),
			   function (i, element) {
				   if ($(this).prop("checked")) {
					   $(this).prop("checked", false);
					   $(element).next(".after").find(".partition").remove();
				   }
			   });
	}

	///////////////////////////
	// Event handlers
	///////////////////////////

	function state_onchange_reference() {
		// general handler and state change for all combogrids
		$.each($('.referencewidget'), function (i, element) {
			$(element).live('selected', function () {
				var arnum = $(this).parents('td').attr('arnum')
				var fieldname = $(this).attr('fieldname')
				if (!fieldname) fieldname = this.id
				var td = $(this).parents('td')
				var id = 'ar_' + arnum + '_' + fieldname;
				var value = $(td).find('input[id="' + id + '"]').val()
				var uid = $(td).find('[id*="' + id + '_uid"]').val()
				state_set(arnum, fieldname, value)
				state_set(arnum, fieldname + "_uid", uid)
			})
		})
	}

	function state_onchange_selectwidget() {
		// general handler and state change for all <select> widgets
		$.each($('select'), function (i, element) {
			$(element).live('change', function () {
				var arnum = $(this).parents('td').attr('arnum')
				var fieldname = $(this).attr('fieldname')
				if (!fieldname) fieldname = this.id
				var td = $(this).parents('td')
				var instr = '#ar_' + arnum + '_' + fieldname;
				var value = $(td).find(instr).val()
				state_set(arnum, fieldname, value)
			})
		})
	}

	function state_onchange_textinput() {
		// general handler and state change for text <inputs>
		$.each($('input[type="text"]'), function (i, element) {
			$(element).live('change', function () {
				var td = $(this).parents('td')
				var arnum = $(this).parents('td').attr('arnum')
				var fieldname = $(this).attr('fieldname')
				if (!fieldname) fieldname = this.id
				var instr = 'input[id="ar_' + arnum + '_' + fieldname + '"]';
				var value = $(td).find(instr).val()
				state_set(arnum, fieldname, value)
			})
		})
	}

	function state_onchange_checkbox() {
		// general handler and state change for checkboxes.
		// This does not include service selector checkboxes.
		$.each($('[ar_add_ar_widget] input[type="checkbox"]'),
			   function (i, element) {
				   $(element).live('change', function () {
					   var td = $(this).parents('td')
					   var arnum = $(this).parents('td').attr('arnum')
					   var fieldname = $(this).attr('fieldname')
					   if (!fieldname) fieldname = this.id
					   var instr = 'input[id="ar_' + arnum + '_' + fieldname + '"]';
					   var value = $(td).find(instr).val()
					   state_set(arnum, fieldname, value)
				   })
			   })
	}

	function client_selected() {
		// A client was selected
		$("[id*='_Client']").live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			filter_by_client(arnum)
		})
	}

	function cc_contacts_set(arnum) {
		// Update the multiselect CCContacts referencewidget,
		// to match Contact->CCContacts value.
		var contact_uid = $("#ar_" + arnum + "_Contact_uid").val()
		var fieldName = "ar." + arnum + ".CCContact"
		// clear the CC widget
		$("input[name*='" + fieldName + "']").val('').attr('uid', '')
		$('input[name="' + fieldName + '_uid"]').val('')
		$("#ar_" + arnum + "_CCContact-listing").empty()
		if (contact_uid !== "") {
			var request_data = {portal_type: "Contact", UID: contact_uid}
			window.bika.lims.jsonapi_read(request_data, function (data) {
				if (data.objects && data.objects.length < 1) return
				var ob = data.objects[0]
				var cc_titles = ob['CCContact']
				var cc_uids = ob['CCContact_uid']
				if (!cc_uids) return
				$("input[name='" + fieldName + "_uid']").val(cc_uids.join(","))
				for (var i = 0; i < cc_uids.length; i++) {
					var title = cc_titles[i]
					var uid = cc_uids[i]
					var del_btn_src = window.portal_url + "/++resource++bika.lims.images/delete.png"
					var del_btn = "<img class='deletebtn' src='" + del_btn_src + "' fieldName='" + fieldName + "' uid='" + uid + "'/>"
					var new_item = "<div class='reference_multi_item' uid='" + uid + "'>" + del_btn + title + "</div>"
					$("#ar\\." + arnum + "\\.CCContact-listing").append($(new_item))
				}
				// This is done for us normally:
				state_set(arnum, 'CCContact_uid', cc_uids.join(","))
				state_set(arnum, 'CCContact', cc_titles.join(","))
			})
		}
	}

	function contact_selected() {
		// selected a Contact
		$('[id*="_Contact"]').live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			cc_contacts_set(arnum)
		})
	}

	function copyButton() {
		// Anything that can be copied from columnn1 across all columns
		var fieldName = $(this).attr("name")
		var ar_count = parseInt($("#ar_count").val(), 10)
		// Checkbox
		if ($("input[name^='ar\\.0\\." + fieldName + "']").attr("type") == "checkbox") {
			var first_val = $("input[name^='ar\\.0\\." + fieldName + "']").prop("checked")
			var ar_count = parseInt($("#ar_count").val(), 10)
			// arnum starts at 1 here; we don't copy into the the first row
			for (var arnum = 1; arnum < ar_count; arnum++) {
				var other_elem = $("#ar_" + arnum + "_" + fieldName)
				if ((other_elem.prop("checked") != first_val)) {
					other_elem.prop("checked", first_val ? true : false)
					other_elem.trigger("change")
				}
			}
			$("[id*='_" + fieldName + "']").change()
		}
		// Anything else
		else {
			var first_val = $("input[name^='ar\\.0\\." + fieldName + "']").filter("[type=text]").val()
			// Reference fields have a hidden *_uid field
			var first_uid = $("input[name^='ar\\.0\\." + fieldName + "_uid']").val()
			// multi-valued fields: selection is in {fieldname}-listing
			var first_multi_html = $("div[name^='ar\\.0\\." + fieldName + "-listing']").html()
			// arnum starts at 1 here; we don't copy into the the first row
			for (var arnum = 1; arnum < ar_count; arnum++) {
				var other_uid_elem = $("#ar_" + arnum + "_" + fieldName + "_uid")
				if (first_uid !== undefined && first_uid !== null) {
					other_uid_elem.val(first_uid)
				}
				var other_multi_div = $("div[name^='ar\\." + arnum + "\\." + fieldName + "-listing']")
				if (first_multi_html !== undefined && first_multi_html !== null) {
					other_multi_div.html(first_multi_html.replace(".0.",
																  "." + arnum + "."))
				}
				// Actual field value
				var other_elem = $("#ar_" + arnum + "_" + fieldName)
				if (!(other_elem.prop("disabled"))) {
					$(other_elem).attr("skip_referencewidget_lookup", true)
					other_elem.val(first_val)
					other_elem.trigger("change")

					if (fieldName == "Contact") {
						cc_contacts_set(arnum)
					}

					if (fieldName == "Profile") {
						template_unset(arnum)
						profile_set(arnum, first_val)
						calculate_parts(arnum)
					}

					if (fieldName == "Template") {
						template_set(arnum, first_val)
					}

					if (fieldName == "SampleType") {
						template_unset(arnum)
						calculate_parts(arnum)
						specification_set(col)
					}

					if (fieldName == "Specification") {
						specification_set()
					}

				}
			}
		}
	}

	function copybutton_click() {
		// Anything that can be copied from columnn1 across all columns
		$(".copyButton").live("click", copyButton)
	}

	function specification_set_from_sampletype(arnum) {
		// When setting SampleType, we may automatically set the Specification.
		st_uid = $("#ar_" + arnum + "_SampleType_uid").val();
		st_title = $("#ar_" + arnum + "_SampleType").val();
		if (!st_uid) {
			return;
		}
		spec_element = $("#ar_" + arnum + "_Specification");
		spec_uid_element = $("#ar_" + arnum + "_Specification_uid");
		var request_data = {
			catalog_name: "bika_setup_catalog",
			portal_type: "AnalysisSpec",
			getSampleTypeTitle: st_title,
			include_fields: ["Title", "UID"]
		};
		window.bika.lims.jsonapi_read(request_data, function (data) {
			if (data.objects.length > 0) {
				var spec = data.objects[0];
				// set spec values for this arnum
				$(spec_element).val(spec.Title);
				$(spec_uid_element).val(spec.UID);
				specification_set(arnum);
			}
		});
	}

	function filter_spec_by_sampletype(arnum) {
		// when a SampleType is selected I will allow only specs to be selected
		// which 1- (have the same Sample Types)
		// 2- (have no sample type at all)
		var sampletype_title = $("#ar_" + arnum + "_SampleType").val();
		var e = $("#ar_" + arnum + "_Specification");
		var query_str = $(e).attr("search_query");
		var query_obj = $.parseJSON(query_str);
		if (query_obj.hasOwnProperty("getSampleTypeTitle")) {
			delete query_obj.getSampleTypeTitle;
		}
		query_obj.getSampleTypeTitle = [encodeURIComponent(sampletype_title),
										""];
		query_str = $.toJSON(query_obj);
		$(e).attr("search_query", query_str);
	}

	function specification_set(arnum) {
		// Get the spec for this ar, and check if the hidden #spec input must be updated.
		var spec_uid = $("#ar_" + arnum + "_Specification_uid").val();
		if (spec_uid == "" || spec_uid == undefined || spec_uid == null) {
			return;
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
				form_rr[arnum] = data.objects[0]['ResultsRange'];
				$(element).val($.toJSON(form_rr));

				/* Specs are taken from the Specification element values (#specs).
				 If a spec is defined in copy_to_new_specs, it is used instead, and the
				 values in #specs have no effect. */
				var copy_to_new_specs = $.parseJSON($("#copy_to_new_specs").val());
				var specs = $.parseJSON($("#specs").val());
				var rr = copy_to_new_specs[arnum];
				if (rr == undefined || rr.length < 1) {
					rr = specs[arnum];
				}
				// Set values for selected analyses
				if (rr != undefined && rr.length > 0) {
					for (var i = 0; i < rr.length; i++) {
						var this_min = "[name='ar." + arnum + ".min." + rr[i].uid + "']";
						var this_max = "[name='ar." + arnum + ".max." + rr[i].uid + "']";
						var this_error = "[name='ar." + arnum + ".error." + rr[i].uid + "']";
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
		});
	}

	function validate_spec_field_entry(element) {
		var arnum = $(element).attr("name").split(".")[1];
		var uid = $(element).attr("uid");
		$("[name^='ar\\." + arnum + "\\.Specification']").val("");
		$("[name^='ar\\." + arnum + "\\.Specification_uid']").val("");
		var min_element = $("[name='ar." + arnum + ".min." + uid + "']");
		var max_element = $("[name='ar." + arnum + ".max." + uid + "']");
		var error_element = $("[name='ar." + arnum + ".error." + uid + "']");
		var min = parseFloat($(min_element).val(), 10);
		var max = parseFloat($(max_element).val(), 10);
		var error = parseFloat($(error_element).val(), 10);
		if ($(element).hasClass("min")) {
			if (isNaN(min)) {
				$(min_element).val("");
			}
			else if ((!isNaN(max)) && min > max) {
				$(max_element).val("");
			}
		}
		else if ($(element).hasClass("max")) {
			if (isNaN(max)) {
				$(max_element).val("");
			}
			else if ((!isNaN(min)) && max < min) {
				$(min_element).val("");
			}
		}
		else if ($(element).hasClass("error")) {
			if (isNaN(error) || error < 0 || error > 100) {
				$(error_element).val("");
			}
		}
	}

	function specification_selected() {
		// Selected a Specification
		$("[id*='_Specification']").live('selected', function () {
			specification_set()
		})
	}

	function samplepoint_selected() {
		// selecting a Samplepoint - jiggle the SampleType element.
		$("[id*='_SamplePoint']").live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			var st_element = $("#ar_" + arnum + "_SampleType")
			st_element
					.removeClass("cg-autocomplete-input")
					.removeAttr("autocomplete")
					.removeAttr("role")
					.removeAttr("aria-autocomplete")
					.removeAttr("aria-haspopup")
			var new_st_element = $(st_element[0]).clone()
			var st_parent_node = $(st_element).parent()
			$(st_element).remove()
			$(st_parent_node).append(new_st_element)
			st_element = $("#ar_" + arnum + "_SampleType")
			// cut kwargs into the base_query
			//   var st_base_query = $(st_element).attr("base_query")
			//   st_base_query = $.parseJSON(st_base_query)
			//   st_base_query = $.toJSON(st_base_query)
			// 			var st_search_query = {"getRawSamplePoints": $(this).attr("uid")}
			st_search_query = $.toJSON(st_search_query)
			st_element.attr("search_query", st_search_query)
			ar_referencewidget_lookups(st_element)
		})
	}

	function sampletype_selected() {
		// selecting a Sampletype - Fix the SamplePoint filter:
		// 1. Can select SamplePoint which does not link to any SampleType
		// 2. Can select SamplePoint linked to This SampleType.
		// 3. Cannot select SamplePoint linked to other sample types (and not to this one)
		$("[id*='_SampleType']").live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			var sp_element = $("#ar_" + arnum + "_SamplePoint")
			filter_combogrid(sp_element, "getSampleTypeTitle", $(this).val())

			template_unset(arnum)
			specification_set_from_sampletype(arnum)
			filter_spec_by_sampletype(arnum)
			specification_set(arnum)
			calculate_parts(arnum)
		})
	}

	function profile_selected() {
		$("[id*='_Profile']").live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			template_unset(arnum)
			$.ajaxSetup({async: false})
			profile_set(arnum, $(this).val())
			$.ajaxSetup({async: true})
			specification_blank_inputs(arnum)
			specification_set()
			calculate_parts(arnum)
		})
	}

	function profile_unset(arnum) {
		if ($("#ar_" + arnum + "_Profile").val() !== "") {
			$("#ar_" + arnum + "_Profile").val("");
		}
	}


	function profile_set(arnum, profile_title) {
		window.bika.lims.jsonapi_read(
				{
					portal_type: "AnalysisProfile",
					title: profile_title
				},
				function (profile_data) {
					window.bika.lims.jsonapi_read(
							{
								portal_type: "AnalysisService",
								title: profile_data.objects[0].Service,
								include_fields: ["PointOfCapture", "Category",
												 "UID",
												 "Title", "Keyword", "Price",
												 "VAT"]
							},
							function (data) {
								analysis_unset_all(arnum);
								unset_ReportDryMatter(arnum)
								var service_objects = data.objects;

								// just a silly thing for lookups:
								// categorised_services : key is "pointofcapture_category"
								if (service_objects.length === 0) return;
								var categorised_services = {};
								for (var i in service_objects) {
									var key = service_objects[i].PointOfCapture + "__" +
											service_objects[i].Category;
									if (categorised_services[key] === undefined)
										categorised_services[key] = [];
									categorised_services[key].push(service_objects[i]);
								}

								for (var key in categorised_services) {
									var services = categorised_services[key];
									var poc = key.split("__")[0];
									var cat = key.split("__")[1];
									var th = $("th[cat='" + cat + "']")
									if ($(th).hasClass("collapsed"))
										$(th).click()
									for (i in services) {
										var service = services[i];
										var service_uid = services[i].UID;
										analysis_set(arnum, service_uid)
									}
									recalc_prices(arnum);
								}
								calculate_parts(arnum);
							});
				});
	}

	function profile_set_from_template(template) {
		var arnum = $(this).parents('td').attr('arnum')
		// lookup AnalysisProfile
		if (template['AnalysisProfile']) {
			var request_data = {
				portal_type: "AnalysisProfile",
				title: template['AnalysisProfile'],
				include_fields: ["UID"]
			};
			window.bika.lims.jsonapi_read(request_data, function (data) {
				$("#ar_" + arnum + "_Profile").val(template['AnalysisProfile']);
				$("#ar_" + arnum + "_Profile_uid").val(data['objects'][0]['UID']);
			});
		}
		else {
			$("#ar_" + arnum + "_Profile").val("");
			$("#ar_" + arnum + "_Profile_uid").val("");
		}

	}

	function analysis_set(arnum, service_uid) {
		var arnum = $(this).parents('td').attr('arnum')
		profile_unset(arnum);
		template_unset(arnum);

		// Unselecting Dry Matter Service unsets 'Report Dry Matter'
		if ($(this).val() == $("#getDryMatterService").val() && !$(this).prop("checked")) {
			$("#ar_" + arnum + "_ReportDryMatter").prop("checked", false);
		}

		// unselecting service: remove part number.
		if (!$(this).prop("checked")) {
			$(".partnr_" + this.id).filter("[arnum='" + arnum + "']").empty();
		}

		calcdependencies([$(this)]);
		var layout = $("input[id='layout']").val();
		if (layout == 'columns') {
			recalc_prices();
		}
		else {
			recalc_prices(arnum);
		}
		calculate_parts(arnum);
		toggle_spec_fields($(this));
	}

	function unset_ReportDryMatter(arnum) {
		$("#ar_" + arnum + "_ReportDryMatter").prop("checked", false);
	}

	function template_unset(arnum) {
		if ($("#ar_" + arnum + "_Template").val() !== "") {
			$("#ar_" + arnum + "_Template").val("");
		}
	}

	function template_set(arnum, template_title) {
		analysis_unset_all(arnum);
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
				"Analyses",
				"Prices",
			]
		};
		window.bika.lims.jsonapi_read(request_data, function (data) {
			var template = data.objects[0];
			var request_data, x, i;
			// set our template fields
			$("#ar_" + arnum + "_SampleType").val(template['SampleType']);
			$("#ar_" + arnum + "_SampleType_uid").val(template['SampleTypeUID']);
			$("#ar_" + arnum + "_SamplePoint").val(template['SamplePoint']);
			$("#ar_" + arnum + "_SamplePoint_uid").val(template['SamplePointUID']);
			$("#ar_" + arnum + "_reportdrymatter")
					.prop("checked", template['reportdrymatter']);
			specification_set_from_sampletype(arnum)
			profile_set_from_template(template)

			// scurrel the parts into hashes for easier lookup
			var parts_by_part_id = {};
			var parts_by_service_uid = {};
			for (x in template['Partitions']) {
				if (!template['Partitions'].hasOwnProperty(x)) {
					continue;
				}
				var P = template['Partitions'][x];
				P.part_nr = parseInt(P.part_id.split("-")[1], 10);
				P.services = [];
				parts_by_part_id[P.part_id] = P;
			}
			for (x in template['Analyses']) {
				if (!template['Analyses'].hasOwnProperty(x)) {
					continue;
				}
				i = template['Analyses'][x];
				parts_by_part_id[i.partition].services.push(i.service_uid);
				parts_by_service_uid[i.service_uid] = parts_by_part_id[i.partition];
			}
			// this one goes through with the form submit
			var parts = [];
			for (x in parts_by_part_id) {
				if (!parts_by_part_id.hasOwnProperty(x)) {
					continue;
				}
				parts.push(parts_by_part_id[x]);
			}
			var formparts = $.parseJSON($("#parts").val());
			formparts[arnum] = parts;
			$("#parts").val($.toJSON(formparts));

			// lookup the services specified in the template
			request_data = {
				portal_type: "AnalysisService",
				UID: [],
				include_fields: ["PointOfCapture", "CategoryUID", "UID",
								 "Title", "Keyword", "Price", 'VAT']
			};
			for (x in template['Analyses']) {
				if (!template['Analyses'].hasOwnProperty(x)) {
					continue;
				}
				request_data.UID.push(template['Analyses'][x]['service_uid']);
			}
			// save services in hash for easier lookup this
			window.bika.lims.jsonapi_read(request_data, function (data) {
				var e;
				var poc_cat_services = {};
				for (var x in data.objects) {
					if (!data.objects.hasOwnProperty(x)) {
						continue;
					}
					var service = data.objects[x];
					var poc_title = service.PointOfCapture;
					if (!(poc_title in poc_cat_services)) {
						poc_cat_services[poc_title] = {};
					}
					if (!(service.CategoryUID in poc_cat_services[poc_title])) {
						poc_cat_services[poc_title][service.CategoryUID] = [];
					}
					poc_cat_services[poc_title][service.CategoryUID].push([service.UID,
																		   service.Title,
																		   service.Keyword,
																		   service.Price,
																		   service.VAT]);
					// poc_cat_services[poc_title][service.CategoryUID].push(service.UID);
				}
				// expand categories, select, and enable controls for template services
				var analyses = $("#ar_" + arnum + "_Analyses");
				var total = 0.00;
				var spec_uid = $("#ar_" + arnum + "_Specification_uid").val();
				var an_parent = $(analyses).parent();
				var titles = [];
				for (var p in poc_cat_services) {
					if (!poc_cat_services.hasOwnProperty(p)) {
						continue;
					}
					var poc = poc_cat_services[p];
					for (var cat_uid in poc) {
						if (!poc.hasOwnProperty(cat_uid)) {
							continue;
						}
						var services = poc[cat_uid];
						var tbody = $("tbody[id='" + p + "_" + cat_uid + "']");
						var service;
						// expand category
						if (!($(tbody).hasClass("expanded"))) {
							$.ajaxSetup({async: false});
							toggleCat(p, cat_uid, arnum);
							$.ajaxSetup({async: true});
						}
						$(tbody).toggle(true);
						for (i = 0; i < services.length; i++) {
							service = services[i];
							// select checkboxes
							e = $("input[arnum='" + arnum + "']").filter("#" + service[0]);
							$(e).prop("checked", true);
						}
					}
					// set part number indicators
					for (i = 0; i < services.length; i++) {
						service = services[i];
						var partnr = parts_by_service_uid[service[0]].part_nr;
						e = $(".partnr_" + service[0]).filter("[arnum='" + arnum + "']");
						$(e).empty().append(partnr + 1);
					}
				}
			})
		})
		recalc_prices(arnum);
	}

	function template_selected() {
		$("[id*='_Template']").live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			template_set(arnum, $(this).val())
			specification_set(arnum)
		})
	}

	function sample_selected() {
		// Selected a sample to create a secondary AR.
		$("[id*='_Sample']").live('selected', function () {
			// var e = $("input[name^='ar\\."+arnum+"\\."+fieldName+"']")
			// var Sample = $("input[name^='ar\\."+arnum+"\\."+fieldName+"']").val()
			// var Sample_uid = $("input[name^='ar\\."+arnum+"\\."+fieldName+"_uid']").val()
			// Install the handler which will undo the changes I am about to make
			$(this).blur(function () {
				if ($(this).val() === "") {
					// clear and un-disable everything
					var disabled_elements = $("[ar_add_ar_widget] [id*='ar_" + arnum + "']:disabled")
					$.each(disabled_elements, function (x, disabled_element) {
						$(disabled_element).prop("disabled", false)
						if ($(disabled_element).attr("type") == "checkbox")
							$(disabled_element).prop("checked", false)
						else
							$(disabled_element).val("")
					})
				}
			})
			// Then populate and disable sample fields
			$.getJSON(window.location.href.replace("/ar_add",
												   "") + "/secondary_ar_sample_info",
					  {
						  "Sample_uid": $(this).attr("uid"),
						  "_authenticator": $("input[name='_authenticator']").val()
					  },
					  function (data) {
						  for (var x = data.length - 1; x >= 0; x--) {
							  var fieldname = data[x][0]
							  var fieldvalue = data[x][1]
							  var uid_element = $("#ar_" + arnum + "_" + fieldname + "_uid")
							  $(uid_element).val("")
							  var sample_element = $("#ar_" + arnum + "_" + fieldname)
							  $(sample_element).val("").prop("disabled", true)
							  if ($(sample_element).attr("type") == "checkbox" && fieldvalue) {
								  $(sample_element).prop("checked", true)
							  }
							  else {
								  $(sample_element).val(fieldvalue)
							  }
						  }
					  }
			)
		})
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
			if (!obj.hasOwnProperty(fieldname)) {
				continue;
			}
			if (skip_fields.indexOf(fieldname) > -1) {
				continue;
			}
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
	}

	function service_checkbox_change() {
		/*jshint validthis:true */
		var arnum = $(this).attr("arnum");
		var element = $(this);
		profile_unset(arnum);
		template_unset(arnum);

		// Unselecting Dry Matter Service unsets 'Report Dry Matter'
		if ($(this).val() == $("#getDryMatterService").val() && !$(this).prop("checked")) {
			$("#ar_" + arnum + "_ReportDryMatter").prop("checked", false);
		}

		// unselecting service: remove part number.
		if (!$(this).prop("checked")) {
			$(".partnr_" + this.id).filter("[arnum='" + arnum + "']").empty();
		}

		calcdependencies([element]);
		recalc_prices();
		calculate_parts(arnum);
	}


	function add_Yes(dlg, element, dep_services) {
		for (var i = 0; i < dep_services.length; i++) {
			var service_uid = dep_services[i].Service_uid;
			if (!$("#list_cb_" + service_uid).prop("checked")) {
				check_service(service_uid);
				$("#list_cb_" + service_uid).prop("checked", true);
			}
		}
		$(dlg).dialog("close");
		$("#messagebox").remove();
	}

	function add_No(dlg, element) {
		if ($(element).prop("checked")) {
			uncheck_service($(element).attr("value"));
			$(element).prop("checked", false);
		}
		$(dlg).dialog("close");
		$("#messagebox").remove();
	}

	function calcdependencies(elements, auto_yes) {
		auto_yes = auto_yes || false;
		jarn.i18n.loadCatalog('bika');
		var _ = window.jarn.i18n.MessageFactory("bika");

		var dep;
		var i, cb;

		var lims = window.bika.lims;

		for (var elements_i = 0; elements_i < elements.length; elements_i++) {
			var dep_services = [];  // actionable services
			var dep_titles = [];
			var element = elements[elements_i];
			var service_uid = $(element).attr("value");
			// selecting a service; discover dependencies
			if ($(element).prop("checked")) {
				var Dependencies = lims.AnalysisService.Dependencies(service_uid);
				for (i = 0; i < Dependencies.length; i++) {
					dep = Dependencies[i];
					if ($("#list_cb_" + dep.Service_uid).prop("checked")) {
						continue; // skip if checked already
					}
					dep_services.push(dep);
					dep_titles.push(dep.Service);
				}
				if (dep_services.length > 0) {
					if (auto_yes) {
						add_Yes(this, element, dep_services);
					}
					else {
						var html = "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>";
						html = html + _(
								"<p>${service} requires the following services to be selected:</p>" +
								"<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
								{
									service: $(element).attr("title"),
									deps: dep_titles.join("<br/>")
								});
						html = html + "</div>";
						$("body").append(html);
						$("#messagebox").dialog(
								{
									width: 450,
									resizable: false,
									closeOnEscape: false,
									buttons: {
										yes: function () {
											add_Yes(this,
													element,
													dep_services);
										},
										no: function () {
											add_No(this,
												   element);
										}
									}
								});
					}
				}
			}
			// unselecting a service; discover back dependencies
			else {
				var Dependants = lims.AnalysisService.Dependants(service_uid);
				for (i = 0; i < Dependants.length; i++) {
					dep = Dependants[i];
					cb = $("#list_cb_" + dep.Service_uid);
					if (cb.prop("checked")) {
						dep_titles.push(dep.Service);
						dep_services.push(dep);
					}
				}
				if (dep_services.length > 0) {
					if (auto_yes) {
						for (i = 0; i < dep_services.length; i += 1) {
							dep = dep_services[i];
							service_uid = dep.Service_uid;
							cb = $("#list_cb_" + dep.Service_uid);
							uncheck_service(dep.Service_uid);
							$(cb).prop("checked", false);
						}
					}
					else {
						$("body").append(
								"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>" +
								_("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
								  {
									  service: $(element).attr("title"),
									  deps: dep_titles.join("<br/>")
								  }) + "</div>");
						$("#messagebox").dialog(
								{

									width: 450,
									resizable: false,
									closeOnEscape: false,
									buttons: {
										yes: function () {
											for (i = 0; i < dep_services.length; i += 1) {
												dep = dep_services[i];
												service_uid = dep.Service_uid;
												cb = $("#list_cb_" + dep.Service_uid);
												$(cb).prop("checked",
														   false);
												uncheck_service(dep.Service_uid);
											}
											$(this).dialog("close");
											$("#messagebox").remove();
										},
										no: function () {
											service_uid = $(element).attr("value");
											check_service(service_uid);
											$(element).prop("checked",
															true);
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
}

