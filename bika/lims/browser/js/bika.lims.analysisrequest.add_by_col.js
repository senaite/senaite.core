/* Controller class for AnalysisRequestAddView - column layout.
 *
 * This form is completely customisable, without regard to what the submit
 * handler expects to receive.  The interface between the form and the submit
 * handler is the state variable, stored in bika.lims.ar_add.state.  In this
 * particular form, have bound the submit button handler to first invoke
 * set_state_from_form_values, which compiles the correct state variable
 * and flags errors before the submission is permitted. The state variable is
 * submitted as a json string, and is required to be uniform between all the
 * different ar_add forms.
 *
 * JQuery recommends using .prop("checked") for checkboxes, but selenium/xpath
 * cannot discover the state of such inputs.  I use .attr("checked",true)
 * and .removeAttr("checked") here, although .prop("checked") is still the
 * correct way to check state of a particular element from JS.
 *
 * Do not edit the state variable directly unless you know what you are doing.
 * In these cases, remember to place comments.  In all other cases, this should
 * be handled by the generic element setters below, by set_state, or by the
 * set_state_from_form_values() function called from the submit handlers
 *
 */
function AnalysisRequestAddByCol() {

	var that = this

	that.load = function () {

		$('input[type=text]').prop('autocomplete', 'off')

		state_init()
		form_init()

		/* widgets with generic state-setting handlers
		 * We must keep the state variable up-to-date enough for the UI to respond
		 * correctly to changes, even though we will re-populate the state when
		 * the form is submitted.
		 */
		checkbox_change()        // does not apply to analysisservice selectors
		referencewidget_change() // does not apply to #singleservice
		selectelement_change()
		textinput_change()

		/* These widgets require special UI handling when they are acted on.
		 * The simple state-setting functions above are invoked from within most
		 * of these functions, to keep the state up-to-date while the form is live.
		 */
		client_selected()
		contact_selected()
		copybutton_click()
		profile_selected()
		sample_selected()
		samplepoint_selected()
		sampletype_selected()
		specification_field_entered()
		specification_selected()
		template_selected()
		analysis_cb_click()                     // also select-all checkboxes
		singleservice_dropdown_item_selected()  // single-service selector
		singleservice_deletebtn_click()

		form_submit()
	}

	// initialisation and utils  ///////////////////////////////////////////////

	function state_init() {
		/***
		 * Create the empty state variable.
		 */
		bika.lims.ar_add = {}
		bika.lims.ar_add.state = {}
		var nr_ars = parseInt($('input[id="ar_count"]').val(), 10)
		for (var arnum = 0; arnum < nr_ars; arnum++) {
			bika.lims.ar_add.state[arnum] = {}
		}
	}

	function state_set(arnum, fieldname, value) {
		/***
		 * Use this function to set values in the state variable.
		 */
		var arnum_i = parseInt(arnum, 10)
		if (value != undefined) {
			bika.lims.ar_add.state[arnum_i][fieldname] = value
		}
	}

	function set_state_from_form_values() {
		var nr_ars = parseInt($("#ar_count").val(), 10)
		// hidden values are flagged as such so that the handler knows they
		// contain "default" values, and do not constitute data "entry"
		// to avoid confusion with other hidden inputs, these have a 'hidden'
		// attribute on the TD element.
		$.each($('td[arnum][hidden] input[type="hidden"]'),
			   function (i, e) {
				   var td = $(e).parents('td')
				   var arnum = $(td).attr('arnum')
				   var name = $(e).attr('fieldname') ? $(e).attr('fieldname') : $(e).attr('name')
				   var value = $(e).attr("uid") ? $(e).attr("uid") : $(e).val()
				   state_set(arnum, name, value)
				   state_set(arnum, name+"_hidden", true)
			   })
		// other field values which are handled similarly:
		$.each($('td[arnum] input[type="text"], td[arnum] input.referencewidget'),
			   function (i, e) {
				   var td = $(e).parents('td')
				   var arnum = $(td).attr('arnum')
				   var name = $(e).attr('fieldname') ? $(e).attr('fieldname') : $(e).attr('name')
				   var value = $(e).attr("uid") ? $(e).attr("uid") : $(e).val()
				   state_set(arnum, name, value)
			   })
		// checkboxes inside ar_add_widget table.
		$.each($('[ar_add_ar_widget] input[type="checkbox"]'),
			   function (i, e) {
				   var arnum = $(e).parents("[arnum]").attr('arnum')
				   var fieldname = $(e).attr('fieldname')
				   var value = $(e).prop('checked')
				   state_set(arnum, fieldname, value)
			   })
		// select widget values
		$.each($('select'),
			   function (i, e) {
				   var td = $(e).parents('td')
				   var arnum = $(e).parents('td').attr('arnum')
				   var fieldname = $(e).attr('fieldname')
				   if (!fieldname)
					   fieldname = e.id
				   var instr = '#ar_' + arnum + '_' + fieldname
				   var value = $(td).find(instr).val()
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
			state_set(arnum, "services", services)
		}
		// ResultsRange + specifications from UI
		var rr, specs, min, max, error
		for (arnum = 0; arnum < nr_ars; arnum++) {
			rr = bika.lims.ar_add.state[arnum].ResultsRange
			if (rr != undefined) {
				specs = hashes_to_hash(rr, 'uid')
				$.each($('.service_selector td[arnum="' + arnum + '"] .after'),
					   function (i, e) {
						   uid = $(e).parents("[uid]").attr("uid")
						   keyword = $(e).parents("[keyword]").attr("keyword")
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
								   specs[uid].min = $(min) ? $(min).val() : specs[uid].min
								   specs[uid].max = $(max) ? $(max).val() : specs[uid].max
								   specs[uid].error = $(error) ? $(error).val() : specs[uid].error
							   }
						   }
					   })
				state_set(arnum, "ResultsRange", hash_to_hashes(specs))
			}
		}
	}

	function form_init() {
		/***
		 * Form load tasks.
		 *
		 * - Rename widgets in each column. Multiple AT widgets may be
		 *   rendered for each field. Rename them here, so their IDs and
		 *   names do not conflict.  We use name= and id=, but the values
		 *   in these inputs are not submitted.
		 *
		 * - Show only the data (contacts, templates, etc.) for the selected
		 *   client.   This is the initial filter, but the filters are
		 *   re-applied each time a Client field is modified.
		 */
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
			// '.' format for both name= and id=.  Is this/This is correct.
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

		// When the page is reloaded by the browser, we must clear things
		// that may still be set
		$("#singleservice").val("").attr("uid", "new").attr("keyword", "")
		$("#singleservice").parents("[uid]").attr("uid", "new")
		$("input[type='checkbox']").removeAttr("checked")
		$(".min,.max,.error").val("")

		// filter_by_client
		setTimeout(function () {
			var nr_ars = parseInt($("#ar_count").val(), 10)
			for (arnum = 0; arnum < nr_ars; arnum++) {
				filter_by_client(arnum)
			}
		}, 250)

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
						   debugger
					   }
				   });
		})
	}

	function show_partitions() {
		/* Return true if bika_setup/getShowPartitions() is True.
		 */
		return $("bika_setup").attr("ShowPartitions") == "true"
	}

	function ar_specs_enabled() {
		/* Return true if bika_setup/getEnableARSpecs() is True.
		 */
		if ($("bika_setup").attr("EnableARSpecs")) {
			return true
		}
		else {
			return false
		}
	}

	function filter_combogrid(element, filterkey, filtervalue) {
		/***
		 * Apply or modify a query filter for a reference widget.
		 *
		 *  This will set the options, then re-create the combogrid widget
		 *  with the new filter key/value set in base_query.
		 */
		if (!$(element).is(':visible')) return
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
		/***
		 * Filter all Reference fields that reference Client items
		 *
		 * Some reference fields can select Lab or Client items.  In these
		 * cases, the 'getParentUID' or 'getClientUID' index is used
		 * to filter against Lab and Client folders.
		 */
		var clientuid = $("td[arnum='" + arnum + "'] [fieldName='Client']").attr("uid")
		filter_combogrid(
			$("#ar_" + arnum + "_Contact"),
			"getParentUID", clientuid)
		filter_combogrid(
			$("#ar_" + arnum + "_CCContact"),
			"getParentUID", clientuid)
		filter_combogrid(
			$("#ar_" + arnum + "_InvoiceContact"),
			"getParentUID", clientuid)
		filter_combogrid(
			$("#ar_" + arnum + "_SamplePoint"),
			"getClientUID",
			[clientuid, $("#bika_setup").attr("bika_samplepoints_uid")])
		filter_combogrid(
			$("#ar_" + arnum + "_Template"),
			"getClientUID",
			[clientuid, $("#bika_setup").attr("bika_artemplates_uid")])
		filter_combogrid(
			$("#ar_" + arnum + "_Profile"), "getClientUID",
			[clientuid, $("#bika_setup").attr("bika_analysisprofiles_uid")])
		filter_combogrid(
			$("#ar_" + arnum + "_Specification"),
			"getClientUID",
			[clientuid, $("#bika_setup").attr("bika_analysisspecs_uid")])
	}


	function hashes_to_hash(hashlist, key) {
		/***
		 * Convert a list of hashes to a hash, by one of their keys.
		 *
		 * This will return a single hash: the key that will be used MUST
		 * exist in all hashes in hashlist.
		 */
		var ret = {}
		for (var i = 0; i < hashlist.length; i++)
			ret[hashlist[i][key]] = hashlist[i]
		return ret
	}

	function hash_to_hashes(hash) {
		/***
		 * Convert a single hash into a list of hashes
		 *
		 * Basically, this just returns the keys, unmodified.
		 */
		var ret = []
		$.each(hash, function (i, v) {
			ret.push(v)
		})
		return ret
	}

	function analysis_unset_all(arnum) {
		/***
		 *
		 */
		var analyses = $('td.ar\\.' + arnum).find("[type='checkbox']")
		for (var i = 0; i < analyses.length; i++) {
			$(analyses[i]).removeAttr("checked")
			if (show_partitions()) {
				$(analyses[i]).next(".after").children(".partnr").empty()
			}
		}
	}

	// Event handlers //////////////////////////////////////////////////////////

	function checkbox_change() {
		/***
		 * Handler and state change for checkboxes
		 *
		 * The checkboxes used to select analyses are handled separately.
		 */
		var e = $('[ar_add_ar_widget] input[type="checkbox"]')
		$(e).live('change', function () {
			var arnum = $(this).parents('td').attr('arnum')
			var fieldname = $(this).attr('fieldname')
			var input = 'input[id="ar_' + arnum + '_' + fieldname + '"]'
			var value = $(this).parents('td').find(input).val()
			state_set(arnum, fieldname, value)
		})
	}

	function referencewidget_change() {
		/***
		 * Handler and state change for all combogrids
		 *
		 * Save Reference fields into the state If set, they have an extra
		 * hidden field, *_uid, which also gets saved into the state
		 */
		$('.referencewidget')
			.not("#singleservice")
			.live('selected', function (event, item) {
					  referencewidget_change_handler(this)
				  })
	}

	function referencewidget_change_handler(element) {
		var arnum = $(element).parents('td').attr('arnum')
		var fieldname = $(element).attr('fieldname')
		if (!fieldname) fieldname = element.id
		var td = $(element).parents('td')
		var id = 'ar_' + arnum + '_' + fieldname
		var value = $(td).find('input[id="' + id + '"]').val()
		var uid = $(td).find('[id*="' + id + '_uid"]').val()
		state_set(arnum, fieldname, value)
		state_set(arnum, fieldname + "_uid", uid)
	}

	function selectelement_change() {
		/***
		 * Handler and state change for all <select> widgets
		 *
		 * Get the value of the selected option, and stick it in state.
		 */
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

	function textinput_change() {
		/***
		 * Handler and state change for text <inputs>
		 *
		 *  Plainly put text input values into their fields in state.
		 *  Specifically ignore the following which are handled elsewhere:
		 *      #singleservice
		 */
		$('input[type="text"]')
			.not("#singleservice")
			.live('change', function () {
					  var fieldname = $(this).attr('fieldname')
					  var td = $(this).parents('td')
					  var arnum = $(this).parents('td').attr('arnum')
					  if (!fieldname) fieldname = this.id
					  var instr = 'input[id="ar_' + arnum + '_' + fieldname + '"]'
					  var value = $(td).find(instr).val()
					  state_set(arnum, fieldname, value)
				  })
	}

	function client_selected() {
		/***
		 * A client was selected
		 *
		 * Now we must filter any references that search inside the Client.
		 */
		$("[id*='_Client']").live('selected', function (event, item) {
			var arnum = $(this).parents('td').attr('arnum')
			filter_by_client(arnum)
			referencewidget_change_handler(this)
		})
	}

	function cc_contacts_set(arnum) {
		/***
		 * Setting the CC Contacts after a Contact was set
		 *
		 * Contact.CCContact may contain a list of Contact references.
		 * So we need to select them in the form with some fakey html,
		 * and set them in the state.
		 */
		// Update the multiselect CCContacts referencewidget,
		// to match Contact->CCContacts value.
		var contact_uid = $("#ar_" + arnum + "_Contact_uid").val()
		var fieldName = "ar." + arnum + ".CCContact"
		// clear the CC widget
		$("input[name*='" + fieldName + "']").val('').attr('uid', '')
		$('input[name="' + fieldName + '_uid"]').val('')
		$("#ar\\." + arnum + "\\.CCContact-listing").empty()
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
		/***
		 * Selected a Contact: trigger CC Contacts
		 */
		$('[id*="_Contact"]').live('selected', function (event, item) {
			var arnum = $(this).parents('td').attr('arnum')
			cc_contacts_set(arnum)
			referencewidget_change_handler(this)
		})
	}

	function copybutton_click() {
		$(".copyButton").live("click", copyButton)
	}

	function copyButton() {
		/***
		 * Anything that can be copied from columnn1 across all columns
		 *
		 * This function triggers a 'change' event on all elements into
		 * which values are copied
		 */
		var fieldName = $(this).attr("name")
		var ar_count = parseInt($("#ar_count").val(), 10)

		// Checkbox are mostly all handled the same way.
		// This does not include the checkboxes used to select analyses
		if ($("input[name^='ar\\.0\\." + fieldName + "']").attr("type") == "checkbox") {
			var src_element = $("input[name^='ar\\.0\\." + fieldName + "']")
			var src_val = $(src_element).prop("checked")
			var ar_count = parseInt($("#ar_count").val(), 10)
			// arnum starts at 1 here
			// we don't copy into the the first row
			for (var arnum = 1; arnum < ar_count; arnum++) {
				var dst_elem = $("#ar_" + arnum + "_" + fieldName)
				src_val = src_val ? true : false
				if ((dst_elem.prop("checked") != src_val)) {
					if (!src_val) {
						dst_elem.removeAttr("checked")
					}
					else {
						dst_elem.attr("checked", true)
					}
					// Trigger change like we promised
					dst_elem.trigger("change")
				}
			}
		}

		// Handle Reference fields
		else if ($("input[name^='ar\\.0\\." + fieldName + "']").attr("type") == "checkbox") {
			var src_elem = $("input[name^='ar\\.0\\." + fieldName + "']")
			var src_val = $(src_elem).filter("[type=text]").val()
			var src_uid = $("input[name^='ar\\.0\\." + fieldName + "_uid']").val()
			/***
			 * Multiple-select references have no "input" for the list of selected items.
			 * Instead we just copy the entire html over from the first column.
			 */
			var src_multi_html = $("div[name^='ar\\.0\\." + fieldName + "-listing']").html()
			// arnum starts at 1 here
			for (var arnum = 1; arnum < ar_count; arnum++) {
				// If referencefield is single-select: copy the UID
				var dst_uid_elem = $("#ar_" + arnum + "_" + fieldName + "_uid")
				if (src_uid !== undefined && src_uid !== null) {
					dst_uid_elem.val(src_uid)
				}
				// If referencefield is multi-selet: copy list of selected UIDs:
				var dst_multi_div = $("div[name^='ar\\." + arnum + "\\." + fieldName + "-listing']")
				if (src_multi_html !== undefined && src_multi_html !== null) {
					dst_multi_div.html(
						src_multi_html
							.replace(".0.", "." + arnum + ".")
							.replace("_0_", "_" + arnum + "_")
					)
				}
				var dst_elem = $("#ar_" + arnum + "_" + fieldName)
				if (dst_elem.prop("disabled")) break
				// skip_referencewidget_lookup: a little cheat.
				// it prevents this widget from falling over itself,
				// by allowing other JS to request that the "selected" action
				// is not triggered.
				$(dst_elem).attr("skip_referencewidget_lookup", true)
				// Now transfer the source value into the destination field:
				dst_elem.val(src_val)

				// And trigger change like we promised.
				dst_elem.trigger("change")

				/***
				 * Now a bunch of custom stuff we need to run for specific
				 * fields.
				 *
				 * we should handle this better if we called "selected" or
				 * "changed" as the case may be for Reference widgets
				 * if (fieldName == "Contact") {
				 * 		.cc_contacts_set(arnum)
				 * }
				 * if (fieldName == "Profile") {
				 * 	$("#ar_" + arnum + "_Template").val("")
				 * 	profile_set(arnum, src_val)
				 * 		.then(calculate_parts(arnum))
				 * }
				 * if (fieldName == "Template") {
				 * 	template_set(arnum, src_val)
				 * 		.then(partition_indicators_set(arnum, false))
				 * }
				 * if (fieldName == "SampleType") {
				 * 	$("#ar_" + arnum + "_Template").val("")
				 * 	partition_indicators_set(arnum)
				 * 	specification_refetch(arnum)
				 * }
				 * if (fieldName == "Specification") {
				 * 	specification_refetch(arnum)
				 * }
				 * console.log in all these, then delete this when they fire and
				 * work correctly.
				 */
			}
		}
	}

	function filter_spec_by_sampletype(arnum) {
		/***
		 * Possibly filter the Specification dropdown when SampleType selected
		 *
		 * when a SampleType is selected I will allow only specs to be
		 * selected which have a matching SampleType value, or which
		 * have no sampletype set.
		 */
		arnum_i = parseInt(arnum, 10)
		var sampletype_uid = bika.lims.ar_add.state[arnum_i]['SampleType_uid']
		var spec_element = $("#ar_" + arnum + "_Specification")
		var query_str = $(spec_element).attr("search_query")
		var query = $.parseJSON(query_str)
		if (query.hasOwnProperty("getSampleTypeUID")) {
			delete query.getSampleTypeUID
		}
		query.getSampleTypeUID = [encodeURIComponent(sampletype_uid), ""]
		query_str = $.toJSON(query)
		$(spec_element).attr("search_query", query_str)
	}

	function specification_refetch(arnum) {
		/***
		 * Lookup the selected specification with ajax, then set all
		 * min/max/error fields in all columns to match.
		 *
		 * If the specification does not define values for a particular service,
		 * the form values will not be cleared.
		 *
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
			var state = bika.lims.ar_add.state[arnum]
			var hashlist = state.ResultsRange
			if (hashlist != undefined) {
				var spec = hashes_to_hash(hashlist, 'uid')
				$.each($("td[arnum='" + arnum + "']"), function (i, td) {
					var uid = $(td).parents("[uid]").attr("uid")
					if (uid != "new" && uid != undefined && uid in spec) {
						var min = $(td).find(".min")
						var max = $(td).find(".max")
						var error = $(td).find(".error")
						$(min).val(spec[uid].min)
						$(max).val(spec[uid].max)
						$(error).val(spec[uid].error)
					}
				})
			}
		}
	}

	function specification_set_from_sampletype(arnum) {
		/***
		 * Look for Specifications with the selected SampleType.
		 *
		 * If a specification is found:
		 *
		 * 1) Set the value of the Specification field
		 * 2) Fetch the spec from the server, and set all the spec field values
		 * 3) Set the partition indicator numbers.
		 */
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
				specification_refetch(arnum)
				partition_indicators_set(arnum)
			}
		})
	}

	function specification_field_entered() {
		/***
		 * Validate entry into min/max/error fields, and save them
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
				if (isNaN(min))
					$(min_element).val("")
				else if ((!isNaN(max)) && min > max)
					$(max_element).val("")
			}
			else if ($(this).hasClass("max")) {
				if (isNaN(max))
					$(max_element).val("")
				else if ((!isNaN(min)) && max < min)
					$(min_element).val("")
			}
			else if ($(this).hasClass("error")) {
				if (isNaN(error) || error < 0 || error > 100)
					$(error_element).val("")
			}

			arnum_i = parseInt(arnum, 10)
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

	function specification_selected() {
		/***
		 * Selected a Specification - invoke the fetch/update function
		 */
		$("[id*='_Specification']").live('selected', function (event, item) {
			var arnum = $(this).parents('td').attr('arnum')
			specification_refetch(arnum)
		})
	}

	function samplepoint_selected() {
		$("[id*='_SamplePoint']").live('selected', function(event, item){
			arnum = $(this).parents("[arnum]").attr("arnum")
			samplepoint_set(arnum)
		})
	}

	function sampletype_selected() {
		$("[id*='_SampleType']").live('selected', function (event, item) {
			arnum = $(this).parents("[arnum]").attr("arnum")
			sampletype_set(arnum)
		})
	}

	function samplepoint_set(arnum) {
		/***
		 * Sample point and Sample type can set each other.
		 */
		var arnum = $(this).parents('td').attr('arnum')
		var sp_element = $("#ar_" + arnum + "_SampleType")
		filter_combogrid(sp_element, "getSamplePointTitle", $(this).val())
	}

	function sampletype_set(arnum) {
		/***
		 * Sample point and Sample type can set each other.
		 */
		var arnum = $(this).parents('td').attr('arnum')
		var sp_element = $("#ar_" + arnum + "_SamplePoint")
		var st_element = $("#ar_" + arnum + "_SampleType")
		filter_combogrid(sp_element, "getSampleTypeTitle", $(this).val())
		specification_set_from_sampletype(arnum)
		partition_indicators_set(arnum)
	}

	function profile_selected() {
		/*** A profile is selected.
		 *
		 * - Set the profile's analyses (existing analyses will be cleared)
		 * - Set the partition number indicators
		 */
		$("[id*='_Profile']").live('selected', function (event, item) {
			var arnum = $(this).parents('td').attr('arnum')
			profile_set(arnum, $(this).val())
				.then(function () {
						  specification_apply()
						  partition_indicators_calculate()
					  })
		})
	}

	function profile_set(arnum, profile_title) {
		/*** Set the profile analyses for the AR in this column.
		 *
		 *  Set the analyses specified in the  profile.
		 *
		 *  This will clear  analyses in this AR column, and it will
		 *  also clear the AR Template field.
		 */
		template_unset(arnum)
		var d = $.Deferred()
		var request_data = {
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

	function template_selected() {
		$("[id*='_Template']").live('selected', function (event, item) {
			var arnum = $(this).parents('td').attr('arnum')
			template_set(arnum, $(this).val())
				.then(function () {
						  specification_refetch(arnum)
						  partition_indicators_calculate()
					  })
		})
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
			if (!template['reportdrymatter']) {
				$("#ar_" + arnum + "_reportdrymatter").removeAttr("checked")
			}
			else {
				$("#ar_" + arnum + "_reportdrymatter").attr("checked", true)
			}
			specification_set_from_sampletype(arnum)

			// Set the ARTemplate's AnalysisProfile
			if (template['AnalysisProfile']) {
				$("#ar_" + arnum + "_Profile").val(template['AnalysisProfile'])
				$("#ar_" + arnum + "_Profile_uid").val(template['AnalysisProfile_uid'])
				template['AnalysisProfile_uid']
			}
			else {
				$("#ar_" + arnum + "_Profile").val("")
				$("#ar_" + arnum + "_Profile_uid").val("")
			}

			// Set the services from the template into the form
			uncheck_all_services(arnum)
			if ($('#singleservice').length > 0) {
				expand_services_singleservice(arnum, template['service_data'])
			}
			else {
				expand_services_bika_listing(arnum, template['service_data'])
			}

			// munge parts into a hash for easier lookup
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

			partition_indicators_set(arnum, false)

			// prices_update(arnum)

			d.resolve()
		})
		return d.promise()
	}

	function template_unset(arnum) {
		$("#ar_" + arnum + "_Template").val("")
		$("#ar_" + arnum + "_Template_uid").val("")
		state_set(arnum, "Template", "")
		state_set(arnum, "Template_uid", "")
	}


	function uncheck_all_services(arnum) {
		// Remove checkboxes for all existing services in this column
		var cblist = $(".service_selector td[arnum='" + arnum + "'] input[type='checkbox']")
			.filter(":checked")
		for (var i = 0; i < cblist.length; i++) {
			var e = cblist[i]
			var arnum = $(e).parents("[arnum]").attr("arnum")
			var uid = $(e).parents("[uid]").attr("uid")
			analysis_cb_uncheck(arnum, uid)
		}
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

	function expand_services_singleservice(arnum, service_data) {
		// When the single-service serviceselector is in place,
		// this function is called to select services for Profiles and Templates.
		// Select services which are already present
		var uid, keyword, title
		var not_present = []
		var sd = service_data
		for (var i = 0; i < sd.length; i++) {
			uid = sd[i]['UID']
			keyword = sd[i]['Keyword']
			var e = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] input[type='checkbox']")
			e.length > 0 ?
				analysis_cb_check(arnum, sd[i]['UID']) :
				not_present.push(sd[i])
		}
		// Insert services which are not yet present
		for (var i = 0; i < not_present.length; i++) {
			title = not_present[i]['Title']
			uid = not_present[i]['UID']
			var keyword = not_present[i]['Keyword']
			$("#singleservice").val(title)
			$("#singleservice").attr('uid', uid)
			$("#singleservice").attr('keyword', keyword)
			singleservice_dropdown_item_duplicate()
			analysis_cb_check(arnum, uid)
		}
	}

	function sample_selected() {
		var arnum = $(this).parents('td').attr('arnum')
		// Selected a sample to create a secondary AR.
		$("[id*='_Sample']").live('selected', function (event, item) {
			// var e = $("input[name^='ar\\."+arnum+"\\."+fieldName+"']")
			// var Sample = $("input9[name^='ar\\."+arnum+"\\."+fieldName+"']").val()
			// var Sample_uid = $("input[name^='ar\\."+arnum+"\\."+fieldName+"_uid']").val()
			// Install the handler which will undo the changes I am about to make
			$(this).blur(function () {
				if ($(this).val() === "") {
					// clear and un-disable everything
					var disabled_elements = $("[ar_add_ar_widget] [id*='ar_" + arnum + "']:disabled")
					$.each(disabled_elements,
						   function (x, disabled_element) {
							   $(disabled_element).prop("disabled", false)
							   if ($(disabled_element).attr("type") == "checkbox")
								   $(disabled_element).removevAttr("checked")
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
							  $(sample_element).val("").prop("disabled",
															 true)
							  if ($(sample_element).attr("type") == "checkbox" && fieldvalue) {
								  $(sample_element).attr("checked", true)
							  }
							  else {
								  $(sample_element).val(fieldvalue)
							  }
						  }
					  }
			)
		})
	}

	function analysis_cb_check(arnum, uid) {
		/* Called to un-check an Analysis' checkbox as though it were clicked.
		 */
		var cb = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] [type='checkbox']")
		$(cb).attr("checked", true)
		analysis_cb_after_change(arnum, uid)
	}

	function analysis_cb_uncheck(arnum, uid) {
		/* Called to un-check an Analysis' checkbox as though it were clicked.
		 */
		var cb = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] [type='checkbox']")
		$(cb).removeAttr("checked")
		analysis_cb_after_change(arnum, uid)
	}

	function analysis_cb_after_change(arnum, uid) {
		/* If changed by click or by other trigger, all analysis checkboxes
		 * must invoke this function.
		 */
		var cb = $("tr[uid='" + uid + "'] td[arnum='" + arnum + "'] [type='checkbox']")
		var tr = $(cb).parents("tr")
		var checked = $(cb).prop("checked")
		var checkboxes = $(tr)
			.find("input[type=checkbox][name!='uids:list']")
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
		calcdependencies(arnum, [uid])
		partition_indicators_set(arnum)
	}

	function analysis_cb_click() {
		/*
		 * configures handler for click event on analysis checkboxes
		 * and their associated select-all checkboxes.
		 *
		 * As far as possible, the bika_listing and single-select selectors
		 * try to emulate each other's HTML structure in each row.
		 *
		 */
		// regular analysis cb
		$(".service_selector input[type='checkbox'][name!='uids:list']")
			.live('click', function () {
					  arnum = $(this).parents("[arnum]").attr("arnum")
					  uid = $(this).parents("[uid]").attr("uid")
					  analysis_cb_after_change(arnum, uid)
					  // If the click is on "new" row, focus the selector
					  if (uid == "new") {
						  $("#singleservice").focus()
					  }
				  })
		// select-all cb
		$(".service_selector input[type='checkbox'][name='uids:list']")
			.live('click', function () {
					  var tr = $(this).parents("tr")
					  var uid = $(this).parents("[uid]").attr("uid")
					  var checked = $(this).prop("checked")
					  var checkboxes = $(tr)
						  .find("input[type=checkbox][name!='uids:list']")
					  for (var i = 0; i < checkboxes.length; i++) {
						  if (checked) {
							  analysis_cb_check(i, uid)
						  }
						  else {
							  analysis_cb_uncheck(i, uid)
						  }
					  }
					  // If the click is on "new" row, focus the selector
					  if (uid == "new") {
						  $("#singleservice").focus()
					  }
				  })

	}

	function singleservice_dropdown_item_selected() {
		/* Add new table rows when services are added with single-select form.
		 *
		 * :element: #singleservice: the combogrid enabled text input
		 * :event: selected: a vocabulary item is selected.
		 */
		$("#singleservice").live('selected', function (event, item) {
			// Set the 'uid' and 'keyword' attributes on #singleservice
			// we require the _duplicate function to set them on the actual TR.
			$("#singleservice").attr("uid", item.UID)
			$("#singleservice").attr("keyword", item.Keyword)
			singleservice_dropdown_item_duplicate()
		})
	}

	function singleservice_dropdown_item_duplicate() {
		/* After selecting a service from the #singleservice combogrid,
		 * this function is reponsible for duplicating the TR.  This is
		 * factored out so that template, profile etc, can also duplicate
		 * rows.
		 *
		 * This function is also responsible for inserting hidden Pricing
		 * information.  Pricing info is also inserted when Templates or
		 * Profiles are selected.
		 */
		var tr = $("#singleservice").parents("tr")
		// The uid and keyword attributes are set via the 'selected' handler,
		// or manually by the template/profile completion
		var uid = $("#singleservice").attr("uid")
		var keyword = $("#singleservice").attr("keyword")
		// clone tr *before* anything else
		var new_tr = $(tr).clone()
		/* Clobber the old row first, set all it's attributes to look like
		 * a bika_listing version of itself.
		 * The attributes are a little wonky perhaps.  They mimic the
		 * attributes that bika_listing rows get, so that the event handlers
		 * don't have to care:
		 * XXX when bika_listing or bika_listing_table change, this must also change!
		 */
		// set uid on TR element
		$(tr).attr("uid", uid)
		$(tr).attr("keyword", keyword)
		// analyses checkbox attributes
		var analyses = $(tr).find("input[type='checkbox'][name!='uids:list']")
		for (var i = 0; i < analyses.length; i++) {
			$(analyses[i])
				.attr('uid', uid)
				.attr('id', uid + '-ar.' + i)
				.attr('name', 'ar.' + i + '.' + uid)
		}
		// select_all
		$(tr).find("input[name='uds:list']").attr('value', uid)
		// alert containers
		$(tr).find('.alert').attr('uid', uid)
		// Replace the text widget with a label, delete btn etc:
		var service_label = $(
			"<a href='#' class='deletebtn'><img src='" + portal_url +
			"/++resource++bika.lims.images/delete.png' uid='" + uid +
			"' style='vertical-align: -3px;'/></a>&nbsp;" +
			"<span>" + $("#singleservice").val() + "</span>")
		$(tr).find(".ArchetypesReferenceWidget").replaceWith(service_label)
		// Set spec values manually for the row xxxyz
		// Configure and insert new row
		$(new_tr).find("[type='checkbox']").removeAttr("checked")
		$(new_tr).find("[type='text']").val("")
		$(new_tr).find("#singleservice").attr("uid", "new")
		$(new_tr).find("#singleservice").attr("keyword", "")
		$(new_tr).find("#singleservice").removeClass("has_combogrid_widget")
		$(tr).after(new_tr)
		referencewidget_lookups()
		specification_apply()
	}

	function singleservice_deletebtn_click() {
		/*
		 * Remove the service row.
		 */
		$(".service_selector a.deletebtn").live('click', function (event) {
			event.preventDefault()
			$(this).parents("tr[uid]").remove()
		})
	}

	function recalc_prices(arnum) {
		var subtotal = 0.00
		var discount_amount = 0.00
		var vat = 0.00
		var total = 0.00
		var discount_pcnt = parseFloat($("#bika_setup").attr("MemberDiscount"))
		$.each($("input[name='ar." + arnum + ".Analyses:list:ignore_empty:record']"),
			   function () {
				   var disabled = $(this).prop("disabled")
				   // For some browsers, `attr` is undefined; for others, its false.  Check for both.
				   if (typeof disabled !== "undefined" && disabled !== false) {
					   disabled = true
				   }
				   else {
					   disabled = false
				   }
				   var include = (!(disabled) && $(this).prop("checked") && $(this).hasClass('overlay_field'))
				   if (include) {
					   var serviceUID = this.id
					   var form_price = parseFloat($("#" + serviceUID + "_price").val())
					   var vat_amount = parseFloat($("#" + serviceUID + "_price").attr("vat_amount"))
					   var price
					   if (discount_pcnt) {
						   price = form_price - ((form_price / 100) * discount_pcnt)
					   }
					   else {
						   price = form_price
					   }
					   subtotal += price
					   discount_amount += ((form_price / 100) * discount_pcnt)
					   vat += ((price / 100) * vat_amount)
					   total += price + ((price / 100) * vat_amount)
				   }
			   })
		$("#ar_" + arnum + "_subtotal").val(subtotal.toFixed(2))
		$("#ar_" + arnum + "_subtotal_display").val(subtotal.toFixed(2))
		$("#ar_" + arnum + "_discount").val(discount_amount.toFixed(2))
		$("#ar_" + arnum + "_vat").val(vat.toFixed(2))
		$("#ar_" + arnum + "_vat_display").val(vat.toFixed(2))
		$("#ar_" + arnum + "_total").val(total.toFixed(2))
		$("#ar_" + arnum + "_total_display").val(total.toFixed(2))
	}

	function partition_indicators_calculate(arnum) {
		var d = $.Deferred()
		// Configures the state partition data
		arnum_i = parseInt(arnum, 10)
		var state = bika.lims.ar_add.state[arnum_i]

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
		return
		console.log("partition indicators set")
		// set calculate=false to prevent calculateion (eg, setting template)
		if (show_partitions()) {
			$('[id*="-ar.' + arnum + '"]')
				.filter("[type='checkbox']")
				.next(".after")
				.children(".partnr")
				.empty()
		}
		if (calculate != true) {
			partition_indicators_calculate(arnum)
				.done(function () {
						  arnum_i = parseInt(arnum, 10)
						  var parts = bika.lims.ar_add.state[arnum_i]['parts']
						  if (!parts) return
						  for (var pi = 0; pi < parts.length; pi++) {
							  var part_nr = pi + 1;
							  var part = parts[pi];
							  var services = part['services']
							  for (var si = 0; si < services.length; si++) {
								  var uid = services[si];
								  var cb = $("input[id*=ar\\." + arnum + "]")
									  .filter("[uid=" + uid + "]")
								  if ($(cb).prop("checked")) {
									  if (show_partitions()) {
										  $('#' + uid + '-ar\\.' + arnum)
											  .next(".after")
											  .children(".partnr")
											  .empty()
											  .append(part_nr)
									  }
								  }
							  }
						  }
					  })
		}
	}


	function add_Yes(dlg, element, dep_services) {
		for (var i = 0; i < dep_services.length; i++) {
			var service_uid = dep_services[i].Service_uid
			if (!$('#list_cb_' + service_uid).prop('checked')) {
				analysis_cb_check(service_uid)
				$('#list_cb_' + service_uid).attr('checked', true)
			}
		}
		$(dlg).dialog('close')
		$('#messagebox').remove()
	}

	function add_No(dlg, element) {
		if ($(element).prop('checked')) {
			analysis_cb_uncheck($(element).attr('value'))
			$(element).removeAttr('checked')
		}
		$(dlg).dialog('close')
		$('#messagebox').remove()
	}

	function calcdependencies(arnum, uids, auto_yes) {
		return
		auto_yes = auto_yes || false
		jarn.i18n.loadCatalog('bika')
		var _ = window.jarn.i18n.MessageFactory('bika')

		var dep
		var i, e, cb

		var lims = window.bika.lims

		var elements = []
		for (i = 0; i <= uids.length; i++) {
			uid = uids[i]
			e = $(' input[id*=ar\\.' + arnum + ']').filter('[uid=' + uid + ']')
			elements.push(e)
		}

		for (var elements_i = 0; elements_i < elements.length; elements_i++) {
			var dep_services = [];  // actionable services
			var dep_titles = []
			var element = elements[elements_i]
			var service_uid = $(element).attr('value')
			// selecting a service; discover dependencies
			if ($(element).prop('checked')) {
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
							analysis_cb_uncheck(dep.Service_uid)
							$(cb).removeAttr("checked")
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
											$(cb).removeAttr("checked")
											analysis_cb_uncheck(dep.Service_uid)
										}
										$(this).dialog("close")
										$("#messagebox").remove()
									},
									no: function () {
										service_uid = $(element).attr("value")
										analysis_cb_check(service_uid)
										$(element).attr("checked", true)
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

