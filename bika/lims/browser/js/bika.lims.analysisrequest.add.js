/**
 * Controller class for AnalysisRequestAddView
 */
function AnalysisRequestAddView() {

	var that = this

	that.load = function () {

		$('input[type=text]').prop('autocomplete', 'off')

		state_init()
		configure_at_widgets()

		state_onchange_reference()
		state_onchange_selectwidget()
		state_onchange_textinput()
		state_onchange_checkbox()

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

	// initialisation and utils  ///////////////////////////////////////////////

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
		base_query[filterkey] = filtervalue
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
		var bs = $("#bika_setup")
		var clientuid = $("#ar_" + arnum + "_Client_uid").val()
		filter_combogrid(
			$("#ar_" + arnum + "_Contact")[0],
			"getParentUID", clientuid)
		filter_combogrid(
			$("#ar_" + arnum + "_CCContact")[0],
			"getParentUID", clientuid)
		filter_combogrid(
			$("#ar_" + arnum + "_InvoiceContact")[0],
			"getParentUID", clientuid)
		filter_combogrid(
			$("#ar_" + arnum + "_SamplePoint")[0],
			"getClientUID",
			[clientuid, $(bs).attr("bika_samplepoints_uid")])
		filter_combogrid(
			$("#ar_" + arnum + "_Template")[0],
			"getClientUID",
			[clientuid, $(bs).attr("bika_artemplates_uid")])
		filter_combogrid(
			$("#ar_" + arnum + "_Profile")[0], "getClientUID",
			[clientuid, $(bs).attr("bika_analysisprofiles_uid")])
		filter_combogrid(
			$("#ar_" + arnum + "_Specification")[0],
			"getClientUID",
			[clientuid, $(bs).attr("bika_analysisspecs_uid")])
	}

	function analysis_unset_all(arnum) {
		var analyses = $('td.ar\\.' + arnum).find("[type='checkbox']")
		for (var i = 0; i < analyses.length; i++) {
			$(analyses[i]).prop("checked", false)
			$(analyses[i]).next(".after").empty()
		}
	}

	// Event handlers //////////////////////////////////////////////////////////

	function state_onchange_checkbox() {
		// general handler and state change for checkboxes.
		// (excluding service selector checkboxes).
		var e = $('[ar_add_ar_widget] input[type="checkbox"]')
		$(e).live('change', function () {
			var td = $(this).parents('td')
			var arnum = $(this).parents('td').attr('arnum')
			var fieldname = $(this).attr('fieldname')
			var instr = 'input[id="ar_' + arnum + '_' + fieldname + '"]'
			var value = $(td).find(instr).val()
			state_set(arnum, fieldname, value)
		})
	}

	function state_onchange_reference() {
		// general handler and state change for all combogrids
		$('.referencewidget').live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			var fieldname = $(this).attr('fieldname')
			if (!fieldname) fieldname = this.id
			var td = $(this).parents('td')
			var id = 'ar_' + arnum + '_' + fieldname
			var value = $(td).find('input[id="' + id + '"]').val()
			var uid = $(td).find('[id*="' + id + '_uid"]').val()
			state_set(arnum, fieldname, value)
			state_set(arnum, fieldname + "_uid", uid)
		})
	}

	function state_onchange_selectwidget() {
		// general handler and state change for all <select> widgets
		$('select').live('change', function () {
			var arnum = $(this).parents('td').attr('arnum')
			var fieldname = $(this).attr('fieldname')
			if (!fieldname) fieldname = this.id
			var td = $(this).parents('td')
			var instr = '#ar_' + arnum + '_' + fieldname
			var value = $(td).find(instr).val()
			state_set(arnum, fieldname, value)
		})
	}

	function state_onchange_textinput() {
		// general handler and state change for text <inputs>
		$('input[type="text"]').live('change', function () {
			var td = $(this).parents('td')
			var arnum = $(this).parents('td').attr('arnum')
			var fieldname = $(this).attr('fieldname')
			if (!fieldname) fieldname = this.id
			var instr = 'input[id="ar_' + arnum + '_' + fieldname + '"]'
			var value = $(td).find(instr).val()
			state_set(arnum, fieldname, value)
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

	function copybutton_click() {
		// Anything that can be copied from columnn1 across all columns
		$(".copyButton").live("click", copyButton)
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
						$("#ar_" + arnum + "_Template").val("")
						profile_set(arnum, first_val)
							.then(calculate_parts(arnum))
					}

					if (fieldName == "Template") {
						template_set(arnum, first_val)
							.then(partition_indicators_set(arnum, false))
					}

					if (fieldName == "SampleType") {
						$("#ar_" + arnum + "_Template").val("")
						partition_indicators_set(arnum)
						specification_set(arnum)
					}

					if (fieldName == "Specification") {
						specification_set()
					}

				}
			}
		}
	}

	function filter_spec_by_sampletype(arnum) {
		// when a SampleType is selected I will allow only specs to be selected
		// which 1- (have the same Sample Types)
		// 2- (have no sample type at all)
		var sampletype_title = $("#ar_" + arnum + "_SampleType").val()
		var e = $("#ar_" + arnum + "_Specification")
		var query_str = $(e).attr("search_query")
		var query_obj = $.parseJSON(query_str)
		if (query_obj.hasOwnProperty("getSampleTypeTitle")) {
			delete query_obj.getSampleTypeTitle
		}
		query_obj.getSampleTypeTitle = [encodeURIComponent(sampletype_title),
										""]
		query_str = $.toJSON(query_obj)
		$(e).attr("search_query", query_str)
	}

	function specification_set(arnum) {
		var d = $.Deferred()
		// Get the spec for this ar, and check if the hidden #spec input must be updated.
		var spec_uid = $("#ar_" + arnum + "_Specification_uid").val()
		if (!spec_uid) {
			d.resolve()
			return d.promise()
		}
		var request_data = {
			catalog_name: 'bika_setup_catalog',
			UID: spec_uid
		}
		window.bika.lims.jsonapi_read(request_data, function (data) {
			if (data.success && data.objects.length > 0) {
				// Update the #specs value.
				var element = $("#specs")
				var form_rr = $.parseJSON($(element).val())
				form_rr[arnum] = data.objects[0]['ResultsRange']
				$(element).val($.toJSON(form_rr))

				/* Specs are taken from the Specification element values (#specs).
				 If a spec is defined in copy_to_new_specs, it is used instead, and the
				 values in #specs have no effect. */
				var copy_to_new_specs = $.parseJSON($("#copy_to_new_specs").val())
				var specs = $.parseJSON($("#specs").val())
				var rr = copy_to_new_specs[arnum]
				if (rr == undefined || rr.length < 1) {
					rr = specs[arnum]
				}
				// Set values for selected analyses
				if (rr != undefined && rr.length > 0) {
					debugger;
					for (var i = 0; i < rr.length; i++) {
						var this_min = "[name='ar." + arnum + ".min." + rr[i].uid + "']"
						var this_max = "[name='ar." + arnum + ".max." + rr[i].uid + "']"
						var this_error = "[name='ar." + arnum + ".error." + rr[i].uid + "']"
						if ($(this_min).length > 0) {
							if ($(this_min).val() == "") {
								$(this_min).val(rr[i].min)
							}
							if ($(this_max).val() == "") {
								$(this_max).val(rr[i].max)
							}
							if ($(this_error).val() == "") {
								$(this_error).val(rr[i].error)
							}
						}
					}
				}
			}
			d.resolve()
		})
		return d.promise()
	}

	function specification_set_from_sampletype(arnum) {
		// When setting SampleType, we may automatically set the Specification.
		var st_uid = $("#ar_" + arnum + "_SampleType_uid").val()
		var st_title = $("#ar_" + arnum + "_SampleType").val()
		if (!st_uid) {
			return
		}
		filter_spec_by_sampletype(arnum)
		var spec_element = $("#ar_" + arnum + "_Specification")
		var spec_uid_element = $("#ar_" + arnum + "_Specification_uid")
		var request_data = {
			catalog_name: "bika_setup_catalog",
			portal_type: "AnalysisSpec",
			getSampleTypeTitle: st_title,
			include_fields: ["Title", "UID"]
		}
		window.bika.lims.jsonapi_read(request_data, function (data) {
			if (data.objects.length > 0) {
				var spec = data.objects[0]
				// set spec values for this arnum
				$(spec_element).val(spec['Title'])
				$(spec_uid_element).val(spec['UID'])
				state_set(arnum, 'Specification', spec['Title'])
				state_set(arnum, 'Specification_uid', spec['UID'])
				specification_set(arnum)
				partition_indicators_set(arnum)
			}
		})
	}

	function validate_spec_field_entry(element) {
		var arnum = $(element).attr("name").split(".")[1]
		var uid = $(element).attr("uid")
		$("[name^='ar\\." + arnum + "\\.Specification']").val("")
		$("[name^='ar\\." + arnum + "\\.Specification_uid']").val("")
		var min_element = $("[name='ar." + arnum + ".min." + uid + "']")
		var max_element = $("[name='ar." + arnum + ".max." + uid + "']")
		var error_element = $("[name='ar." + arnum + ".error." + uid + "']")
		var min = parseFloat($(min_element).val(), 10)
		var max = parseFloat($(max_element).val(), 10)
		var error = parseFloat($(error_element).val(), 10)
		if ($(element).hasClass("min")) {
			if (isNaN(min)) {
				$(min_element).val("")
			}
			else if ((!isNaN(max)) && min > max) {
				$(max_element).val("")
			}
		}
		else if ($(element).hasClass("max")) {
			if (isNaN(max)) {
				$(max_element).val("")
			}
			else if ((!isNaN(min)) && max < min) {
				$(min_element).val("")
			}
		}
		else if ($(element).hasClass("error")) {
			if (isNaN(error) || error < 0 || error > 100) {
				$(error_element).val("")
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

	function sampletype_set(arnum) {
		var arnum = $(this).parents('td').attr('arnum')
		var sp_element = $("#ar_" + arnum + "_SamplePoint")
		filter_combogrid(sp_element, "getSampleTypeTitle", $(this).val())
		// $("#ar_" + arnum + "_Template").val("")
		specification_set_from_sampletype(arnum)
		partition_indicators_set(arnum)
	}

	function sampletype_selected() {
		$("[id*='_SampleType']").live('selected', sampletype_set)
	}

	function profile_selected() {
		$("[id*='_Profile']").live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			profile_set(arnum, $(this).val())
				.done(partition_indicators_set(arnum))
		})
	}

	function profile_set(arnum, profile_title) {
		var d = $.Deferred()
		$("#ar_" + arnum + "_Template").val("")
		var request_data = {
			portal_type: "AnalysisProfile",
			title: profile_title
		}
		bika.lims.jsonapi_read(request_data, function (data) {
			var profile = data['objects'][0]
			analysis_unset_all(arnum)
			ReportDryMatter_unset(arnum)
			var service_uids = []
			for (var i = 0; i < profile['service_data'].length; i++) {
				var service = profile['service_data'][i]
				service_uids.push(service['UID'])
				var poc = service['PointOfCapture']
				$('#services_' + poc + ' [cat="' + service['CategoryTitle'] + '"].collapsed').click()
				$('#' + service['UID'] + '-ar\\.' + arnum).attr("checked", true)
			}
			state_set(arnum, 'Analyses', service_uids)
			d.resolve()
		})
		return d.promise()
	}

	function ReportDryMatter_unset(arnum) {
		$("#ar_" + arnum + "_ReportDryMatter").prop("checked", false)
	}

	function template_set(arnum, template_title) {
		var d = $.Deferred()
		analysis_unset_all(arnum)
		var request_data = {
			portal_type: "ARTemplate",
			title: template_title,
			include_fields: [
				"SampleType", "SampleTypeUID", "SamplePoint", "SamplePointUID",
				"ReportDryMatter", "AnalysisProfile", "Partitions", "Analyses",
				"Prices"]
		}
		window.bika.lims.jsonapi_read(request_data, function (data) {
			var template = data.objects[0]
			var request_data, x, i

			// set our template fields
			$("#ar_" + arnum + "_SampleType").val(template['SampleType'])
			$("#ar_" + arnum + "_SampleType_uid").val(template['SampleTypeUID'])
			state_set(arnum, 'SampleType', template['SampleType'])
			state_set(arnum, 'SampleType_uid', template['SampleTypeUID'])
			$("#ar_" + arnum + "_SamplePoint").val(template['SamplePoint'])
			$("#ar_" + arnum + "_SamplePoint_uid").val(template['SamplePointUID'])
			state_set(arnum, 'SamplePoint', template['SamplePoint'])
			state_set(arnum, 'SamplePoint_uid', template['SamplePointUID'])
			$("#ar_" + arnum + "_reportdrymatter")
				.prop("checked", template['reportdrymatter'])
			specification_set_from_sampletype(arnum)

			// Set the ARTemplate's AnalysisProfile
			if (template['AnalysisProfile']) {
				$("#ar_" + arnum + "_Profile").val(template['AnalysisProfile'])
				$("#ar_" + arnum + "_Profile_uid").val(template['AnalysisProfile_uid'])
				state_set(arnum, 'Profile', template['AnalysisProfile'])
				state_set(arnum, 'Profile_uid', template['AnalysisProfile_uid'])
			}
			else {
				$("#ar_" + arnum + "_Profile").val("")
				$("#ar_" + arnum + "_Profile_uid").val("")
				state_set(arnum, 'Profile', "")
				state_set(arnum, 'Profile_uid', "")
			}

			// save parts (with service UIDS as values) for easier lookup
			var parts_by_part_id = {}
			var parts_by_service_uid = {}
			for (x in template['Partitions']) {
				var P = template['Partitions'][x]
				P['part_nr'] = parseInt(P['part_id'].split("-")[1], 10)
				P['services'] = []
				parts_by_part_id[P['part_id']] = P
			}
			for (x in template['Analyses']) {
				i = template['Analyses'][x]
				parts_by_part_id[i['partition']].services.push(i.service_uid)
				parts_by_service_uid[i['service_uid']] = parts_by_part_id[i.partition]
			}

			// compose 'parts' data for the form state.
			var parts = []
			for (x in parts_by_part_id) {
				if (!parts_by_part_id.hasOwnProperty(x)) continue
				parts.push(parts_by_part_id[x])
			}
			state_set(arnum, 'parts', parts)

			var service_uids = []
			for (si = 0; si < template['service_data'].length; si++) {
				var service = template['service_data'][si]
				service_uids.push(service['UID'])
				var poc = service['PointOfCapture']
				$('#services_' + poc + ' [cat="' + service['CategoryTitle'] + '"].collapsed').click()
				$('#' + service['UID'] + '-ar\\.' + arnum).attr("checked", true)
			}
			state_set(arnum, 'Analyses', service_uids)
			partition_indicators_set(arnum, false)
			// prices_update(arnum)
			d.resolve()
		})
		return d.promise()
	}

	function template_selected() {
		$("[id*='_Template']").live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
			template_set(arnum, $(this).val()).then(specification_set(arnum))
		})
	}

	function partition_indicators_calculate(arnum) {
		var d = $.Deferred()
		// Configures the state partition data
		var state = bika.lims.ar_add.analysisrequests[arnum]

		// Template columns are not calculated - they are set manually.
		if ($("#ar_" + arnum + "_Template").val() !== "") {
			d.resolve()
			return d.promise()
		}

		var st_uid = state['SampleType_uid']
		var service_uids = state['Analyses']
		// if no sampletype or no selected analyses:  remove partition markers
		if (!st_uid || !service_uids) {
			d.resolve()
			return d.promise()
		}
		var request_data = {
			services: service_uids.join(","),
			sampletype: st_uid,
			_authenticator: $("input[name='_authenticator']").val()
		}
		window.jsonapi_cache = window.jsonapi_cache || {}
		var cacheKey = $.param(request_data)
		if (typeof window.jsonapi_cache[cacheKey] === "undefined") {
			$.ajax({
					   type: "POST",
					   dataType: "json",
					   url: window.portal_url + "/@@API/calculate_partitions",
					   data: request_data,
					   success: function (data) {
						   // Check if calculation succeeded
						   if (data.success == false) {
							   bika.lims.log('Error while calculating partitions: ' + data.message)
						   }
						   else {
							   window.jsonapi_cache[cacheKey] = data
							   state['parts'] = data['parts']
						   }
						   d.resolve()
					   }
				   })
		}
		else {
			var data = window.jsonapi_cache[cacheKey]
			state['parts'] = data['parts']
			d.resolve()
		}
		return d.promise()
	}

	function partition_indicators_set(arnum, calculate) {
		// set calculate=false to prevent calculateion (eg, setting template)
		$('[id*="-ar.' + arnum + '"]').filter("[type='checkbox']").next(".after").empty()
		if (calculate == undefined) partition_indicators_calculate(arnum)
			.done(function () {
					  var parts = bika.lims.ar_add.analysisrequests[arnum]['parts']
					  if (!parts) return
					  for (var pi = 0; pi < parts.length; pi++) {
						  part_nr = pi + 1;
						  var part = parts[pi];
						  var services = part['services']
						  for (var si = 0; si < services.length; si++) {
							  var service_uid = services[si];
							  $('#' + service_uid + '-ar\\.' + arnum).next(".after").empty().append(part_nr)
						  }
					  }
				  })
	}

	function sample_selected() {
		var arnum = $(this).parents('td').attr('arnum')
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

	function service_checkbox_change() {
		/*jshint validthis:true */
		var arnum = $(this).attr("arnum")
		$("#ar_" + arnum + "_Profile").val("")
		$("#ar_" + arnum + "_Template").val("")

		// Unselecting Dry Matter Service unsets 'Report Dry Matter'
		if ($(this).val() == $("#getDryMatterService").val() && !$(this).prop("checked")) {
			$("#ar_" + arnum + "_ReportDryMatter").prop("checked", false)
		}

		// unselecting service: remove part number.
		if (!$(this).prop("checked")) {
			$(this).next(".after").empty()
		}

		calcdependencies([this])
		recalc_prices()
		calculate_parts(arnum)
	}

	function add_Yes(dlg, element, dep_services) {
		for (var i = 0; i < dep_services.length; i++) {
			var service_uid = dep_services[i].Service_uid
			if (!$("#list_cb_" + service_uid).prop("checked")) {
				check_service(service_uid)
				$("#list_cb_" + service_uid).prop("checked", true)
			}
		}
		$(dlg).dialog("close")
		$("#messagebox").remove()
	}

	function add_No(dlg, element) {
		if ($(element).prop("checked")) {
			uncheck_service($(element).attr("value"))
			$(element).prop("checked", false)
		}
		$(dlg).dialog("close")
		$("#messagebox").remove()
	}

	function calcdependencies(elements, auto_yes) {
		auto_yes = auto_yes || false
		jarn.i18n.loadCatalog('bika')
		var _ = window.jarn.i18n.MessageFactory("bika")

		var dep
		var i, cb

		var lims = window.bika.lims

		for (var elements_i = 0; elements_i < elements.length; elements_i++) {
			var dep_services = [];  // actionable services
			var dep_titles = []
			var element = elements[elements_i]
			var service_uid = $(element).attr("value")
			// selecting a service; discover dependencies
			if ($(element).prop("checked")) {
				var Dependencies = lims.AnalysisService.Dependencies(service_uid)
				for (i = 0; i < Dependencies.length; i++) {
					dep = Dependencies[i]
					if ($("#list_cb_" + dep.Service_uid).prop("checked")) {
						continue; // skip if checked already
					}
					dep_services.push(dep)
					dep_titles.push(dep.Service)
				}
				if (dep_services.length > 0) {
					if (auto_yes) {
						add_Yes(this, element, dep_services)
					}
					else {
						var html = "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"
						html = html + _(
								"<p>${service} requires the following services to be selected:</p>" +
								"<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
								{
									service: $(element).attr("title"),
									deps: dep_titles.join("<br/>")
								})
						html = html + "</div>"
						$("body").append(html)
						$("#messagebox").dialog(
							{
								width: 450,
								resizable: false,
								closeOnEscape: false,
								buttons: {
									yes: function () {
										add_Yes(this,
												element,
												dep_services)
									},
									no: function () {
										add_No(this,
											   element)
									}
								}
							})
					}
				}
			}
			// unselecting a service; discover back dependencies
			else {
				var Dependants = lims.AnalysisService.Dependants(service_uid)
				for (i = 0; i < Dependants.length; i++) {
					dep = Dependants[i]
					cb = $("#list_cb_" + dep.Service_uid)
					if (cb.prop("checked")) {
						dep_titles.push(dep.Service)
						dep_services.push(dep)
					}
				}
				if (dep_services.length > 0) {
					if (auto_yes) {
						for (i = 0; i < dep_services.length; i += 1) {
							dep = dep_services[i]
							service_uid = dep.Service_uid
							cb = $("#list_cb_" + dep.Service_uid)
							uncheck_service(dep.Service_uid)
							$(cb).prop("checked", false)
						}
					}
					else {
						$("body").append(
								"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>" +
								_("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
								  {
									  service: $(element).attr("title"),
									  deps: dep_titles.join("<br/>")
								  }) + "</div>")
						$("#messagebox").dialog(
							{

								width: 450,
								resizable: false,
								closeOnEscape: false,
								buttons: {
									yes: function () {
										for (i = 0; i < dep_services.length; i += 1) {
											dep = dep_services[i]
											service_uid = dep.Service_uid
											cb = $("#list_cb_" + dep.Service_uid)
											$(cb).prop("checked",
													   false)
											uncheck_service(dep.Service_uid)
										}
										$(this).dialog("close")
										$("#messagebox").remove()
									},
									no: function () {
										service_uid = $(element).attr("value")
										check_service(service_uid)
										$(element).prop("checked",
														true)
										$("#messagebox").remove()
										$(this).dialog("close")
									}
								}
							})
					}
				}
			}
		}
	}
}

