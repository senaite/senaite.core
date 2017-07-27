/**
 * Controller class for Bika Listing Table view
 */
function BikaListingTableView() {

	var that = this;
	// To keep track if a transitions loading is taking place atm
	var loading_transitions = false;

	// Entry-point method for AnalysisServiceEditView
	that.load = function () {

		column_header_clicked()
		load_transitions();
		select_one_clicked();
		select_all_clicked();
		listing_string_input_keypress()
		listing_string_select_changed()
		pagesize_change()
		category_header_clicked()
		filter_search_keypress()
		filter_search_button_click()
		workflow_action_button_click()
		column_toggle_context_menu()
		column_toggle_context_menu_selection()
		show_more_clicked();
        autosave();
		load_export_buttons();

		$('*').click(function () {
			if ($(".tooltip").length > 0) {
				$(".tooltip").remove()
			}
		})

	}

	function show_more_clicked() {
		$('a.bika_listing_show_more').click(function(e){
			e.preventDefault();
			var formid = $(this).attr('data-form-id');
			var pagesize = parseInt($(this).attr('data-pagesize'));
			var url = $(this).attr('data-ajax-url');
			var limit_from = parseInt($(this).attr('data-limitfrom'));
			url = url.replace('_limit_from=','_olf=');
			url += '&'+formid+"_limit_from="+limit_from;
			$('#'+formid+' a.bika_listing_show_more').fadeOut();
			var tbody = $('table.bika-listing-table[form_id="'+formid+'"] tbody.item-listing-tbody');
			// The results must be filtered?
			var filter_options = [];
			filters1 = $('.bika_listing_filter_bar input[name][value!=""]');
			filters2 = $('.bika_listing_filter_bar select option:selected[value!=""]');
			filters = $.merge(filters1, filters2);
			$(filters).each(function(e) {
				var opt = [$(this).attr('name'), $(this).val()];
				filter_options.push(opt);
			});
			var filterbar = {};
			if (filter_options.length > 0) {
				filterbar.bika_listing_filter_bar = $.toJSON(filter_options);
			}
			$.post(url, filterbar)
				.done(function(data) {
					try {
						// We must surround <tr> inside valid TABLE tags before extracting
						var rows = $('<html><table>'+data+'</table></html>').find('tr')
						// Then we can simply append the rows to existing TBODY.
						$(tbody).append(rows)
						// Increase limit_from so that next iteration uses correct start point
						$('#'+formid+' a.bika_listing_show_more').attr('data-limitfrom', limit_from+pagesize);
						loadNewRemarksEventHandlers();
					}
					catch (e) {
						$('#' + formid + ' a.bika_listing_show_more').hide();
						console.log(e);
					}
					load_transitions();
				}).fail(function () {
					$('#'+formid+' a.bika_listing_show_more').hide();
					console.log("bika_listing_show_more failed");
    		}).always(function() {
					var numitems = $('table.bika-listing-table[form_id="'+formid+'"] tbody.item-listing-tbody tr').length;
					$('#'+formid+' span.number-items').html(numitems);
					if (numitems % pagesize == 0) {
						$('#'+formid+' a.bika_listing_show_more').fadeIn();
					}
				});
		});
	}

	function loadNewRemarksEventHandlers() {
			// Add a baloon icon before Analyses' name when you'd add a remark. If you click on, it'll display remarks textarea.
			$('a.add-remark').remove();
			var txt1 = '<a href="#" class="add-remark"><img src="'+window.portal_url+'/++resource++bika.lims.images/comment_ico.png" title="'+_('Add Remark')+'")"></a>';
			var pointer = $(".listing_remarks:contains('')").closest('tr').prev().find('td.service_title span.before');

			$(pointer).append(txt1);

			$("a.add-remark").click(function(e){
					e.preventDefault();
					var rmks = $(this).closest('tr').next('tr').find('td.remarks');
					if (rmks.length > 0) {
							rmks.toggle();
					}
			});
			$("td.remarks").hide();
	}

	function column_header_clicked() {
		// Click column header - set or modify sort order.
		$("th.sortable").live("click", function () {
			form = $(this).parents("form")
			form_id = $(form).attr("id")
			column_id = this.id.split("-")[1]
			var column_index = $(this).parent().children("th").index(this)
			sort_on_selector = "[name=" + form_id + "_sort_on]"
			sort_on = $(sort_on_selector).val()
			sort_order_selector = "[name=" + form_id + "_sort_order]"
			sort_order = $(sort_order_selector).val()
			// if this column_id is the current sort
			if (sort_on == column_id) {
				// then we reverse sort order
				if (sort_order == "descending") {
					sort_order = "ascending"
				}
				else {
					sort_order = "descending"
				}
			}
			else {
				sort_on = column_id
				sort_order = "ascending"
			}
			// reset these values in the form (ajax sort uses them)
			$(sort_on_selector).val(sort_on)
			$(sort_order_selector).val(sort_order)

			// request new table content
			stored_form_action = $(form).attr("action")
			$(form).attr("action", window.location.href)
			$(form).append("<input type='hidden' name='table_only' value='" + form_id + "'>")
			var options = {
				target: $(this).parents("table"),
				replaceTarget: true,
				data: form.formToArray()
			}
			form.ajaxSubmit(options)
			$("[name='table_only']").remove()
			$(form).attr("action", stored_form_action)
		})
	}

	/**
	* Fetch allowed transitions for all the objects listed in bika_listing and
	* sets the value for the attribute 'data-valid_transitions' for each check
	* box next to each row.
	* The process requires an ajax call, so the function keeps checkboxes
	* disabled until the allowed transitions for the associated object are set.
	*/
	function load_transitions(blisting) {
		"use strict";
		if (blisting == '' || typeof blisting === 'undefined') {
            var blistings = $('table.bika-listing-table');
            $(blistings).each(function(i) {
                load_transitions($(this));
            });
            return;
		}
        var buttonspane = $(blisting).find('span.workflow_action_buttons');
		if (loading_transitions || $(buttonspane).length == 0) {
		    // If show_workflow_action_buttons param is set to False in the
		    // view, or transitions are being loaded already, do nothing
			return;
		}
		loading_transitions = true;
		var uids = [];
		var checkall = $("input[id*='select_all']");
		$(checkall).hide();
		var wo_trans = $("input[type='checkbox'][id*='_cb_'][data-valid_transitions='']");
		$(wo_trans).prop("disabled", true);
		$(wo_trans).each(function(e){
			uids.push($(this).val());
		});
		if (uids.length > 0) {
			var request_data = {
				_authenticator: $("input[name='_authenticator']").val(),
				uid:  $.toJSON(uids),};
			window.jsonapi_cache = window.jsonapi_cache || {};
			$.ajax({
				type: "POST",
				dataType: "json",
				url: window.portal_url + "/@@API/allowedTransitionsFor_many",
				data: request_data,
				success: function(data) {
					if ('transitions' in data) {
						for (var i = 0; i < data.transitions.length; i++) {
							var uid = data.transitions[i].uid;
							var trans = data.transitions[i].transitions;
							var el = $("input[type='checkbox'][id*='_cb_'][value='"+uid+"']");
							el.attr('data-valid_transitions', trans.join(','));
							$(el).prop("disabled", false);
						}
						$("input[id*='select_all']").fadeIn();
					}
				}
			});
		}
		loading_transitions = false;
	}

	/**
	* Controls the behavior when a checkbox of row selection is clicked.
	* Updates the status of the 'select all' checkbox accordingly and also
	* re-renders the workflow action buttons from the bottom of the list
	* based on the allowed transitions of the currently selected items
	*/
	function select_one_clicked() {
		"use strict";
		$("input[type='checkbox'][id*='_cb_']").live("click", function () {
			var blst = $(this).parents("table.bika-listing-table");
			render_transition_buttons(blst);
			// Modify all checkbox statuses
			var checked = $("input[type='checkbox'][id*='_cb_']:checked");
			var all =  $("input[type='checkbox'][id*='_cb_']");
			var checkall = $(blst).find("input[id*='select_all']");
			checkall.prop("checked", checked.length == all.length);
		});
	}

	/**
	* Controls the behavior when the 'select all' checkbox is clicked.
	* Checks/Unchecks all the row selection checkboxes and once done,
	* re-renders the workflow action buttons from the bottom of the list,
	* based on the allowed transitions for the currently selected items
	*/
	function select_all_clicked() {
		"use strict";
		// select all (on this page at least)
		$("input[id*='select_all']").live("click", function () {
			var blst = $(this).parents("table.bika-listing-table");
			var checkboxes = $(blst).find("[id*='_cb_']");
			$(checkboxes).prop("checked", $(this).prop("checked"));
			render_transition_buttons(blst);
		});
	}

	/**
	* Re-generates the workflow action buttons from the bottom of the list in
	* accordance with the allowed transitions for the currently selected items.
	* This is, makes the intersection within all allowed transitions and adds
	* the corresponding buttons to the workflow action bar.
	*/
	function render_transition_buttons(blst) {
		"use strict";
        var buttonspane = $(blst).find('span.workflow_action_buttons');
        if ($(buttonspane).length == 0) {
		    // If show_workflow_action_buttons param is set to False in the
		    // view, do nothing
		    return;
		}
		var allowed_transitions = [];
		var hidden_transitions = $(blst).find('input[type="hidden"][id="hide_transitions"]');
		hidden_transitions = $(hidden_transitions).length == 1 ? $(hidden_transitions).val() : '';
		hidden_transitions = hidden_transitions === '' ? [] : hidden_transitions.split(',');
		var restricted_transitions = $(blst).find('input[type="hidden"][id="restricted_transitions"]');
		restricted_transitions = $(restricted_transitions).length == 1 ? $(restricted_transitions).val() : '';
		restricted_transitions = restricted_transitions === '' ? [] : restricted_transitions.split(',');
		var checked = $(blst).find("input[type='checkbox'][id*='_cb_']:checked");
		$(checked).each(function(e) {
			var transitions = $(this).attr('data-valid_transitions');
			transitions = transitions.split(',');
			if (restricted_transitions.length > 0) {
				// Do not want transitions other than those defined in bikalisting
				transitions = transitions.filter(function(el) {
					return restricted_transitions.indexOf(el) != -1;
				});
			}
			// Do not show hidden transitions
			transitions = transitions.filter(function(el) {
				return hidden_transitions.indexOf(el) == -1;
			});
			// We only want the intersection within all selected items
			if (allowed_transitions.length > 0) {
				transitions = transitions.filter(function(el) {
					return allowed_transitions.indexOf(el) != -1;
				});
			}
			allowed_transitions = transitions;
		});
		if (restricted_transitions.length > 0) {
			// Sort the transitions in accordance with bikalisting settings
			allowed_transitions = restricted_transitions.filter(function(v) {
			    return allowed_transitions.includes(v);
			});
		}

		// Generate the action buttons
		$(buttonspane).html('');
		for (var i = 0; i < allowed_transitions.length; i++) {
			var trans = allowed_transitions[i];
			var button = '<input id="'+trans+'_transition" class="context workflow_action_button action_button allowMultiSubmit" type="submit" url="" value="'+_(PMF(trans+'_transition_title'))+'" transition="'+trans+'" name="workflow_action_button">&nbsp;';
			$(buttonspane).append(button);
		}
		// Add now custom actions
		if ($(checked).length > 0) {
			var custom_actions = $(blst).find('input[type="hidden"].custom_action');
			$(custom_actions).each(function(e){
				var trans = $(this).val();
				var url = $(this).attr('url');
				var title = $(this).attr('title');
				var button = '<input id="'+trans+'_transition" class="context workflow_action_button action_button allowMultiSubmit" type="submit" url="'+url+'" value="'+title+'" transition="'+trans+'" name="workflow_action_button">&nbsp;';
				$(buttonspane).append(button);
			});
		}
	}

	function listing_string_input_keypress() {
		"use strict";
		$(".listing_string_entry,.listing_select_entry").live("keypress", function (event) {
			// Prevent automatic submissions of manage_results forms when enter is pressed
			var enter = 13
			if (event.which == enter) {
				event.preventDefault()
			}
			// check the item's checkbox
			var form_id = $(this).parents("form").attr("id")
			var uid = $(this).attr("uid")
			if (!($("#" + form_id + "_cb_" + uid).prop("checked"))) {
				$("#" + form_id + "_cb_" + uid).prop("checked", true)
			}
		})
	}

	function listing_string_select_changed() {
		// always select checkbox when selectable listing item is changed
		$(".listing_select_entry").live("change", function () {
			form_id = $(this).parents("form").attr("id")
			uid = $(this).attr("uid")
			// check the item's checkbox
			if (!($("#" + form_id + "_cb_" + uid).prop("checked"))) {
				$("#" + form_id + "_cb_" + uid).prop("checked", true)
			}
		})
	}

	function pagesize_change() {
		// pagesize
		$("select.pagesize").live("change", function () {
			form = $(this).parents("form")
			form_id = $(form).attr("id")
			pagesize = $(this).val()
			new_query = $.query
			  .set(form_id + "_pagesize", pagesize)
			  .set(form_id + "_pagenumber", 1).toString()
			window.location = window.location.href.split("?")[0] + new_query
		})
	}

	function category_header_clicked() {
		// expand/collapse categorised rows
		$(".bika-listing-table th.collapsed").live("click", function () {
			if (!$(this).hasClass("ignore_bikalisting_default_handler")){
				that.category_header_expand_handler(this)
			}
		});
        $(".bika-listing-table th.expanded").live("click", function () {
            if (!$(this).hasClass("ignore_bikalisting_default_handler")){
                // After ajax_category expansion, collapse and expand work as they would normally.
                $(this).parent().nextAll("tr[cat='" + $(this).attr("cat") + "']").toggle();
                if($(this).hasClass("expanded")){
                    // Set collapsed class on TR
                    $(this).removeClass("expanded").addClass("collapsed")
                }
                else if ($(this).hasClass("collapsed")){
                    // Set expanded class on TR
                    $(this).removeClass("collapsed").addClass("expanded")
                }
            }
        })
    }

	that.category_header_expand_handler = function (element) {
		// element is the category header TH.
		// duplicated in bika.lims.analysisrequest.add_by_col.js
		var def = $.Deferred()
		// with form_id allow multiple ajax-categorised tables in a page
		var form_id = $(element).parents("[form_id]").attr("form_id")
		var cat_title = $(element).attr('cat')
		// URL can be provided by bika_listing classes, with ajax_category_url attribute.
		var url = $("input[name='ajax_categories_url']").length > 0
		  ? $("input[name='ajax_categories_url']").val()
		  : window.location.href.split('?')[0]
		// We will replace this element with downloaded items:
		var placeholder = $("tr[data-ajax_category='" + cat_title + "']")

		// If it's already been expanded, ignore
		if ($(element).hasClass("expanded")) {
			def.resolve()
			return def.promise()
		}

		// If ajax_categories are enabled, we need to go request items now.
		var ajax_categories_enabled = $("input[name='ajax_categories']")
		if (ajax_categories_enabled.length > 0 && placeholder.length > 0) {
			var options = {}
			options['ajax_category_expand'] = 1
			options['cat'] = cat_title
			options['form_id'] = form_id
			url = $("input[name='ajax_categories_url']").length > 0
			  ? $("input[name='ajax_categories_url']").val()
			  : url
			if ($('.review_state_selector a.selected').length > 0) {
				// review_state must be kept the same after items are loaded
				// (TODO does this work?)
				options['review_state'] = $('.review_state_selector a.selected')[0].id
			}
            $.ajax({url: url, data: options})
                .done(function (data) {
                    // The same as: LIMS-1970 Analyses from AR Add form not displayed properly
                    var rows = $("<table>"+data+"</table>").find("tr");
                    $("[form_id='" + form_id + "'] tr[data-ajax_category='" + cat_title + "']")
                        .replaceWith(rows);
                    $(element).removeClass("collapsed").addClass("expanded");
                    def.resolve()
                })
        }
		else {
			// When ajax_categories are disabled, all cat items exist as TR elements:
			$(element).parent().nextAll("tr[cat='" + $(element).attr("cat") + "']").toggle(true)
			$(element).removeClass("collapsed").addClass("expanded")
			def.resolve()
		}
		// Set expanded class on TR
		return def.promise()
	}

	function filter_search_keypress() {
		// pressing enter on filter search will trigger
		// a click on the search link.
		$('.filter-search-input').live('keypress', function (event) {
			var enter = 13
			if (event.which == enter) {
				$('.filter-search-button').click()
				return false
			}
		})
	}

	function filter_search_button_click() {
		// trap the Clear search / Search buttons
		$('.filter-search-button').live('click', function (event) {
			form = $(this).parents('form')
			form_id = $(form).attr('id')
			stored_form_action = $(form).attr("action")
			$(form).attr("action", window.location.href)
			$(form).append("<input type='hidden' name='table_only' value='" + form_id + "'>")
			var options = {
				target: $(this).parents('table'),
				replaceTarget: true,
				data: form.formToArray()
			}
			form.ajaxSubmit(options)
			$('[name="table_only"]').remove()
			$(form).attr('action', stored_form_action)
			return false
		})
	}

	function workflow_action_button_click() {
		// Workflow Action button was clicked.
		$(".workflow_action_button").live("click", function (event) {

			// The submit buttons would like to put the translated action title
			// into the request.  Insert the real action name here to prevent the
			// WorkflowAction handler from having to look it up (painful/slow).
			var form = $(this).parents("form")
			var form_id = $(form).attr("id")
			$(form).append("<input type='hidden' name='workflow_action_id' value='" + $(this).attr("transition") + "'>")

			// This submit_transition cheat fixes a bug where hitting submit caused
			// form to be posted before ajax calculation is returned
			if (this.id == "submit_transition") {
				var focus = $(".ajax_calculate_focus")
				if (focus.length > 0) {
					var e = $(focus[0])
					if ($(e).attr("focus_value") == $(e).val()) {
						// value did not change - transparent blur handler.
						$(e).removeAttr("focus_value")
						$(e).removeClass("ajax_calculate_focus")
					}
					else {
						// The calcs.js code is now responsible for submitting
						// this form when the calculation ajax is complete
						$(e).parents("form").attr("submit_after_calculation", 1)
						event.preventDefault()
					}
				}
			}

			// If a custom_actions action with a URL is clicked
			// the form will be submitted there
			if ($(this).attr("url") !== "") {
				form = $(this).parents("form")
				$(form).attr("action", $(this).attr("url"))
				$(form).submit()
			}

		})
	}

	function column_toggle_context_menu() {
		// show / hide columns - the right-click pop-up
		$('th[id^="foldercontents-"]').live('contextmenu', function (event) {
			event.preventDefault()
			form_id = $(this).parents("form").attr("id")
			portal_url = window.portal_url
			toggle_cols = $("#" + form_id + "_toggle_cols").val()
			if (toggle_cols == ""
			  || toggle_cols == undefined
			  || toggle_cols == null) {
				return false
			}
			sorted_toggle_cols = []
			$.each($.parseJSON(toggle_cols), function (col_id, v) {
				v['id'] = col_id
				sorted_toggle_cols.push(v)
			})
			sorted_toggle_cols.sort(function (a, b) {
				var titleA = a['title'].toLowerCase()
				var titleB = b['title'].toLowerCase()
				if (titleA < titleB) {
					return -1
				}
				if (titleA > titleB) {
					return 1
				}
				return 0
			})

			txt = '<div class="tooltip"><table class="contextmenu" cellpadding="0" cellspacing="0">'
			txt = txt + "<tr><th colspan='2'>" + _("Display columns") + "</th></tr>"
			for (i = 0; i < sorted_toggle_cols.length; i++) {
				col = sorted_toggle_cols[i]
				col_id = _(col['id'])
				col_title = _(col['title'])
				enabled = $("#foldercontents-" + col_id + "-column")
				if (enabled.length > 0) {
					txt = txt + "<tr class='enabled' col_id='" + col_id + "' form_id='" + form_id + "'>"
					txt = txt + "<td>"
					txt = txt + "<img style='height:1em;' src='" + portal_url + "/++resource++bika.lims.images/ok.png'/>"
					txt = txt + "</td>"
					txt = txt + "<td>" + col_title + "</td></tr>"
				}
				else {
					txt = txt + "<tr col_id='" + col_id + "' form_id='" + form_id + "'>"
					txt = txt + "<td>&nbsp;</td>"
					txt = txt + "<td>" + col_title + "</td></tr>"
				}
			}
			txt = txt + "<tr col_id='" + _("All") + "' form_id='" + form_id + "'>"
			txt = txt + "<td style='border-top:1px solid #ddd'>&nbsp;</td>"
			txt = txt + "<td style='border-top:1px solid #ddd'>" + _('All') + "</td></tr>"

			txt = txt + "<tr col_id='" + _("Default") + "' form_id='" + form_id + "'>"
			txt = txt + "<td>&nbsp;</td>"
			txt = txt + "<td>" + _('Default') + "</td></tr>"

			txt = txt + '</table></div>'
			$(txt).appendTo('body')
			positionTooltip(event)
			return false
		})
	}

	function column_toggle_context_menu_selection() {
		// show / hide columns - the action when a column is clicked in the menu
		$('.contextmenu tr').live('click', function (event) {
			form_id = $(this).attr('form_id')
			form = $("form#" + form_id)

			col_id = $(this).attr('col_id')
			col_title = $(this).text()
			enabled = $(this).hasClass("enabled")

			cookie = readCookie("toggle_cols")
			cookie = $.parseJSON(cookie)
			cookie_key = $(form[0].portal_type).val() + form_id

			if (cookie == null || cookie == undefined) {
				cookie = {}
			}
			if (col_id == _('Default')) {
				// Remove entry from existing cookie if there is one
				delete(cookie[cookie_key])
				createCookie('toggle_cols', $.toJSON(cookie), 365)
			}
			else if (col_id == _('All')) {
				// add all possible columns
				toggle_cols = []
				$.each($.parseJSON($('#' + form_id + "_toggle_cols").val()), function (i, v) {
					toggle_cols.push(i)
				})
				cookie[cookie_key] = toggle_cols
				createCookie('toggle_cols', $.toJSON(cookie), 365)
			}
			else {
				toggle_cols = cookie[cookie_key]
				if (toggle_cols == null || toggle_cols == undefined) {
					// this cookie key not yet defined
					toggle_cols = []
					$.each($.parseJSON($('#' + form_id + "_toggle_cols").val()), function (i, v) {
						if (!(col_id == i && enabled) && v['toggle']) {
							toggle_cols.push(i)
						}
					})
				}
				else {
					// modify existing cookie
					if (enabled) {
						toggle_cols.splice(toggle_cols.indexOf(col_id), 1)
					}
					else {
						toggle_cols.push(col_id)
					}
				}
				cookie[cookie_key] = toggle_cols
				createCookie('toggle_cols', $.toJSON(cookie), 365)

			}
			$(form).attr("action", window.location.href)
			$(".tooltip").remove()
			form.submit()
			return false
		})
	}

	function positionTooltip(event) {
		var tPosX = event.pageX - 5
		var tPosY = event.pageY - 5
		$('div.tooltip').css({
								 'border': '1px solid #fff',
								 'border-radius': '.25em',
								 'background-color': '#fff',
								 'position': 'absolute',
								 'top': tPosY,
								 'left': tPosX
							 })
	}

    function autosave() {
        /*
        This function looks for the column defined as 'autosave' and if
        its value is true, the result of this input will be saved after each
        change via ajax.
        */
        $('select.autosave, input.autosave').not('[type="hidden"]')
            .each(function(i) {
            // Save select fields
            $(this).change(function () {
                var pointer = this;
                build_typical_save_request(pointer);
            });
        });
    }
    function build_typical_save_request(pointer) {
        /**
         * Build an array with the data to be saved for the typical data fields.
         * @pointer is the object which has been modified and we want to save its new data.
         */
        var fieldvalue, fieldname, requestdata={}, uid, tr;
        fieldvalue = $(pointer).val();
        fieldname = $(pointer).attr('field');
        tr = $(pointer).closest('tr');
        uid = $(pointer).attr('uid');
        requestdata[fieldname] = fieldvalue;
        requestdata['obj_uid']= uid;
        save_elements(requestdata, tr);
    }
    function save_elements(requestdata, tr) {
        /**
         * Given a dict with a fieldname and a fieldvalue, save this data via ajax petition.
         * @requestdata should has the format  {fieldname=fieldvalue, uid=xxxx} ->  { ReportDryMatter=false, uid=xxx}.
         */
        var url = window.location.href.replace('/base_view', '');
        // Staff for the notification
        var name = $(tr).attr('title');
        var anch =  "<a href='"+ url + "'>" + name + "</a>";
        $.ajax({
            type: "POST",
            url: window.portal_url+"/@@API/update",
            data: requestdata
        })
        .done(function(data) {
            //success alert
            if (data != null && data['success'] == true) {
                bika.lims.SiteView.notificationPanel(anch + ': ' + name + ' updated successfully', "succeed");
            } else {
                bika.lims.SiteView.notificationPanel('Error while updating ' + name + ' for '+ anch, "error");
                var msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for '+ ar;
                console.warn(msg);
                window.bika.lims.error(msg);
            }
        })
        .fail(function(){
            //error
            bika.lims.SiteView.notificationPanel('Error while updating ' + name + ' for '+ anch, "error");
            var msg = '[bika.lims.analysisrequest.js] Error while updating ' + name + ' for '+ ar;
            console.warn(msg);
            window.bika.lims.error(msg);
        });
    }

    /**
     * Load the events regardin to the export (to CSV and to XML) buttons. When
     * an export button is clicked, the function walksthrough all the items
     * within the bika listing table, builds a string with the desired format
     * (CSV or XML) and prompts the user for its download.
     */
    function load_export_buttons() {
        $('.bika-listing-table td.export-controls span.export-toggle').click(function(e) {
            var ul = $(this).closest('td').find('ul');
            if ($(ul).is(":visible")) {
                $(this).removeClass("expanded");
            } else {
                $(ul).css('min-width', $(this).width());
                $(this).addClass("expanded");
            }
            $(ul).toggle();
        });
        $(".bika-listing-table a[download]").click(function(e) {
            $(this).closest('.bika-listing-table').find('td.export-controls span.export-toggle').click();
            var type = $(this).attr('type');
            var data = [];
            var headers = [];
            var omitidx = [];

            // Get the headers, but only if not empty. Store the position index
            // of those columns that must be omitted later on rows walkthrouugh
            $(this).closest(".bika-listing-table").find("th.column").each(function(i) {
                var colname = $.trim($(this).text());
                if (colname != "") {
                    colname = colname.replace('"', "'");
                    headers.push('"' + colname + '"');
                } else {
                    omitidx.push(i);
                }
            });
            data.push(headers.join(","));

            // Iterate through all rows an append all data in an array
            // that later will be transformed into the desired format
            $(this).closest(".bika-listing-table").find("tbody tr").each(function(r) {
                // Iterate through all cells from within the current row
                var rowdata = [];
                $(this).find("td").each(function(c) {
                    // Should the current cell be omitted?
                    if ($.inArray(c, omitidx) > -1) {
                        return 'non-false';
                    }
                    // Each cell's content is structured as follows:
                    // <span class='before'></span>
                    // <element>content</element>
                    // <span class='after'>
                    var text = $(this).find("span.before")
                                      .nextUntil("span.after").text();
                    // If no format specified, always fallback to csv
                    text = text.replace('"', "'");
                    rowdata.push('"' + $.trim(text) + '"');
                });
                if (rowdata.length == headers.length) {
                    data.push(rowdata.join(','));
                }
            });
            var output = '';
            var urischema = '';
            if (type == 'xml') {
                output = "<items>\r\n";
                for (var i = 1; i < data.length; i++) {
                    row = data[i].substr(1,data[i].length-2);
                    row = row.split('","');
                    if (row.length == headers.length) {
                        output += "  <item>\r\n";
                        for (var j=0; j < row.length; j++) {
                            if (j < headers.length) {
                                var colname = qname(headers[j]);
                                output += "    <"+colname+">";
                                output += escapeTxt(row[j]);
                                output += "</"+colname+">\r\n";
                            }
                        }
                        output += "  </item>\r\n";
                    }
                }
                output += "</items>";
                urischema = 'data:application/xml;base64;charset-UTF-8,';
            } else {
                // Fallback CSV
                output = data.join('\r\n');
                urischema = 'data:application/csv;base64;charset=UTF-8,';
            }
            var uri = urischema + btoa(output);
            $(this).attr('href', uri);
        });

        function unquote(val) {
            return val.replace( /^\s*\"(.*)\"\s*$/, "$1" );
        }

        function escapeTxt(val) {
            var vl = val.replace(/&/g, "&amp;");
            vl = vl.replace(/</g, "&lt;");
            vl = vl.replace(/>/g, "&gt;");
            return unquote(vl);
        }

        function qname(name) {
            var nm = name.replace(/(\s)+/g, "_");
            return unquote(nm);
        }
    }
}
