/* Controller class for AnalysisRequestAddView - column layout.
 *
 * The form elements are not submitted.  Instead, their values are inserted
 * into bika.lims.ar_add.state, and this variable is submitted as a json
 * string.
 *
 *
 * Regarding checkboxes: JQuery recommends using .prop() instead of .attr(),
 * but selenium/xpath cannot discover the state of such inputs.  I use
 * .attr("checked",true) and .removeAttr("checked") to set their values,
 * although .prop("checked") is still the correct way to check state of
 * a particular element from JS.
 */

function AnalysisRequestAddByCol() {
	"use strict";

	var that = this

	that.load = function () {

		// disable browser autocomplete
		$('input[type=text]').prop('autocomplete', 'off')

		// load-time form configuration
		form_init()

		/*
		 The state variable is fully populated when the form is submitted,
		 but in many cases it must be updated on the fly, to allow the form
		 to change behaviour based on some selection.  To help with this,
		 there are some generic state-setting handlers below, but these must
		 be augmented with specific handlers for difficult cases.
		 */
		checkbox_change()
		referencewidget_change()
		select_element_change()
		textinput_change()

		client_selected()
		contact_selected()
		spec_field_entry()
		spec_selected()
		samplepoint_selected()
		sampletype_selected()
		profile_selected()
		template_selected()
		drymatter_selected()

		singleservice_dropdown_init()
		singleservice_deletebtn_click()
		analysis_cb_click()

		//		copybutton_click()
		//		sample_selected()

		form_submit()

	}

	// Form management, and utility functions //////////////////////////////////
	/* form_init - load time form config
	 * state_set - should be used when setting fields in the state var
	 * filter_combogrid - filter an existing dropdown (referencewidget)
	 * filter_by_client - Grab the client UID and filter all applicable dropdowns
	 */

	function form_init() {
		/* load-time form configuration
		 *
		 * - Create empty state var
		 * - fix generated elements
		 * - clear existing values (on page reload)
		 * - filter fields based on the selected Client
		 */
		// Create empty state var
		// We include initialisation for a couple of special fields that
		// do not directly tie to specific form controls
		bika.lims.ar_add = {}
		bika.lims.ar_add.state = {}
		var nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
		for (var arnum = 0; arnum < nr_ars; arnum++) {
			bika.lims.ar_add.state[arnum] = {
				'Analyses': []
			}
		}
		// Remove "required" attribute; we will manage this manually, later.
		var elements = $("input[type!='hidden']").not("[disabled]")
		for (var i = elements.length - 1; i >= 0; i--) {
			var element = elements[i]
			$(element).removeAttr("required")
		}
		// DatePickers must have their name/id attributes munged, because
		// they are created identically for each AR column
		$.each($(".ArchetypesDateTimeWidget input"), function (i, e) {
			arnum = $(e).parents("[arnum]").attr("arnum")
			$(e).attr("id", $(e).attr("id") + "_" + arnum)
			$(e).attr("name", $(e).attr("name") + "_" + arnum)
		})

		// clear existing values (on page reload).
		$("#singleservice").val("")
		$("#singleservice").attr("uid", "new")
		$("#singleservice").attr("title", "")
		$("#singleservice").parents("[uid]").attr("uid", "new")
		$("#singleservice").parents("[keyword]").attr("keyword", "")
		$("#singleservice").parents("[title]").attr("title", "")
		$("input[type='checkbox']").removeAttr("checked")
		$(".min,.max,.error").val("")

		// filter fields based on the selected Client
		// we need a little delay here to be sure the elements have finished
		// initialising before we attempt to filter them
		setTimeout(function () {
			var nr_ars = parseInt($("#ar_count").val(), 10)
			for (arnum = 0; arnum < nr_ars; arnum++) {
				filter_by_client(arnum)
			}
		}, 250)
	}

	function state_set(arnum, fieldname, value) {
		/* Use this function to set values in the state variable.
		 */
		var arnum_i = parseInt(arnum, 10)
		if (fieldname && value !== undefined) {
			// console.log("arnum=" + arnum + ", fieldname=" + fieldname + ", value=" + value)
			bika.lims.ar_add.state[arnum_i][fieldname] = value
		}
	}

	function filter_combogrid(element, filterkey, filtervalue, querytype) {
		/* Apply or modify a query filter for a reference widget.
		 *
		 *  This will set the options, then re-create the combogrid widget
		 *  with the new filter key/value.
		 *
		 *  querytype can be 'base_query' or 'search_query'.
		 */
		if (!$(element).is(':visible')) {
			return
		}
		if (!querytype) {
			querytype = 'base_query'
		}
		var query = $.parseJSON($(element).attr(querytype))
		query[filterkey] = filtervalue
		$(element).attr(querytype, $.toJSON(query))
		var options = $.parseJSON($(element).attr("combogrid_options"))
		options.url = window.location.href.split("/ar_add")[0] + "/" + options.url
		options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val()
		options.url = options.url + "&catalog_name=" + $(element).attr("catalog_name")
		if (querytype == 'base_query') {
			options.url = options.url + "&base_query=" + $.toJSON(query)
			options.url = options.url + "&search_query=" + $(element).attr("search_query")
		}
		else {
			options.url = options.url + "&base_query=" + $(element).attr("base_query")
			options.url = options.url + "&search_query=" + $.toJSON(query)
		}
		options.url = options.url + "&colModel=" + $.toJSON($.parseJSON($(element).attr("combogrid_options")).colModel)
		options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['search_fields'])
		options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(element).attr("combogrid_options"))['discard_empty'])
		options.force_all = "false"
		$(element).combogrid(options)
		$(element).addClass("has_combogrid_widget")
		$(element).attr("search_query", "{}")
	}

	function filter_by_client(arnum) {
		/***
		 * Filter all Reference fields that reference Client items
		 *
		 * Some reference fields can select Lab or Client items.  In these
		 * cases, the 'getParentUID' or 'getClientUID' index is used
		 * to filter against Lab and Client folders.
		 */
		var element, uids
		var uid = $($("tr[fieldName='Client'] td[arnum='" + arnum + "'] input")[0]).attr("uid")
		element = $("tr[fieldName=Contact] td[arnum=" + arnum + "] input")[0]
		filter_combogrid(element, "getParentUID", uid)
		element = $("tr[fieldName=CCContact] td[arnum=" + arnum + "] input")[0]
		filter_combogrid(element, "getParentUID", uid)
		element = $("tr[fieldName=InvoiceContact] td[arnum=" + arnum + "] input")[0]
		filter_combogrid(element, "getParentUID", uid)
		uids = [uid, $("#bika_setup").attr("bika_samplepoints_uid")]
		element = $("tr[fieldName=SamplePoint] td[arnum=" + arnum + "] input")[0]
		filter_combogrid(element, "getClientUID", uids)
		uids = [uid, $("#bika_setup").attr("bika_artemplates_uid")]
		element = $("tr[fieldName=Template] td[arnum=" + arnum + "] input")[0]
		filter_combogrid(element, "getClientUID", uids)
		uids = [uid, $("#bika_setup").attr("bika_analysisprofiles_uid")]
		element = $("tr[fieldName=Profile] td[arnum=" + arnum + "] input")[0]
		filter_combogrid(element, "getClientUID", uids)
		uids = [uid, $("#bika_setup").attr("bika_analysisspecs_uid")]
		element = $("tr[fieldName=Specification] td[arnum=" + arnum + "] input")[0]
		filter_combogrid(element, "getClientUID", uids)
	}

	function hashes_to_hash(hashlist, key) {
		/* Convert a list of hashes to a hash, by one of their keys.
		 *
		 * This will return a single hash: the key that will be used must
		 * of course exist in all hashes in hashlist.
		 */
		var ret = {}
		for (var i = 0; i < hashlist.length; i++) {
			ret[hashlist[i][key]] = hashlist[i]
		}
		return ret
	}

	function hash_to_hashes(hash) {
		/* Convert a single hash into a list of hashes
		 *
		 * Basically, this just returns the keys, unmodified.
		 */
		var ret = []
		$.each(hash, function (i, v) {
			ret.push(v)
		})
		return ret
	}

	// Generic handlers for more than one field  ///////////////////////////////
	/*
	 checkbox_change - applies to all except analysis services
	 checkbox_change_handler
	 referencewidget_change - applies to all except #singleservice
	 referencewidget_change_handler
	 select_element_change - select elements are a bit different
	 select_element_change_handler
	 textinput_change - all except referencwidget text elements
	 textinput_change_handler
	 */

	function checkbox_change_handler(element) {
		var arnum = $(element).parents('[arnum]').attr('arnum')
		var fieldName = $(element).parents('[fieldName]').attr('fieldName')
		var value = $(element).prop("checked")
		state_set(arnum, fieldName, value)
	}

	function checkbox_change() {
		/* Generic state-setter for AR field checkboxes
		 * The checkboxes used to select analyses are handled separately.
		 */
		$('tr[fieldName] input[type="checkbox"]')
			.live('change', function () {
					  checkbox_change_handler(this)
				  })
	}

	function referencewidget_change_handler(element, item) {
		var arnum = $(element).parents('[arnum]').attr('arnum')
		var fieldName = $(element).parents('[fieldName]').attr('fieldName')
		state_set(arnum, fieldName, item.UID)
	}

	function referencewidget_change() {
		/* Generic state-setter for AR field referencewidgets
		 */
		$('tr[fieldName] input.referencewidget')
			.live('selected', function (event, item) {
					  referencewidget_change_handler(this, item)
				  })
	}

	function select_element_change_handler(element) {
		var arnum = $(element).parents('[arnum]').attr('arnum')
		var fieldName = $(element).parents('[fieldName]').attr('fieldName')
		var value = $(element).val()
		state_set(arnum, fieldName, value)
	}

	function select_element_change() {
		/* Generic state-setter for SELECT inputs
		 */
		$('tr[fieldName] select')
			.live('change', function (event, item) {
					  select_element_change_handler(this)
				  })
	}

	function textinput_change_handler(element) {
		var arnum = $(element).parents('[arnum]').attr('arnum')
		var fieldName = $(element).parents('[fieldName]').attr('fieldName')
		var value = $(element).val()
		state_set(arnum, fieldName, value)
	}

	function textinput_change() {
		/* Generic state-setter for SELECT inputs
		 */
		$('tr[fieldName] input[type="text"]')
			.not("#singleservice")
			.not(".referencewidget")
			.live('change', function () {
					  textinput_change_handler(this)
				  })
	}

	// Specific handlers for fields requiring special actions  /////////////////
	/*
	 --- These configure the jquery bindings for different fields ---
	 client_selected        -
	 contact_selected		-
	 spec_selected			-
	 samplepoint_selected	-
	 sampletype_selected	-
	 profile_selected		-
	 template_selected		-
	 drymatter_selected		-
	 --- These are called by the above bindings, or by other javascript ---
	 cc_contacts_set 			- when contact is selected, apply CC Contacts
	 spec_field_entry 			- min/max/error field
	 specification_refetch 		- lookup ajax spec and apply to min/max/error
	 specification_apply 		- just re-apply the existing spec
	 spec_from_sampletype 		- sampletype selection may set the current spec
	 spec_filter_on_sampletype 	- there may be >1 allowed specs for a sampletype.
	 samplepoint_set 			- filter with sampletype<->samplepoint relation
	 sampletype_set 			- filter with sampletype<->samplepoint relation
	 profile_set 				- apply profile
	 profile_unset 				- empty profile field in form and state
	 template_set 				- apply template
	 template_unset 			- empty template field in form and state
	 drymatter_set              - select the DryMatterService and set state
	 drymatter_unset            - unset state
	 */

	function client_selected() {
		/* Client field is visibile and a client has been selectec
		 */
		$('tr[fieldName="Client"] input[type="text"]')
			.live('selected', function (event, item) {
					  // filter any references that search inside the Client.
					  var arnum = $(this).parents('[arnum]').attr('arnum')
					  filter_by_client(arnum)
				  })
	}

	function contact_selected() {
		/* Selected a Contact: retrieve and complete UI for CC Contacts
		 */
		$('tr[fieldName="Contact"] input[type="text"]')
			.live('selected', function (event, item) {
					  var arnum = $(this).parents('[arnum]').attr('arnum')
					  cc_contacts_set(arnum)
				  })
	}

	function cc_contacts_set(arnum) {
		/* Setting the CC Contacts after a Contact was set
		 *
		 * Contact.CCContact may contain a list of Contact references.
		 * So we need to select them in the form with some fakey html,
		 * and set them in the state.
		 */
		var td = $("tr[fieldName='Contact'] td[arnum='" + arnum + "']")
		var contact_element = $(td).find("input[type='text']")[0]
		var contact_uid = $(contact_element).attr("uid")
		// clear the CC selector widget and listing DIV
		var cc_div = $("tr[fieldName='CCContact'] td[arnum='" + arnum + "'] .multiValued-listing")
		var cc_uids = $("tr[fieldName='CCContact'] td[arnum='" + arnum + "'] input[name='CCContact_uid']")
		$(cc_div).empty()
		if (contact_uid) {
			var request_data = {
				catalog_name: "portal_catalog",
				UID: contact_uid
			}
			window.bika.lims.jsonapi_read(request_data, function (data) {
				if (data.objects && data.objects.length > 0) {
					var ob = data.objects[0]
					var cc_titles = ob['CCContact']
					var cc_uids = ob['CCContact_uid']
					if (!cc_uids) {
						return
					}
					$(cc_uids).val(cc_uids.join(","))
					for (var i = 0; i < cc_uids.length; i++) {
						var title = cc_titles[i]
						var uid = cc_uids[i]
						var del_btn_src = window.portal_url + "/++resource++bika.lims.images/delete.png"
						var del_btn =
							"<img class='deletebtn' src='" + del_btn_src + "' fieldName='CCContact' uid='" + uid + "'/>"
						var new_item = "<div class='reference_multi_item' uid='" + uid + "'>" + del_btn + title + "</div>"
						$(cc_div).append($(new_item))
					}
					state_set(arnum, 'CCContact', cc_uids.join(","))
				}
			})
		}
	}

	function spec_selected() {
		/* Configure handler for the selection of a Specification
		 *
		 */
		$("[id*='_Specification']")
			.live('selected',
				  function (event, item) {
					  var arnum = $(this).parents('td').attr('arnum')
					  specification_refetch(arnum)
				  })
	}

	function spec_field_entry() {
		/* Validate entry into min/max/error fields, and save them
		 * to the state.
		 *
		 * If min>max or max<min, or error<>0,100, correct the values directly
		 * in the field by setting one or the other to a "" value to indicate
		 * an error
		 */
		$('.min, .max, .error').live('change', function () {
			var td = $(this).parents('td')
			var tr = $(td).parent()
			var arnum = $(td).attr('arnum')
			var uid = $(tr).attr('uid')
			var keyword = $(tr).attr('keyword')
			var min_element = $(td).find(".min")
			var max_element = $(td).find(".max")
			var error_element = $(td).find(".error")
			var min = parseInt(min_element.val(), 10)
			var max = parseInt(max_element.val(), 10)
			var error = parseInt(error_element.val(), 10)

			if ($(this).hasClass("min")) {
				if (isNaN(min)) {
					$(min_element).val("")
				}
				else if ((!isNaN(max)) && min > max) {
					$(max_element).val("")
				}
			}
			else if ($(this).hasClass("max")) {
				if (isNaN(max)) {
					$(max_element).val("")
				}
				else if ((!isNaN(min)) && max < min) {
					$(min_element).val("")

				}
			}
			else if ($(this).hasClass("error")) {
				if (isNaN(error) || error < 0 || error > 100) {
					$(error_element).val("")
				}
			}

			var arnum_i = parseInt(arnum, 10)
			var state = bika.lims.ar_add.state[arnum_i]
			var hash = hashes_to_hash(state['ResultsRange'], 'uid')
			hash[uid] = {
				'min': min_element.val(),
				'max': max_element.val(),
				'error': error_element.val(),
				'uid': uid,
				'keyword': keyword
			}
			var hashes = hash_to_hashes(hash)
			state_set(arnum, 'ResultsRange', hashes)
		})
	}

	function specification_refetch(arnum) {
		/* Lookup the selected specification with ajax, then set all
		 * min/max/error fields in all columns to match.
		 *
		 * If the specification does not define values for a particular service,
		 * the form values will not be cleared.
		 */
		var d = $.Deferred()
		var arnum_i = parseInt(arnum, 10)
		var state = bika.lims.ar_add.state[arnum_i]
		var spec_uid = state['Specification_uid']
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
				var rr = data.objects[0]['ResultsRange']
				if (rr && rr.length > 0) {
					state_set(arnum, 'ResultsRange', rr)
					specification_apply()
				}
			}
			d.resolve()
		})
		return d.promise()
	}

	function specification_apply() {
		var nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
		for (var arnum = 0; arnum < nr_ars; arnum++) {
			var hashlist = bika.lims.ar_add.state[arnum]['ResultsRange']
			if (hashlist) {
				var spec = hashes_to_hash(hashlist, 'uid')
				$.each($("tr.service_selector td[arnum='" + arnum + "']"),
					   function (i, td) {
						   var uid = $(td).parents("[uid]").attr("uid")
						   if (uid && uid != "new" && uid in spec) {
							   var min = $(td).find(".min")
							   var max = $(td).find(".max")
							   var error = $(td).find(".error")
							   $(min).attr("value", (spec[uid].min))
							   $(max).attr("value", (spec[uid].max))
							   $(error).attr("value", (spec[uid].error))
						   }
					   })
			}
		}
	}

	function set_spec_from_sampletype(arnum) {
		/* Look for Specifications with the selected SampleType.
		 *
		 * 1) Set the value of the Specification field
		 * 2) Fetch the spec from the server, and set all the spec field values
		 * 3) Set the partition indicator numbers.
		 */
		var st_uid = $("tr[fieldName='SampleType'] " +
					   "td[arnum='" + arnum + "'] " +
					   "input[type='text']").attr("uid")
		if (!st_uid) {
			return
		}
		spec_filter_on_sampletype(arnum)
		var spec_element = $("tr[fieldName='Specification'] " +
							 "td[arnum='" + arnum + "'] " +
							 "input[type='text']")
		var spec_uid_element = $("tr[fieldName='Specification'] " +
								 "td[arnum='" + arnum + "'] " +
								 "input[id$='_uid']")
		var request_data = {
			catalog_name: "bika_setup_catalog",
			portal_type: "AnalysisSpec",
			getSampleTypeUID: st_uid,
			include_fields: ["Title", "UID", "ResultsRange"]
		}
		window.bika.lims.jsonapi_read(request_data, function (data) {
			if (data.objects.length > 0) {
				// If there is one Lab and one Client spec defined, the
				// client spec will be objects[0]
				var spec = data.objects[0]
				// set spec values for this arnum
				$(spec_element).val(spec["Title"])
				$(spec_element).attr("uid", spec["UID"])
				$(spec_uid_element).val(spec['UID'])
				state_set(arnum, 'Specification', spec['UID'])
				// set ResultsRange here!
				var rr = data.objects[0]['ResultsRange']
				if (rr && rr.length > 0) {
					state_set(arnum, 'ResultsRange', rr)
					specification_apply()
				}
			}
		})
	}

	function spec_filter_on_sampletype(arnum) {
		/* Possibly filter the Specification dropdown when SampleType selected
		 *
		 * when a SampleType is selected I will allow only specs to be
		 * selected which have a matching SampleType value, or which
		 * have no sampletype set.
		 */
		var arnum_i = parseInt(arnum, 10)
		var sampletype_uid = bika.lims.ar_add.state[arnum_i]['SampleType']
		var spec_element = $("tr[fieldName='Specification'] td[arnum='" + arnum + "'] input[type='text']")
		var query_str = $(spec_element).attr("search_query")
		var query = $.parseJSON(query_str)
		if (query.hasOwnProperty("getSampleTypeUID")) {
			delete query.getSampleTypeUID
		}
		query.getSampleTypeUID = [encodeURIComponent(sampletype_uid), ""]
		query_str = $.toJSON(query)
		$(spec_element).attr("search_query", query_str)
	}

	function samplepoint_selected() {
		$("tr[fieldName='SamplePoint'] td[arnum] input[type='text']")
			.live('selected', function (event, item) {
					  var arnum = $(this).parents("[arnum]").attr("arnum")
					  samplepoint_set(arnum)
				  })
	}

	function sampletype_selected() {
		$("tr[fieldName='SampleType'] td[arnum] input[type='text']")
			.live('selected', function (event, item) {
					  var arnum = $(this).parents("[arnum]").attr("arnum")
					  sampletype_set(arnum)
				  })
	}

	function samplepoint_set(arnum) {
		/***
		 * Sample point and Sample type can set each other.
		 */
		var spe = $("tr[fieldName='SamplePoint'] td[arnum='" + arnum + "'] input[type='text']")
		var ste = $("tr[fieldName='SampleType'] td[arnum='" + arnum + "'] input[type='text']")
		filter_combogrid(ste, "getSamplePointTitle", $(spe).val(),
						 'search_query')
	}

	function sampletype_set(arnum) {
		// setting the Sampletype - Fix the SamplePoint filter:
		// 1. Can select SamplePoint which does not link to any SampleType
		// 2. Can select SamplePoint linked to This SampleType.
		// 3. Cannot select SamplePoint linked to other sample types (and not to this one)
		var spe = $("tr[fieldName='SamplePoint'] td[arnum='" + arnum + "'] input[type='text']")
		var ste = $("tr[fieldName='SampleType'] td[arnum='" + arnum + "'] input[type='text']")
		filter_combogrid(spe, "getSampleTypeTitle", $(ste).val(),
						 'search_query')
		set_spec_from_sampletype(arnum)
		partition_indicators_set(arnum)
	}

	function profile_selected() {
		/* A profile is selected.
		 * - Set the profile's analyses (existing analyses will be cleared)
		 * - Set the partition number indicators
		 */
		$("tr[fieldName='Profile'] td[arnum] input[type='text']")
			.live('selected', function (event, item) {
					  var arnum = $(this).parents('td').attr('arnum')
					  profile_set(arnum, $(this).val())
						  .then(function () {
									specification_apply()
									partition_indicators_set(arnum)
								})
				  })
	}

	function profile_set(arnum, profile_title) {
		/* Set the profile analyses for the AR in this column
		 *  This will clear  analyses in this AR column, and it will
		 *  also clear the AR Template field.
		 */
		template_unset(arnum)
		var d = $.Deferred()
		var request_data = {
			catalog_name: "bika_setup_catalog",
			portal_type: "AnalysisProfile",
			title: profile_title
		}
		bika.lims.jsonapi_read(request_data, function (data) {
			var profile = data['objects'][0]
			// Set the services from the template into the form
			uncheck_all_services(arnum)
			if ($('#singleservice').length > 0) {
				expand_services_singleservice(arnum, profile['service_data'])
			}
			else {
				expand_services_bika_listing(arnum, profile['service_data'])
			}
			d.resolve()
		})
		return d.promise()
	}

	function profile_unset(arnum) {
		var td = $("tr[fieldName='Profile'] td[arnum='" + arnum + "']")
		$(td).find("input[type='text']").val("").attr("uid", "")
		$(td).find("input[id$='_uid']").val("")
	}

	function template_selected() {
		$("tr[fieldName='Template'] td[arnum] input[type='text']")
			.live('selected', function (event, item) {
					  var arnum = $(this).parents('td').attr('arnum')
					  template_set(arnum, $(this).val())
				  })
	}

	function template_set(arnum, template_title) {
		var d = $.Deferred()
		uncheck_all_services(arnum)
		var td = $("tr[fieldName='Template'] " +
				   "td[arnum='" + arnum + "'] ")
		var uid = $(td).find("input[id$='_uid']").val()
		var request_data = {
			catalog_name: "bika_setup_catalog",
			UID: uid,
			include_fields: [
				"SampleType",
				"SampleTypeUID",
				"SamplePoint",
				"SamplePointUID",
				"ReportDryMatter",
				"AnalysisProfile",
				"Partitions",
				"Analyses",
				"Prices"]
		}
		window.bika.lims.jsonapi_read(request_data, function (data) {

			var template = data.objects[0]
			var td

			// set SampleType
			td = $("tr[fieldName='SampleType'] td[arnum='" + arnum + "']")
			$(td).find("input[type='text']")
				.val(template['SampleType'])
				.attr("uid", template['SampleTypeUID'])
			$(td).find("input[id$='_uid']")
				.val(template['SampleTypeUID'])
			state_set(arnum, 'SampleType', template['SampleTypeUID'])

			// set Specification from selected SampleType
			set_spec_from_sampletype(arnum)

			// set SamplePoint
			td = $("tr[fieldName='SamplePoint'] td[arnum='" + arnum + "']")
			$(td).find("input[type='text']")
				.val(template['SamplePoint'])
				.attr("uid", template['SamplePointUID'])
			$(td).find("input[id$='_uid']")
				.val(template['SamplePointUID'])
			state_set(arnum, 'SamplePoint', template['SamplePointUID'])

			// Set the ARTemplate's AnalysisProfile
			td = $("tr[fieldName='Profile'] td[arnum='" + arnum + "']")
			if (template['AnalysisProfile']) {
				$(td).find("input[type='text']")
					.val(template['AnalysisProfile'])
					.attr("uid", template['AnalysisProfileUID'])
				$(td).find("input[id$='_uid']")
					.val(template['AnalysisProfileUID'])
				state_set(arnum, 'Profile', template['AnalysisProfileUID'])
			}
			else {
				profile_unset(arnum)
			}

			// Set the services from the template into the form
			uncheck_all_services(arnum)
			if ($('#singleservice').length > 0) {
				expand_services_singleservice(arnum, template['service_data'])
			}
			else {
				expand_services_bika_listing(arnum, template['service_data'])
			}

			// Dry Matter checkbox.  drymatter_set will calculate it's
			// dependencies and select them, and apply specs
			td = $("tr[fieldName='ReportDryMatter'] td[arnum='" + arnum + "']")
			if (template['ReportDryMatter']) {
				$(td).find("input[type='checkbox']").attr("checked", true)
				drymatter_set(arnum, true)
			}
			else {
				$(td).find("input[type='checkbox']").removeAttr("checked")
				drymatter_unset(arnum)
			}

			// Now apply the Template's partition information to the form.
			// If the template doesn't specify partition information,
			// calculate it like normal.
			if (template['Partitions']) {
				// Stick the current template's partition setup into the state
				// though it were sent there by a the deps calculating ajax
				state_set(arnum, 'Partitions', template['Partitions'])
			}
			else {
				// ajax request to calculate the partitions from the form
				partnrs_calc(arnum)
			}
			_partition_indicators_set(arnum)

			// prices_update(arnum)

			d.resolve()
		})
		return d.promise()
	}

	function template_unset(arnum) {
		var td = $("tr[fieldName='Template'] td[arnum='" + arnum + "']")
		$(td).find("input[type='text']").val("").attr("uid", "")
		$(td).find("input[id$='_uid']").val("")
	}

	function drymatter_selected() {
		$("tr[fieldName='ReportDryMatter'] td[arnum] input[type='checkbox']")
			.live('click', function (event) {
					  var arnum = $(this).parents("[arnum]").attr("arnum")
					  if ($(this).prop("checked")) {
						  drymatter_set(arnum)
						  partition_indicators_set(arnum)
					  }
					  else {
						  drymatter_unset(arnum)
					  }
				  })
	}

	function drymatter_set(arnum) {
		/* set the Dry Matter service, dependencies, etc

		 skip_indicators should be true if you want to prevent partition
		 indicators from being set.  This is useful if drymatter is being
		 checked during the application of a Template to this column.
		 */
		var dm_service = $("#getDryMatterService")
		var uid = $(dm_service).val()
		var cat = $(dm_service).attr("cat")
		var poc = $(dm_service).attr("poc")
		var keyword = $(dm_service).attr("keyword")
		var title = $(dm_service).attr("title")
		var price = $(dm_service).attr("price")
		var vatamount = $(dm_service).attr("vatamount")
		var element = $("tr[fieldName='ReportDryMatter'] " +
						"td[arnum='" + arnum + "'] " +
						"input[type='checkbox']")
		// set drymatter service IF checkbox is checked
		if ($(element).attr("checked")) {
			// bika_listing service selection form
			if ($("#singleservice")) {
				var checkbox = $("tr[uid='" + uid + "'] " +
								 "td[arnum='" + arnum + "'] " +
								 "input[type='checkbox']")
				if ($(checkbox).length > 0) {
					analysis_cb_check(arnum, uid)
				}
				else {
					$("#singleservice").attr("uid", uid)
					$("#singleservice").attr("keyword", keyword)
					$("#singleservice").attr("title", title)
					$("#singleservice").attr("price", price)
					$("#singleservice").attr("vatamount", vatamount)
					singleservice_duplicate(uid, title, keyword, price,
											vatamount)
					analysis_cb_check(arnum, uid)
				}
				state_analyses_push(arnum, uid)
			}
			// bika_listing service selection form
			else {
				console.log("XXX implement bika_listing drymatter service selections")
			}
			deps_calc(arnum, [uid], true, _("Dry Matter"))
			recalc_prices(arnum)
			state_set(arnum, 'ReportDryMatter', true)
			specification_apply()
		}
	}

	function drymatter_unset(arnum) {
		// if disabling, then we must still update the state var
		state_set(arnum, 'ReportDryMatter', false)
	}

	// Functions related to the service_selector forms.  ///////////////////////
	/*
	 singleservice_dropdown_init	- configure the combogrid (includes handler)
	 singleservice_duplicate		- create new service row
	 singleservice_deletebtn_click	- remove a service from the form
	 expand_services_singleservice	- add a list of services (single-service)
	 expand_services_bika_listing	- add a list of services (bika_listing)
	 uncheck_all_services			- unselect all from form and state
	 */

	function singleservice_dropdown_init() {
		/*
		 * Configure the single-service selector combogrid
		 */
		var authenticator = $("[name='_authenticator']").val()
		var url = window.location.href.split("/portal_factory")[0] +
			"/service_selector?_authenticator=" + authenticator
		var options = {
			url: url,
			width: "700px",
			showOn: false,
			searchIcon: true,
			minLength: "2",
			resetButton: false,
			sord: "asc",
			sidx: "Title",
			colModel: [
				{
					"columnName": "Title",
					"align": "left",
					"label": "Title",
					"width": "50"
				},
				{
					"columnName": "Identifiers",
					"align": "left",
					"label": "Identifiers",
					"width": "35"
				},
				{
					"columnName": "Keyword",
					"align": "left",
					"label": "Keyword",
					"width": "15"
				},
				{"columnName": "Price", "hidden": true},
				{"columnName": "VAT", "hidden": true},
				{"columnName": "UID", "hidden": true}
			],
			select: function (event, ui) {
				// Set some attributes on #singleservice to assist the
				// singleservice_duplicate function in it's work
				var arnum = $(this).parents("[arnum]").length > 0
					? $(this).parents("[arnum]").attr("arnum")
					: 0
				$("#singleservice").attr("uid", ui['item']['UID'])
				$("#singleservice").attr("keyword", ui['item']['Keyword'])
				$("#singleservice").attr("title", ui['item']['Title'])
				singleservice_duplicate(ui['item']['UID'],
										ui['item']['Title'],
										ui['item']['Keyword'],
										ui['item']['Price'],
										ui['item']['VAT'])
			}
		}
		$("#singleservice").combogrid(options)
	}

	function singleservice_duplicate(new_uid, new_title, new_keyword,
									 new_price, new_vatamount) {
		/*
		 After selecting a service from the #singleservice combogrid,
		 this function is reponsible for duplicating the TR.  This is
		 factored out so that template, profile etc, can also duplicate
		 rows.

		 Clobber the old row first, set all it's attributes to look like
		 bika_listing version of itself.

		 The attributes are a little wonky perhaps.  They should mimic the
		 attributes that bika_listing rows get, so that the event handlers
		 don't have to care.  In some cases though, we need functions for
		 both.

		 does not set any checkbox values
		 */

		// Grab our operating parameters from wherever
		var uid = new_uid || $("#singleservice").attr("uid")
		var keyword = new_keyword || $("#singleservice").attr("keyword")
		var title = new_title || $("#singleservice").attr("title")
		var price = new_price || $("#singleservice").attr("price")
		var vatamount = new_vatamount || $("#singleservice").attr("vatamount")

		// If this service already exists, abort
		var existing = $("tr[uid='" + uid + "']")
		if (existing.length > 0) {
			return
		}

		// clone tr before anything else
		var tr = $("#singleservice").parents("tr")
		var new_tr = $(tr).clone()

		// store row attributes on TR
		$(tr).attr("uid", uid)
		$(tr).attr("keyword", keyword)
		$(tr).attr("title", title)
		$(tr).attr("price", price)
		$(tr).attr("vatamount", vatamount)

		// select_all
		$(tr).find("input[name='uids:list']").attr('value', uid)
		// alert containers
		$(tr).find('.alert').attr('uid', uid)
		// Replace the text widget with a label, delete btn etc:
		var service_label = $(
			"<a href='#' class='deletebtn'><img src='" + portal_url +
			"/++resource++bika.lims.images/delete.png' uid='" + uid +
			"' style='vertical-align: -3px;'/></a>&nbsp;" +
			"<span>" + title + "</span>")
		$(tr).find("#singleservice").replaceWith(service_label)

		// Set spec values manually for the row xyz
		// Configure and insert new row
		$(new_tr).find("[type='checkbox']").removeAttr("checked")
		$(new_tr).find("[type='text']").val("")
		$(new_tr).find("#singleservice").attr("uid", "new")
		$(new_tr).find("#singleservice").attr("keyword", "")
		$(new_tr).find("#singleservice").attr("title", "")
		$(new_tr).find("#singleservice").attr("price", "")
		$(new_tr).find("#singleservice").attr("vatamount", "")
		$(new_tr).find("#singleservice").removeClass("has_combogrid_widget")
		$(tr).after(new_tr)
		specification_apply()
		singleservice_dropdown_init()
	}

	function singleservice_deletebtn_click() {
		/* Remove the service row.
		 */
		$(".service_selector a.deletebtn").live('click', function (event) {
			event.preventDefault()
			var tr = $(this).parents("tr[uid]")
			var checkboxes = $(tr).find("input[type='checkbox']").not("[name='uids:list']")
			for (var i = 0; i < checkboxes.length; i++) {
				var element = checkboxes[i]
				var arnum = $(element).parents('[arnum]').attr("arnum")
				var uid = $(element).parents('[uid]').attr("uid")
				state_analyses_remove(arnum, uid)
			}
			$(tr).remove()
		})
	}

	function expand_services_singleservice(arnum, service_data) {
		/*
		 When the single-service serviceselector is in place,
		 this function is called to select services for setting a bunch
		 of services in one AR, eg Profiles and Templates.

		 service_data is included from the JSONReadExtender of Profiles and
		 Templates.
		 */
		// First Select services which are already present
		var uid, keyword, title, price, vatamount
		var not_present = []
		var sd = service_data
		for (var i = 0; i < sd.length; i++) {
			uid = sd[i]["UID"]
			keyword = sd[i]["Keyword"]
			price = sd[i]["Price"]
			vatamount = sd[i]["VAT"]
			var e = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] input[type='checkbox']")
			e.length > 0
				? analysis_cb_check(arnum, sd[i]["UID"])
				: not_present.push(sd[i])
		}
		// Insert services which are not yet present
		for (var i = 0; i < not_present.length; i++) {
			title = not_present[i]["Title"]
			uid = not_present[i]["UID"]
			keyword = not_present[i]["Keyword"]
			price = not_present[i]["Price"]
			vatamount = not_present[i]["VAT"]
			$("#singleservice").val(title)
			$("#singleservice").attr("uid", uid)
			$("#singleservice").attr("keyword", keyword)
			$("#singleservice").attr("title", title)
			$("#singleservice").attr("price", price)
			$("#singleservice").attr("vatamount", vatamount)
			singleservice_duplicate(uid, title, keyword, price, vatamount)
			analysis_cb_check(arnum, uid)
		}
		recalc_prices(arnum)
	}

	function expand_services_bika_listing(arnum, service_data) {
		// When the bika_listing serviceselector is in place,
		// this function is called to select services for Profiles and Templates.
		var service_uids = []
		for (var si = 0; si < service_data.length; si++) {
			var service = service_data[si]
			service_uids.push(service['UID'])
			var poc = service['PointOfCapture']
			$('#services_' + poc + ' [cat="' + service['CategoryTitle'] + '"].collapsed').click()
			$('#' + service['UID'] + '-ar\\.' + arnum).attr("checked", true)
			$('#' + service['UID'] + '-ar\\.' + arnum).change()
		}
	}

	function uncheck_all_services(arnum) {
		// Remove checkboxes for all existing services in this column
		var cblist = $("tr[uid] td[arnum='" + arnum + "'] input[type='checkbox']")
			.filter(":checked")
		for (var i = 0; i < cblist.length; i++) {
			var e = cblist[i]
			var arnum = $(e).parents("[arnum]").attr("arnum")
			var uid = $(e).parents("[uid]").attr("uid")
			analysis_cb_uncheck(arnum, uid)
		}
	}

	// analysis service checkboxes /////////////////////////////////////////////
	/* - analysis_cb_click   user interaction with form (select, unselect)
	 * - analysis_cb_check   performs the same action, but from code (no .click)
	 * - analysis_cb_uncheck does the reverse
	 * - analysis_cb_after_change  always runs when service checkbox changes.
	 * - state_analyses_push		add selected service to state
	 * - state_analyses_remove		remove service uid from state
	 */

	function analysis_cb_click() {
		/* configures handler for click event on analysis checkboxes
		 * and their associated select-all checkboxes.
		 *
		 * As far as possible, the bika_listing and single-select selectors
		 * try to emulate each other's HTML structure in each row.
		 *
		 */
		// regular analysis cb
		$(".service_selector input[type='checkbox'][name!='uids:list']")
			.live('click', function () {
					  var arnum = $(this).parents("[arnum]").attr("arnum")
					  var uid = $(this).parents("[uid]").attr("uid")
					  analysis_cb_after_change(arnum, uid)
					  // Now we will manually decide if we should add or
					  // remove the service UID from state['Analyses'].
					  if ($(this).prop("checked")) {
						  state_analyses_push(arnum, uid)
					  }
					  else {
						  state_analyses_remove(arnum, uid)
					  }
					  // If the click is on "new" row, focus the selector
					  if (uid == "new") {
						  $("#singleservice").focus()
					  }
					  var title = $(this).parents("[title]").attr("title")
					  deps_calc(arnum, [uid], false, title)
					  partition_indicators_set(arnum)
					  recalc_prices(arnum)
				  })
		// select-all cb
		$(".service_selector input[type='checkbox'][name='uids:list']")
			.live('click', function () {
					  var nr_ars = parseInt($('#ar_count').val(), 10)
					  var tr = $(this).parents("tr")
					  var uid = $(this).parents("[uid]").attr("uid")
					  var checked = $(this).prop("checked")
					  var checkboxes = $(tr).find("input[type=checkbox][name!='uids:list']")
					  for (var i = 0; i < checkboxes.length; i++) {
						  if (checked) {
							  analysis_cb_check(i, uid)
						  }
						  else {
							  analysis_cb_uncheck(i, uid)
						  }
						  recalc_prices(i)
					  }
					  var title = $(this).parents("[title]").attr("title")
					  for (i = 0; i < nr_ars; i++) {
						  deps_calc(i, [uid], true, title)
						  partition_indicators_set(i)
					  }
					  // If the click is on "new" row, focus the selector
					  if (uid == "new") {
						  $("#singleservice").focus()
					  }
				  })
	}

	function analysis_cb_check(arnum, uid) {
		/* Called to un-check an Analysis' checkbox as though it were clicked.
		 */
		var cb = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] input[type='checkbox']")
		$(cb).attr("checked", true)
		analysis_cb_after_change(arnum, uid)
		state_analyses_push(arnum, uid)
		specification_apply()
	}

	function analysis_cb_uncheck(arnum, uid) {
		/* Called to un-check an Analysis' checkbox as though it were clicked.
		 */
		var cb = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] input[type='checkbox']")
		$(cb).removeAttr("checked")
		analysis_cb_after_change(arnum, uid)
		state_analyses_remove(arnum, uid)
	}

	function analysis_cb_after_change(arnum, uid) {
		/* If changed by click or by other trigger, all analysis checkboxes
		 * must invoke this function.
		 */
		var cb = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] input[type='checkbox']")
		var tr = $(cb).parents("tr")
		var checked = $(cb).prop("checked")
		var checkboxes = $(tr).find("input[type=checkbox][name!='uids:list']")
		// sync the select-all checkbox state
		var nr_checked = $(checkboxes).filter(":checked")
		if (nr_checked.length == checkboxes.length) {
			$(tr).find("[name='uids:list']").attr("checked", true)
		}
		else {
			$(tr).find("[name='uids:list']").removeAttr("checked")
		}
		// Unselecting Dry Matter Service unsets 'Report Dry Matter'
		if (uid == $("#getDryMatterService").val() && !checked) {
			var dme = $("#ar_" + arnum + "_ReportDryMatter")
			$(dme).removeAttr("checked")
		}
	}

	function state_analyses_push(arnum, uid) {
		arnum = parseInt(arnum, 10)
		var analyses = bika.lims.ar_add.state[arnum]['Analyses']
		if (analyses.indexOf(uid) == -1) {
			analyses.push(uid)
			state_set(arnum, 'Analyses', analyses)
		}
	}

	function state_analyses_remove(arnum, uid) {
		arnum = parseInt(arnum, 10)
		var analyses = bika.lims.ar_add.state[arnum]['Analyses']
		if (analyses.indexOf(uid) > -1) {
			analyses.splice(analyses.indexOf(uid), 1)
			state_set(arnum, 'Analyses', analyses)
		}
	}

	// form/UI functions: not related to specific fields ///////////////////////
	/* partnrs_calc calls the ajax url, and sets the state variable
	 * partition_indicators_set calls partnrs_calc, and modifies the form.
	 * partition_indicators_from_template set state partnrs from template
	 * _partition_indicators_set actually does the form/ui work
	 */

	function partnrs_calc(arnum) {
		/* Configure the state partition data with an ajax call
		 * - calls to /calculate_partitions json url
		 *
		 */
		var d = $.Deferred()
		arnum = parseInt(arnum, 10)

		//// Template columns are not calculated - they are set manually.
		//// I have disabled this behaviour, to simplify the action of adding
		//// a single extra service to a Template column.
		//var te = $("tr[fieldName='Template'] td[arnum='" + arnum + "'] input[type='text']")
		//if (!$(te).val()) {
		//	d.resolve()
		//	return d.promise()
		//}

		var st_uid = bika.lims.ar_add.state[arnum]['SampleType']
		var service_uids = bika.lims.ar_add.state[arnum]['Analyses']

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
							   bika.lims.ar_add.state[arnum]['Partitions'] = data['parts']
						   }
						   d.resolve()
					   }
				   })
		}
		else {
			var data = window.jsonapi_cache[cacheKey]
			bika.lims.ar_add.state[arnum]['Partitions'] = data['parts']
			d.resolve()
		}
		return d.promise()
	}

	function _partition_indicators_set(arnum) {
		// partnrs_calc (or some template!) should have already set the state.

		// Be aware here, that some services may not have part info, eg if a
		// template was applied with only partial info.  This function literally
		// uses "part-1" as a default

		arnum = parseInt(arnum, 10)
		var parts = bika.lims.ar_add.state[arnum]['Partitions']
		if (!parts) {
			return
		}
		// I'll be looping all the checkboxes currently visible in this column
		var checkboxes = $("tr[uid] td[arnum='" + arnum + "'] " +
						   "input[type='checkbox'][name!='uids:list']")
		// the UIDs of services which are not found in any partition should
		// be indicated.  anyway there should be some default applied, or
		// selection allowed.
		for (var n = 0; n < checkboxes.length; n++) {
			var cb = checkboxes[n]
			var span = $(cb).parents("[arnum]").find(".partnr")
			var uid = $(cb).parents("[uid]").attr("uid")
			if ($(cb).prop("checked")) {
				// this service is selected - locate a partnr for it
				var partnr = 1
				for (var p = 0; p < parts.length; p++) {
					if (parts[p]['services'].indexOf(uid) > -1) {
						if (parts[p]["part_id"]) {
							partnr = parts[p]["part_id"].split("-")[1]
						}
						else {
							partnr = p + 1
						}
						break
					}
				}
				// print the new partnr into the span
				$(span).html(partnr)
			}
			else {
				// this service is not selected - remove the partnr
				$(span).html("&nbsp;")
			}
		}
	}

	function partition_indicators_set(arnum, skip_calculation) {
		/* Calculate and Set partition indicators
		 * set skip_calculation if the state variable already contains
		 * calculated partitions (eg, when setting template)
		 */
		if (skip_calculation) {
			_partition_indicators_set(arnum)
		}
		else {
			partnrs_calc(arnum).done(function () {
				_partition_indicators_set(arnum)
			})
		}
	}

	function recalc_prices(arnum) {
		var price
		var subtotal = 0.00
		var discount_amount = 0.00
		var vat = 0.00
		var total = 0.00
		var discount_pcnt = parseFloat($("#bika_setup").attr("MemberDiscount"))
		var checked = $("tr[uid] td[arnum='" + arnum + "'] input[type='checkbox']:checked")
		for (var i = 0; i < checked.length; i++) {
			var cb = checked[i]
			var form_price = $(cb).parents("[price]").attr("price")
			var vatamount = $(cb).parents("[vatamount]").attr("vatamount")
			if ($(cb).prop("checked") && !$(cb).prop("disabled")) {
				if (discount_pcnt) {
					price = form_price - ((form_price / 100) * discount_pcnt)
				}
				else {
					price = form_price
				}
				subtotal += price
				discount_amount += ((form_price / 100) * discount_pcnt)
				vat += ((price / 100) * vatamount)
				total += price + ((price / 100) * vatamount)
			}
		}
		$("td[arnum='" + arnum + "'] span.price.discount").html(discount_amount.toFixed(2))
		$("td[arnum='" + arnum + "'] span.price.subtotal").html(subtotal.toFixed(2))
		$("td[arnum='" + arnum + "'] span.price.vat").html(vat.toFixed(2))
		$("td[arnum='" + arnum + "'] span.price.total").html(total.toFixed(2))
	}


	// dependencies ////////////////////////////////////////////////////////////
	/*
	 deps_calc					- the main routine for dependencies/dependants
	 dependencies_add_confirm	- adding dependancies to the form/state: confirm
	 dependancies_add_yes		- clicked yes
	 dependencies_add_no		- clicked no
	 */

	function deps_calc(arnum, uids, skip_confirmation, initiator) {
		/* Calculate dependants and dependencies.
		 *
		 * arnum - the column number.
		 * uids - zero or more service UIDs to calculate
		 * skip_confirmation - assume yes instead of confirmation dialog
		 * initiator - the service or control that initiated this check.
		 *             used for a more pretty dialog box header.
		 */
		jarn.i18n.loadCatalog('bika')
		var _ = window.jarn.i18n.MessageFactory("bika")

		var Dep
		var i, cb, dep_element
		var lims = window.bika.lims
		var dep_services = []  // actionable services
		var dep_titles = []    // pretty titles

		for (var n = 0; n < uids.length; n++) {
			var uid = uids[n]
			if (uid == "new") {
				continue
			}
			var element = $("tr[uid='" + uids[n] + "'] " +
							"td[arnum='" + arnum + "'] " +
							"input[type='checkbox']")
			var initiator = $(element).parents("[title]").attr("title")

			// selecting a service; discover dependencies
			if ($(element).prop("checked")) {
				var Dependencies = lims.AnalysisService.Dependencies(uid)
				for (i = 0; i < Dependencies.length; i++) {
					// single-service selector form ////////////////////////////
					if ($("#singleservice")) {
						var Dep = Dependencies[i]
						dep_element = $("tr[uid='" + Dep['Service_uid'] + "'] " +
										"td[arnum='" + arnum + "'] " +
										"input[type='checkbox']")
						if (!$(dep_element).prop("checked")) {
							dep_titles.push(Dep['Service'])
							dep_services.push(Dep)
						}
					}
					// bika_listing service selector form //////////////////////
					else {
						console.log("XXX")
					}
				}
				if (dep_services.length > 0) {
					if (skip_confirmation) {
						dependancies_add_yes(arnum, dep_services)
					}
					else {
						dependencies_add_confirm(initiator, dep_services,
												 dep_titles)
							.done(function (data) {
									  dependancies_add_yes(arnum, dep_services)
								  })
							.fail(function (data) {
									  dependencies_add_no(arnum, uid)
								  })
					}
				}
			}
			// unselecting a service; discover back dependencies
			// this means, services which employ calculations, which in turn
			// require these other services' results in order to be calculated.
			else {
				var Dependants = lims.AnalysisService.Dependants(uid)
				for (i = 0; i < Dependants.length; i++) {
					// single-service selector form ////////////////////////////
					if ($("#singleservice")) {
						Dep = Dependants[i]
						dep_element = $("tr[uid='" + Dep['Service_uid'] + "'] " +
										"td[arnum='" + arnum + "'] " +
										"input[type='checkbox']")
						if ($(dep_element).prop("checked")) {
							dep_titles.push(Dep['Service'])
							dep_services.push(Dep)
						}
					}
					// bika_listing service selector form //////////////////////
					else {
						console.log("XXX")
					}
				}
				if (dep_services.length > 0) {
					if (skip_confirmation) {
						dependants_remove_yes(arnum, dep_services)
					}
					else {
						dependants_remove_confirm(initiator, dep_services,
												  dep_titles)
							.done(function (data) {
									  dependants_remove_yes(arnum, dep_services)
								  })
							.fail(function (data) {
									  dependants_remove_no(arnum, uid)
								  })
					}
				}
			}

		}
	}

	function dependants_remove_confirm(initiator, dep_services, dep_titles) {
		var d = $.Deferred()
		$("body").append(
			"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>" +
			_("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
			  {
				  service: initiator,
				  deps: dep_titles.join("<br/>")
			  }) + "</div>")
		$("#messagebox")
			.dialog(
			{
				width: 450,
				resizable: false,
				closeOnEscape: false,
				buttons: {
					yes: function () {
						d.resolve()
						$(this).dialog("close");
						$("#messagebox").remove();
					},
					no: function () {
						d.reject()
						$(this).dialog("close");
						$("#messagebox").remove();
					}
				}
			})
		return d.promise()
	}

	function dependants_remove_yes(arnum, dep_services) {
		for (var i = 0; i < dep_services.length; i += 1) {
			var Dep = dep_services[i]
			var uid = Dep['Service_uid']
			analysis_cb_uncheck(arnum, uid)
		}
		_partition_indicators_set(arnum)
	}

	function dependants_remove_no(arnum, uid) {
		analysis_cb_check(arnum, uid)
		_partition_indicators_set(arnum)
	}

	function dependencies_add_confirm(initiator_title, dep_services,
									  dep_titles) {
		/*
		 uid - this is the analysisservice checkbox which was selected
		 dep_services and dep_titles are the calculated dependencies
		 initiator_title is the dialog title, this could be a service but also could
		 be "Dry Matter" or some other name
		 */
		var d = $.Deferred()
		var html = "<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"
		html = html + _("<p>${service} requires the following services to be selected:</p>" +
						"<br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
						{
							service: initiator_title,
							deps: dep_titles.join("<br/>")
						})
		html = html + "</div>"
		$("body").append(html)
		$("#messagebox")
			.dialog(
			{
				width: 450,
				resizable: false,
				closeOnEscape: false,
				buttons: {
					yes: function () {
						d.resolve()
						$(this).dialog("close");
						$("#messagebox").remove();
					},
					no: function () {
						d.reject()
						$(this).dialog("close");
						$("#messagebox").remove();
					}
				}
			})
		return d.promise()
	}

	function dependancies_add_yes(arnum, dep_services) {
		/*
		 Adding required analyses to this AR - Clicked "yes" to confirmation,
		 or if confirmation dialog is skipped, this function is called directly.
		 */
		for (var i = 0; i < dep_services.length; i++) {
			var Dep = dep_services[i]
			var uid = Dep['Service_uid']
			var dep_cb = $("tr[uid='" + uid + "'] " +
						   "td[arnum='" + arnum + "'] " +
						   "input[type='checkbox']")
			if (dep_cb.length > 0) {
				// row already exists
				if ($(dep_cb).prop("checked")) {
					// skip if checked already
					continue
				}
			}
			else {
				// create new row for all services we may need
				singleservice_duplicate(Dep['Service_uid'],
										Dep["Service"],
										Dep["Keyword"],
										Dep["Price"],
										Dep["VAT"])
			}
			// finally check the service
			analysis_cb_check(arnum, uid);
		}
		recalc_prices(arnum)
		_partition_indicators_set(arnum)
	}

	function dependencies_add_no(arnum, uid) {
		/*
		 Adding required analyses to this AR - clicked "no" to confirmation.
		 This is just responsible for un-checking the service that was
		 used to invoke this routine.
		 */
		var element = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] input[type='checkbox']")
		if ($(element).prop("checked")) {
			analysis_cb_uncheck(arnum, uid);
		}
		_partition_indicators_set(arnum)
	}

	// Form submission /////////////////////////////////////////////////////////

	function set_state_from_form_values() {
		var nr_ars = parseInt($("#ar_count").val(), 10)
		// Values flagged as 'hidden' in the AT schema widget visibility
		// attribute, are flagged so that we know they contain only "default"
		// values, and do not constitute data entry. To avoid confusion with
		// other hidden inputs, these have a 'hidden' attribute on their td.
		$.each($('td[arnum][hidden] input[type="hidden"]'),
			   function (i, e) {
				   var arnum = $(e).parents("[arnum]").attr("arnum")
				   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
				   var value = $(e).attr("uid")
					   ? $(e).attr("uid")
					   : $(e).val()
				   if (fieldname) {
					   state_set(arnum, fieldname, value)
					   // We transfer a _hidden value to hint at the python, too
					   state_set(arnum, fieldname + "_hidden", true)
				   }
			   })
		// other field values which are handled similarly:
		$.each($('td[arnum] input[type="text"], td[arnum] input.referencewidget'),
			   function (i, e) {
				   var arnum = $(e).parents("[arnum]").attr("arnum")
				   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
				   var value = $(e).attr("uid")
					   ? $(e).attr("uid")
					   : $(e).val()
				   state_set(arnum, fieldname, value)
			   })
		// checkboxes inside ar_add_widget table.
		$.each($('[ar_add_ar_widget] input[type="checkbox"]'),
			   function (i, e) {
				   var arnum = $(e).parents("[arnum]").attr("arnum")
				   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
				   var value = $(e).prop('checked')
				   state_set(arnum, fieldname, value)
			   })
		// select widget values
		$.each($('select'),
			   function (i, e) {
				   var arnum = $(e).parents("[arnum]").attr("arnum")
				   var fieldname = $(e).parents("[fieldname]").attr("fieldname")
				   var value = $(e).val()
				   state_set(arnum, fieldname, value)
			   })
		// services
		var uid, arnum, services
		for (arnum = 0; arnum < nr_ars; arnum++) {
			services = [] // list of UIDs
			$.each($('.service_selector td[arnum="' + arnum + '"] input[type="checkbox"]').filter(":checked"),
				   function (i, e) {
					   uid = $(e).parents("[uid]").attr("uid")
					   services.push(uid)
				   })
			state_set(arnum, "Analyses", services)
		}
		// ResultsRange + specifications from UI
		var rr, specs, min, max, error
		for (arnum = 0; arnum < nr_ars; arnum++) {
			rr = bika.lims.ar_add.state[arnum]['ResultsRange']
			if (rr != undefined) {
				specs = hashes_to_hash(rr, 'uid')
				$.each($('.service_selector td[arnum="' + arnum + '"] .after'),
					   function (i, e) {
						   uid = $(e).parents("[uid]").attr("uid")
						   var keyword = $(e).parents("[keyword]").attr("keyword")
						   if (uid != "new" && uid != undefined) {
							   min = $(e).find(".min")
							   max = $(e).find(".max")
							   error = $(e).find(".error")
							   if (specs[uid] == undefined) {
								   specs[uid] = {
									   'min': $(min).val(),
									   'max': $(max).val(),
									   'error': $(error).val(),
									   'uid': uid,
									   'keyword': keyword
								   }
							   }
							   else {
								   specs[uid].min = $(min)
									   ? $(min).val()
									   : specs[uid].min
								   specs[uid].max = $(max)
									   ? $(max).val()
									   : specs[uid].max
								   specs[uid].error = $(error)
									   ? $(error).val()
									   : specs[uid].error
							   }
						   }
					   })
				state_set(arnum, "ResultsRange", hash_to_hashes(specs))
			}
		}
	}

	function check_state_for_errors() {
		console.log("ok")
	}

	function form_submit() {
		$("[name='save_button']").click(function (event) {
			event.preventDefault()
			set_state_from_form_values()
			check_state_for_errors()
			var request_data = {
				_authenticator: $("input[name='_authenticator']").val(),
				state: $.toJSON(bika.lims.ar_add.state)
			}
			$.ajax({
					   type: "POST",
					   dataType: "json",
					   url: window.location.href.split("/portal_factory")[0] + "/analysisrequest_submit",
					   data: request_data,
					   success: function (data) {
					   }
				   });
		})
	}


}

