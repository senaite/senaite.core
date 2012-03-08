jQuery( function($) {
$(document).ready(function(){

	_ = window.jsi18n;

	function setoddeven(){
		// set alternating odd and even classes if table has setoddeven class
		$.each($("table.setoddeven tbody.item-listing-tbody tr"), function(i,tr){
			if (i%2 == 0) {
				$(tr).addClass('odd');
			} else {
				$(tr).addClass('even');
			}
		});
	}

	function portalMessage(message){
		str = "<dl class='portalMessage error'>"+
			"<dt>"+_("error")+"</dt>"+
			"<dd><ul>" + message +
			"</ul></dd></dl>";
		$('.portalMessage').remove();
		$(str).appendTo('#viewlet-above-content');
	}

	setoddeven();

	// review_state
	$(".review_state_selector a").live('click', function(){
		form = $(this).parents("form");
		form_id = $(form).attr("id");
		review_state = $(this).attr("value");
		$("[name="+form_id+"_review_state]").val(review_state);
		stored_form_action = $(form).attr("action");
		$(form).attr("action", window.location.href);
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		options = {
			target: $(this).parents("table"),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				setoddeven();
			}
		}
		form.ajaxSubmit(options);
		$("[name=table_only]").remove();
		$(form).attr("action", stored_form_action)
		return false;
	});

	// Click column header - set or modify sort order.
	$("th.sortable").live('click', function(){
		form = $(this).parents("form");
		form_id = $(form).attr("id");
		column_id = this.id.split("-")[1];
		var column_index = $(this).parent().children('th').index(this);
		sort_on_selector = '[name=' + form_id + '_sort_on]';
		sort_on = $(sort_on_selector).val();
		sort_order_selector = '[name=' + form_id + '_sort_order]';
		sort_order = $(sort_order_selector).val();
		// if this column_id is the current sort
		if (sort_on == column_id) {
			// then we reverse sort order
			if (sort_order == 'descending') {
				sort_order = 'ascending';
			} else {
				sort_order = 'descending';
			}
		} else {
			sort_on = column_id;
			sort_order = 'ascending';
		}
		// reset these values in the form (ajax sort uses them)
		$(sort_on_selector).val(sort_on);
		$(sort_order_selector).val(sort_order);

		// request new table content
		stored_form_action = $(form).attr("action");
		$(form).attr("action", window.location.href);
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		options = {
			target: $(this).parents("table"),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				setoddeven();
			}
		}
		form.ajaxSubmit(options);
		$("[name=table_only]").remove();
		$(form).attr("action", stored_form_action);
	});

	// select all (on this screen at least)
	$("input[id*='select_all']").live('click', function(){
		form_id = $(this).parents("form").attr("id");
		checked = $(this).attr("checked");
		$.each($("input[id^='"+form_id+"_cb_']"), function(i,v){
			$(v).attr("checked", checked);
		});
	});

	// modify select_all checkbox when regular checkboxes are modified
	$("input[id*='_cb_']").live('click', function(){
		form_id = $(this).parents("form").attr("id");
		all_selected = true;
		$.each($("input[id^='"+form_id+"_cb_']"), function(i,v){
			if($(v).attr("checked") == false){
				all_selected = false;
			}
		});
		if(all_selected){
			$("#"+form_id+"_select_all").attr("checked", true);
		} else {
			$("#"+form_id+"_select_all").attr("checked", false);
		}
	});

	// Prevent automatic submissions of manage_results
	// forms when enter is pressed
	$(".listing_string_entry,.listing_select_entry").live('keypress', function(event) {
		var tab = 9;
		var enter = 13;
		if (event.which == enter) {
			event.preventDefault();
		}
	});

	// pagesize
	$("select[name='pagesize']").live('change', function(){
		form = $(this).parents('form');
		form_id = $(form).attr('id');
		pagesize = $(this).val();
		$("[name="+form_id+"_pagesize]").val(pagesize);
		stored_form_action = $(form).attr("action");
		$(form).attr("action", window.location.href);
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		options = {
			target: $(form).children(".bika-listing-table"),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				setoddeven();
			}
		}
		form.ajaxSubmit(options);
		$('[name=table_only]').remove();
		$(form).attr('action', stored_form_action)
		return false;
	});

	// batching pagenumber links
	$("a[pagenumber]").live('click', function(){
		form = $(this).parents('form');
		form_id = $(form).attr('id');
		pagenumber = $(this).attr('pagenumber');
		$("[name="+form_id+"_pagenumber]").val(pagenumber);
		stored_form_action = $(form).attr("action");
		$(form).attr("action", window.location.href);
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		options = {
			target: $(form).children(".bika-listing-table"),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				setoddeven();
			}
		}
		form.ajaxSubmit(options);
		$('[name=table_only]').remove();
		$(form).attr('action', stored_form_action)
		return false;
	});

	// expand/collapse categorised rows
	$(".bika-listing-table th.collapsed").live('click', function(){
		table = $(this).parents('.bika-listing-table');
		// show sub TR rows
		$(table)
			.children('tbody')
			.children('tr[cat='+$(this).attr("cat")+']')
			.toggle(true);
		// change TH state
		$(this).removeClass('collapsed').addClass('expanded');
		setoddeven();
	});
	$(".bika-listing-table th.expanded").live('click', function(){
		table = $(this).parents('.bika-listing-table');
		// show sub TR rows
		$(table)
			.children('tbody')
			.children('tr[cat='+$(this).attr("cat")+']')
			.toggle(false);
		// change TH state
		$(this).removeClass('expanded').addClass('collapsed');
		setoddeven();
	});

	// always select checkbox when editable listing item is changed
	$(".listing_string_entry,.listing_select_entry").live('change', function(){
		form_id = $(this).parents("form").attr("id");
		uid = $(this).attr('uid');
		// check the item's checkbox
		if ($('#'+form_id+'_cb_'+uid).attr('checked') == false) {
			$('#'+form_id+'_cb_'+uid).click();
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
		options = {
			target: $(this).parents('table'),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				setoddeven();
			}
		}
		form.ajaxSubmit(options);
		$('[name=table_only]').remove();
		$(form).attr('action', stored_form_action)
		return false;
	});

	// wait for all asynchronous requests to complete before allowing clicks
	$('.workflow_action_button').live('click', function(event){
		if($.active > 0){
			event.preventDefault();
			$(this).ajaxStop(function(){
				$(this).click();
			});
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
		base_url = window.location.href;
		toggle_cols = $("#" + form_id + "_toggle_cols").val();
		if (toggle_cols == ""){
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
	            txt = txt + "<img style='height:1em;' src='"+base_url+"/++resource++bika.lims.images/ok.png'/>";
				txt = txt + "</td>";
				txt = txt + "<td>"+col_title+"</td></tr>";
			} else {
				txt = txt + "<tr col_id='"+col_id+"' form_id='"+form_id+"'>";
				txt = txt + "<td>&nbsp;</td>";
				txt = txt + "<td>"+col_title+"</td></tr>";
			}
		}
		txt = txt + "<tr col_id='ALL' form_id='"+form_id+"'>";
		txt = txt + "<td style='border-top:1px solid #ddd'>&nbsp;</td>";
		txt = txt + "<td style='border-top:1px solid #ddd'>"+_('All')+"</td></tr>";

		txt = txt + "<tr col_id='DEFAULT' form_id='"+form_id+"'>";
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

	// show / hide columns - the action when a checkbox is clicked in the menu
	$('.contextmenu tr').live('click', function(event){
		col_id = $(this).attr('col_id');
		form_id = $(this).attr('form_id');
		form = $("form#"+form_id);

		if(col_id=='DEFAULT'){
			$.cookie('toggle_cols', null);
		} else if(col_id=='ALL') {
			cookie = $.cookie("toggle_cols");
			cookie = $.parseJSON(cookie);
			if (cookie == null) {
				cookie = {};
			}
			toggle_cols = [];
			$.each($.parseJSON($('#'+form_id+"_toggle_cols").val()), function(i,v){
				toggle_cols.push(i);
			});
			cookie[form_id] = toggle_cols;
			$.cookie('toggle_cols', $.toJSON(cookie), { expires: 7 });
		} else {
			cookie = $.cookie("toggle_cols");
			cookie = $.parseJSON(cookie);
			if (cookie != null){
				toggle_cols = cookie[form_id];
				if (toggle_cols == null) {
					toggle_cols = [];
					$.each($.parseJSON($('#'+form_id+"_toggle_cols").val()), function(i,v){
						if(v['toggle']) toggle_cols.push(i);
					});
				} else {
					if($(this).hasClass('enabled')){
						toggle_cols.splice(toggle_cols.indexOf(col_id), 1);
					}
					else {
						toggle_cols.push(col_id);
					}
				}
			} else {
				cookie = {};
				toggle_cols = [];
				$.each($.parseJSON($('#'+form_id+"_toggle_cols").val()), function(i,v){
					if(v['toggle']) toggle_cols.push(i);
				});
				if($(this).hasClass('enabled')){
					toggle_cols.splice(toggle_cols.indexOf(col_id), 1);
				}
				else {
					toggle_cols.push(col_id);
				}
			}
			cookie[form_id] = toggle_cols;
			$.cookie('toggle_cols', $.toJSON(cookie), { expires: 7 });
		}
		stored_form_action = $(form).attr("action");
		$(form).attr("action", window.location.href);
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		options = {
			target: $(form).children(".bika-listing-table"),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				setoddeven();
			}
		}
		$(".tooltip").remove();
		form.ajaxSubmit(options);
		$('[name=table_only]').remove();
		$(form).attr('action', stored_form_action);
		return false;
	});

});
});
