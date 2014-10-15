/**
 * Controller class for AnalysisRequestAddView
 */
function AnalysisRequestAddView() {

	var that = this

	that.load = function () {

		$('input[type=text]').prop('autocomplete', 'off')

		initialize_state()
		rename_conflicted_elements()

		referencewidget_selected()
		contact_selected()

	}

	function initialize_state() {
		bika.lims.ar_add = {}
		bika.lims.ar_add.analysisrequests = {}
		for (var arnum = 0; arnum < $('input[id="ar_count"]').val(); arnum++) {
			bika.lims.ar_add.analysisrequests[arnum] = {}
		}
	}

	function set_state(arnum, fieldname, value) {
		bika.lims.ar_add.analysisrequests[arnum][fieldname] = value
	}

	function rename_conflicted_elements() {
		// Multiple AT widgets may be rendered for each field.
		// rename them here, so their IDs and names do not conflict.
		var i, element, elements, arnum, name
		elements = $("td[ar_add_ar_widget]").find("input[type!='hidden']").not("[disabled]")
		for (i = elements.length - 1; i >= 0; i--) {
			element = elements[i]
			arnum = $($(element).parents("td")).attr("arnum")
			name = $(element).attr("name")
			$(element).attr("name", "ar." + arnum + "." + name)
			$(element).attr("id", "ar_" + arnum + "_" + element.id)
			$(element).removeAttr("required")
		}
		elements = $("td[ar_add_ar_widget]").find("input[type='hidden']")
		for (i = elements.length - 1; i >= 0; i--) {
			element = elements[i]
			arnum = $($(element).parents("td")).attr("arnum")
			name = $(element).attr("name")
			$(element).attr("id", "ar_" + arnum + "_" + element.id)
			$(element).attr("name", "ar." + arnum + "." + name)
		}
		elements = $(".multiValued-listing")
		for (i = elements.length - 1; i >= 0; i--) {
			element = elements[i]
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
			arnum = $($(element).parents("td")).attr("arnum")
			name = $(element).attr("name")
			$(element).attr("id", "ar_" + arnum + "_" + element.id)
			$(element).attr("name", "ar." + arnum + "." + name)
		}
	}


	function referencewidget_selected() {
		// selected handler and state change for referencewidget
		$.each($('.referencewidget'), function (i, element) {
			var arnum = $(element).parents('td').attr('arnum')
			var fieldname = element.id
			$(element).live('selected', function () {
				var td = $(element).parents('td')
				var uid = $(td).find('[id*="' + fieldname + '_uid"]').val()
				set_state(arnum, fieldname, uid)
			})
		})
	}

	function contact_selected() {
		$('[id*="_Contact"]').live('selected', function () {
			var arnum = $(this).parents('td').attr('arnum')
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
						var del_btn = "<img class='ar_deletebtn' src='" + del_btn_src + "' fieldName='" + fieldName + "' uid='" + uid + "'/>"
						var new_item = "<div class='reference_multi_item' uid='" + uid + "'>" + del_btn + title + "</div>"
						$("#ar_" + arnum + "_CCContact-listing").append($(new_item))
					}
				})
			}
		})
	}

}