//
//	function copybutton_click() {
//		$(".copyButton").live("click", copyButton)
//	}
//
//	function copyButton() {
//		/* Anything that can be copied from columnn1 across all columns
//		 *
//		 * This function triggers a 'change' event on all elements into
//		 * which values are copied
//		 */
//		var fieldName = $(this).attr("name")
//		var ar_count = parseInt($("#ar_count").val(), 10)
//
//		// Checkboxes
//		var element = $("td[arnum='0']").find("[fieldName='" + fieldName + "']")
//		if ($(element).attr("type") == "checkbox") {
//			var src_val = $(element).prop("checked")
//			// arnum starts at 1 here
//			// we don't copy into the the first row
//			for (var arnum = 1; arnum < ar_count; arnum++) {
//				var dst_elem = $("#ar_" + arnum + "_" + fieldName)
//				src_val = src_val ? true : false
//				if ((dst_elem.prop("checked") != src_val)) {
//					if (!src_val) {
//						dst_elem.removeAttr("checked")
//					}
//					else {
//						dst_elem.attr("checked", true)
//					}
//					// Trigger change like we promised
//					dst_elem.trigger("change")
//				}
//			}
//		}
//
//		// Handle Reference fields
//		else if ($("input[name^='ar\\.0\\." + fieldName + "']").attr("type") == "checkbox") {
//			var src_elem = $("input[name^='ar\\.0\\." + fieldName + "']")
//			var src_val = $(src_elem).filter("[type=text]").val()
//			var src_uid = $("input[name^='ar\\.0\\." + fieldName + "_uid']").val()
//			/***
//			 * Multiple-select references have no "input" for the list of selected items.
//			 * Instead we just copy the entire html over from the first column.
//			 */
//			var src_multi_html = $("div[name^='ar\\.0\\." + fieldName + "-listing']").html()
//			// arnum starts at 1 here
//			for (var arnum = 1; arnum < ar_count; arnum++) {
//				// If referencefield is single-select: copy the UID
//				var dst_uid_elem = $("#ar_" + arnum + "_" + fieldName + "_uid")
//				if (src_uid !== undefined && src_uid !== null) {
//					dst_uid_elem.val(src_uid)
//				}
//				// If referencefield is multi-selet: copy list of selected UIDs:
//				var dst_multi_div = $("div[name^='ar\\." + arnum + "\\." + fieldName + "-listing']")
//				if (src_multi_html !== undefined && src_multi_html !== null) {
//					dst_multi_div.html(
//						src_multi_html
//							.replace(".0.", "." + arnum + ".")
//							.replace("_0_", "_" + arnum + "_")
//					)
//				}
//				var dst_elem = $("#ar_" + arnum + "_" + fieldName)
//				if (dst_elem.prop("disabled")) break
//				// skip_referencewidget_lookup: a little cheat.
//				// it prevents this widget from falling over itself,
//				// by allowing other JS to request that the "selected" action
//				// is not triggered.
//				$(dst_elem).attr("skip_referencewidget_lookup", true)
//				// Now transfer the source value into the destination field:
//				dst_elem.val(src_val)
//
//				// And trigger change like we promised.
//				dst_elem.trigger("change")
//
//				/***
//				 * Now a bunch of custom stuff we need to run for specific
//				 * fields.
//				 *
//				 * we should handle this better if we called "selected" or
//				 * "changed" as the case may be for Reference widgets
//				 * if (fieldName == "Contact") {
//				 * 		.cc_contacts_set(arnum)
//				 * }
//				 * if (fieldName == "Profile") {
//				 * 	$("#ar_" + arnum + "_Template").val("")
//				 * 	profile_set(arnum, src_val)
//				 * 		.then(calculate_parts(arnum))
//				 * }
//				 * if (fieldName == "Template") {
//				 * 	template_set(arnum, src_val)
//				 * 		.then(partition_indicators_set(arnum, false))
//				 * }
//				 * if (fieldName == "SampleType") {
//				 * 	$("#ar_" + arnum + "_Template").val("")
//				 * 	partition_indicators_set(arnum)
//				 * 	specification_refetch(arnum)
//				 * }
//				 * if (fieldName == "Specification") {
//				 * 	specification_refetch(arnum)
//				 * }
//				 * console.log in all these, then delete this when they fire and
//				 * work correctly.
//				 */
//			}
//		}
//	}
//
//
//
//
//
//
//
//
//	function sample_selected() {
//		var arnum = $(this).parents('td').attr('arnum')
//		// Selected a sample to create a secondary AR.
//		$("[id*='_Sample']").live('selected', function (event, item) {
//			// var e = $("input[name^='ar\\."+arnum+"\\."+fieldName+"']")
//			// var Sample = $("input9[name^='ar\\."+arnum+"\\."+fieldName+"']").val()
//			// var Sample_uid = $("input[name^='ar\\."+arnum+"\\."+fieldName+"_uid']").val()
//			// Install the handler which will undo the changes I am about to make
//			$(this).blur(function () {
//				if ($(this).val() === "") {
//					// clear and un-disable everything
//					var disabled_elements = $("[arnum][fieldName] [id*='ar_" + arnum + "']:disabled")
//					$.each(disabled_elements,
//						   function (x, disabled_element) {
//							   $(disabled_element).prop("disabled", false)
//							   if ($(disabled_element).attr("type") == "checkbox")
//								   $(disabled_element).removevAttr("checked")
//							   else
//								   $(disabled_element).val("")
//						   })
//				}
//			})
//			// Then populate and disable sample fields
//			$.getJSON(window.location.href.replace("/ar_add",
//												   "") + "/secondary_ar_sample_info",
//					  {
//						  "Sample_uid": $(this).attr("uid"),
//						  "_authenticator": $("input[name='_authenticator']").val()
//					  },
//					  function (data) {
//						  for (var x = data.length - 1; x >= 0; x--) {
//							  var fieldName = data[x][0]
//							  var fieldvalue = data[x][1]
//							  var uid_element = $("#ar_" + arnum + "_" + fieldName + "_uid")
//							  $(uid_element).val("")
//							  var sample_element = $("#ar_" + arnum + "_" + fieldName)
//							  $(sample_element).val("").prop("disabled",
//															 true)
//							  if ($(sample_element).attr("type") == "checkbox" && fieldvalue) {
//								  $(sample_element).attr("checked", true)
//							  }
//							  else {
//								  $(sample_element).val(fieldvalue)
//							  }
//						  }
//					  }
//			)
//		})
//	}
//
//
//
//
//
//
//
//
