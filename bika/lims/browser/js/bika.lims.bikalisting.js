(function( $ ) {
$(document).ready(function(){

    window.jarn.i18n.loadCatalog("bika");
	_ = jarn.i18n.MessageFactory("bika");
    window.jarn.i18n.loadCatalog("plone");
	PMF = jarn.i18n.MessageFactory("plone");

	// Click column header - set or modify sort order.
	$("th.sortable").live("click", function(){
		form = $(this).parents("form");
		form_id = $(form).attr("id");
		column_id = this.id.split("-")[1];
		var column_index = $(this).parent().children("th").index(this);
		sort_on_selector = "[name=" + form_id + "_sort_on]";
		sort_on = $(sort_on_selector).val();
		sort_order_selector = "[name=" + form_id + "_sort_order]";
		sort_order = $(sort_order_selector).val();
		// if this column_id is the current sort
		if (sort_on == column_id) {
			// then we reverse sort order
			if (sort_order == "descending") {
				sort_order = "ascending";
			} else {
				sort_order = "descending";
			}
		} else {
			sort_on = column_id;
			sort_order = "ascending";
		}
		// reset these values in the form (ajax sort uses them)
		$(sort_on_selector).val(sort_on);
		$(sort_order_selector).val(sort_order);

		// request new table content
		stored_form_action = $(form).attr("action");
		$(form).attr("action", window.location.href);
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		var options = {
			target: $(this).parents("table"),
			replaceTarget: true,
			data: form.formToArray()
		};
		form.ajaxSubmit(options);
		$("[name='table_only']").remove();
		$(form).attr("action", stored_form_action);
	});

	// select all (on this page at least)
	$("input[id*='select_all']").live("click", function(){
		var checkboxes = $(this).parents("form").find("[id*='_cb_']");
		if($(this).prop("checked")) {
			$(checkboxes).filter("input:checkbox:not(:checked)").prop("checked", true);
		} else {
			$(checkboxes).filter("input:checkbox:checked").prop("checked", false);
		}
	});

	// modify select_all checkbox when regular checkboxes are modified
	$("input[id*='_cb_']").live("change", function(){
		form_id = $(this).parents("form").attr("id");
		all_selected = true;
		$.each($("input[id^='"+form_id+"_cb_']"), function(i,v){
			if(!($(v).prop("checked"))){
				all_selected = false;
			}
		});
		if(all_selected){
			$("#"+form_id+"_select_all").prop("checked",true);
		} else {
			$("#"+form_id+"_select_all").prop("checked",false);
		}
	});

	$(".listing_string_entry,.listing_select_entry").live("keypress", function(event) {
		// Prevent automatic submissions of manage_results forms when enter is pressed
		var enter = 13;
		if (event.which == enter) {
			event.preventDefault();
		}
		// check the item's checkbox
		form_id = $(this).parents("form").attr("id");
		uid = $(this).attr("uid");
		if (!($("#"+form_id+"_cb_"+uid).prop("checked"))) {
			$("#"+form_id+"_cb_"+uid).prop("checked", true);
		}
	});

	// pagesize
	$("select.pagesize").live("change", function(){
		form = $(this).parents("form");
		form_id = $(form).attr("id");
		pagesize = $(this).val();
		new_query = $.query
			.set(form_id + "_pagesize", pagesize)
			.set(form_id + "_pagenumber", 1).toString();
		window.location = window.location.href.split("?")[0] + new_query;
	});

	// expand/collapse categorised rows
	$(".bika-listing-table th.collapsed").live("click", function(){
		$(this).parent().nextAll("tr[cat='"+$(this).attr("cat")+"']") .toggle(true);
		$(this) .removeClass("collapsed") .addClass("expanded");
	});
	$(".bika-listing-table th.expanded").live("click", function(){
		$(this).parent().nextAll("tr[cat='"+$(this).attr("cat")+"']") .toggle(false);
		$(this).removeClass("expanded") .addClass("collapsed");
	});

	// always select checkbox when selectable listing item is changed
	$(".listing_select_entry").live("change", function(){
		form_id = $(this).parents("form").attr("id");
		uid = $(this).attr("uid");
		// check the item's checkbox
		if (!($("#"+form_id+"_cb_"+uid).prop("checked"))) {
			$("#"+form_id+"_cb_"+uid).prop("checked", true);
		}
	});

	// pressing enter on filter search will trigger
	// a click on the search link.
	$('.filter-search-input').live('keypress', function(event) {
		var enter = 13;
		if (event.which == enter) {
			$('.filter-search-button').click();
			return false;
		}
	});

	// trap the Clear search / Search buttons
	$('.filter-search-button').live('click', function(event){
		form = $(this).parents('form');
		form_id = $(form).attr('id');
		stored_form_action = $(form).attr("action");
		$(form).attr("action", window.location.href);
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		var options = {
			target: $(this).parents('table'),
			replaceTarget: true,
			data: form.formToArray()
		}
		form.ajaxSubmit(options);
		$('[name="table_only"]').remove();
		$(form).attr('action', stored_form_action)
		return false;
	});


	// Workflow Action button was clicked.
	$(".workflow_action_button").live("click", function(event){

		// The submit buttons would like to put the translated action title
		// into the request.  Insert the real action name here to prevent the
		// WorkflowAction handler from having to look it up (painful/slow).
		var form = $(this).parents("form");
		var form_id = $(form).attr("id");
		$(form).append("<input type='hidden' name='workflow_action_id' value='"+$(this).attr("transition")+"'>");

		// This submit_transition cheat fixes a bug where hitting submit caused
		// form to be posted before ajax calculation is returned
		if(this.id=="submit_transition"){
			var focus = $(".ajax_calculate_focus");
			if(focus.length > 0){
				var e = $(focus[0]);
				if ($(e).attr("focus_value") == $(e).val()){
					// value did not change - transparent blur handler.
					$(e).removeAttr("focus_value");
					$(e).removeClass("ajax_calculate_focus");
				} else {
					// The calcs.js code is now responsible for submitting
					// this form when the calculation ajax is complete
					$(e).parents("form").attr("submit_after_calculation", 1);
					event.preventDefault();
				}
			}
		}

		// If a custom_actions action with a URL is clicked
		// the form will be submitted there
		if ($(this).attr("url") !== ""){
			form = $(this).parents("form");
			$(form).attr("action", $(this).attr("url"));
			$(form).submit();
		}

	});


	function positionTooltip(event){
		var tPosX = event.pageX-5;
		var tPosY = event.pageY-5;
		$('div.tooltip').css({'border': '1px solid #fff',
							  'border-radius':'.25em',
							  'background-color':'#fff',
							  'position': 'absolute',
							  'top': tPosY,
							  'left': tPosX});
	};

	// show / hide columns - the right-click pop-up
	$('th[id^="foldercontents-"]').live('contextmenu', function(event){
		event.preventDefault();
		form_id = $(this).parents("form").attr("id");
		portal_url = window.portal_url;
		toggle_cols = $("#" + form_id + "_toggle_cols").val();
		if (toggle_cols == ""
			|| toggle_cols == undefined
			|| toggle_cols == null){
			return false;
		}
		sorted_toggle_cols = [];
		$.each($.parseJSON(toggle_cols), function(col_id,v){
			v['id'] = col_id;
			sorted_toggle_cols.push(v);
		});
		sorted_toggle_cols.sort(function(a, b){
			var titleA=a['title'].toLowerCase();
			var titleB=b['title'].toLowerCase();
			if (titleA < titleB) return -1;
			if (titleA > titleB) return 1;
			return 0;
		});

		txt = '<div class="tooltip"><table class="contextmenu" cellpadding="0" cellspacing="0">';
		txt = txt + "<tr><th colspan='2'>"+_("Display columns")+"</th></tr>";
		for(i=0;i<sorted_toggle_cols.length;i++){
			col = sorted_toggle_cols[i];
			col_id = _(col['id']);
			col_title = _(col['title']);
			enabled = $("#foldercontents-"+col_id+"-column");
			if(enabled.length > 0){
				txt = txt + "<tr class='enabled' col_id='"+col_id+"' form_id='"+form_id+"'>";
				txt = txt + "<td>";
				txt = txt + "<img style='height:1em;' src='"+portal_url+"/++resource++bika.lims.images/ok.png'/>";
				txt = txt + "</td>";
				txt = txt + "<td>"+col_title+"</td></tr>";
			} else {
				txt = txt + "<tr col_id='"+col_id+"' form_id='"+form_id+"'>";
				txt = txt + "<td>&nbsp;</td>";
				txt = txt + "<td>"+col_title+"</td></tr>";
			}
		}
		txt = txt + "<tr col_id='" + _("All") + "' form_id='"+form_id+"'>";
		txt = txt + "<td style='border-top:1px solid #ddd'>&nbsp;</td>";
		txt = txt + "<td style='border-top:1px solid #ddd'>"+_('All')+"</td></tr>";

		txt = txt + "<tr col_id='" + _("Default") + "' form_id='"+form_id+"'>";
		txt = txt + "<td>&nbsp;</td>";
		txt = txt + "<td>"+_('Default')+"</td></tr>";

		txt = txt + '</table></div>';
		$(txt).appendTo('body');
		positionTooltip(event);
		return false;
	});
	$('*').click(function(){
		$(".tooltip").remove();
	});

	// show / hide columns - the action when a column is clicked in the menu
	$('.contextmenu tr').live('click', function(event){
		form_id = $(this).attr('form_id');
		form = $("form#"+form_id);

		col_id = $(this).attr('col_id');
		col_title = $(this).text();
		enabled = $(this).hasClass("enabled");

		cookie = readCookie("toggle_cols");
		cookie = $.parseJSON(cookie);
		cookie_key = $(form[0].portal_type).val() + form_id;

		if (cookie == null || cookie == undefined) {
			cookie = {};
		}
		if(col_id==_('Default')){
			// Remove entry from existing cookie if there is one
			delete(cookie[cookie_key]);
			createCookie('toggle_cols', $.toJSON(cookie), 365);
		} else if(col_id==_('All')) {
			// add all possible columns
			toggle_cols = [];
			$.each($.parseJSON($('#'+form_id+"_toggle_cols").val()), function(i,v){
				toggle_cols.push(i);
			});
			cookie[cookie_key] = toggle_cols;
			createCookie('toggle_cols', $.toJSON(cookie), 365);
		} else {
			toggle_cols = cookie[cookie_key];
			if (toggle_cols == null || toggle_cols == undefined) {
				// this cookie key not yet defined
				toggle_cols = [];
				$.each($.parseJSON($('#'+form_id+"_toggle_cols").val()), function(i,v){
					if(!(col_id == i && enabled) && v['toggle']) {
						toggle_cols.push(i);
					}
				});
			} else {
				// modify existing cookie
				if(enabled) {
					toggle_cols.splice(toggle_cols.indexOf(col_id), 1);
				} else {
					toggle_cols.push(col_id);
				}
			}
			cookie[cookie_key] = toggle_cols;
			createCookie('toggle_cols', $.toJSON(cookie), 365);

		}
		$(form).attr("action", window.location.href);
		$(".tooltip").remove();
		form.submit();
		return false;
	});

});
}(jQuery));
