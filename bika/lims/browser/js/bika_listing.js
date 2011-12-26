jQuery( function($) {
$(document).ready(function(){

	function portalMessage(message){
		str = "<dl class='portalMessage error'>"+
			"<dt i18n:translate='error'>Error</dt>"+
			"<dd><ul>" + message +
			"</ul></dd></dl>";
		$('.portalMessage').remove();
		$(str).appendTo('#viewlet-above-content');
	}

	function setoddeven() {
		var tbody = $(this);
		// jquery :odd and :even are 0 based
		tbody.find('tr').removeClass('odd').removeClass('even')
			.filter(':odd').addClass('even').end()
			.filter(':even').addClass('odd');
	}

	function sortabledataclass(cell){
		var re = new RegExp("sortabledata-([^ ]*)","g");
		var matches = re.exec(cell.attr('class'));
		if(matches) return matches[1]
		else return null
	}

	function sortable(cell) {
		// convert a cell a to something sortable
		// use sortabledata-xxx cell class if it is defined
		var text = sortabledataclass(cell);
		if(text == null) {
			text = cell.text();
		}
		text = text.toLowerCase().replace(/[^a-zA-Z0-9_]*/mg, "");
		// A number, but not a date?
		if (!isNaN(parseFloat(text)))
			return parseFloat(text);
		return text;
	}

	// review_state
	$(".review_state_selector a").live('click', function(){
		form = $(this).parents("form");
		form_id = $(form).attr("id");
		review_state = $(this).attr("value");
		$("[name="+form_id+"_review_state]").val(review_state);
		stored_form_action = $(form).attr("action");
		$(form).attr("action", $($("[name=view_url]")[0]).val());
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
// XXX formToArray() includes entire form - must slim the request down to what is required
//		formArray = form.formToArray();
//		formData = {};
//		$.each(formArray, function(i, v){
//			// only pass the things we need in the request
//			if (v['name'].search(form_id+"_")==0){
//				formData[v['name']] = v['value'];
//			}
//			if(v['name'] == '_authenticator' ||
//			   v['name'] == 'view_url' ||
//			   v['name'] == 'form_id' ||
//			   v['name'] == 'submitted' ||
//			   v['name'] == 'table_only') {
//				formData[v['name']] = v['value'];
//			}
//		})
		options = {
			target: $(this).parents("table"),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				//$("#spinner").toggle(false);
			}
		}
		//$("#spinner").toggle(true);
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
		// reset these values in the form (ajax and in-place sort use them)
		$(sort_on_selector).val(sort_on);
		$(sort_order_selector).val(sort_order);

		// request ajax re-sort for indexed columns
		if ($(this).hasClass('indexed')) {
			// request new table content
			stored_form_action = $(form).attr("action");
			$(form).attr("action", $($("[name=view_url]")[0]).val());
			$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
			options = {
				target: $(this).parents("table"),
				replaceTarget: true,
				data: form.formToArray(),
				success: function(){
					//$("#spinner").toggle(false);
				}
			}
			//$("#spinner").toggle(true);
			form.ajaxSubmit(options);
			$("[name=table_only]").remove();
			$(form).attr("action", stored_form_action);
		} else {
			// inline sort cribbed from plone/table_sorter.js
			th = $(this).closest('th');
			colnum = $('th', $(this).closest('thead')).index(th);
			table = $(this).parents('table:first');
			tbody = table.children('tbody');
		    index = $(this).parent().children('th').index(this);
			data = [];
			usenumbers = true;
			tbody.children('tr').each(function() {
				cell = $(this).children('td')[index];
				sortableitem = sortable($(cell));
				if (isNaN(sortableitem)) {
					usenumbers = false;
				}
				data.push([sortableitem, this]);
			});
			if (data.length) {
				if (usenumbers) {
					data.sort(function(a,b) {return a[0]-b[0];});
				} else {
					data.sort();
				}
				if (sort_order=='descending') data.reverse();
				// remove sort_on from all TH siblings
				table.find('th').each(function(){
					$(this).removeClass('sort_on');
					$(this).removeClass('ascending');
					$(this).removeClass('descending');
				});
				// add sort_on and sort order classes to ourself
				th.addClass('sort_on');
				th.addClass(sort_order);
				tbody.find('tr').remove();
				// appending the tr nodes in sorted order will remove them from their old ordering
				tbody.append($.map(data, function(a) { return a[1]; }));
				// jquery :odd and :even are 0 based
				setoddeven(tbody);
			}
		}
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
		form_id = $(this).parents("form").attr("id");
		pagesize = $(this).val();
		window.location.href = window.location.href.split("?")[0] +
		                       $.query.set(form_id + "_pagesize", pagesize);
	});

	// batching pagenumber links
	$("a[pagenumber]").live('click', function(){
		form_id = $(this).parents("form").attr("id");
		pagenumber = $(this).attr("pagenumber");
		window.location.href = window.location.href.split("?")[0] +
		                       $.query.set(form_id + "_pagenumber", pagenumber);
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
	$('.filter-search-button,.filter-search-clear').live('click', function(event){
		if ($(this).hasClass('filter-search-clear')){
			$('.filter-search-input').val('');
		}
		form = $(this).parents('form');
		form_id = $(form).attr('id');
		stored_form_action = $(form).attr("action");
		$(form).attr("action", $($("[name=view_url]")[0]).val());
		$(form).append("<input type='hidden' name='table_only' value='"+form_id+"'>");
		options = {
			target: $(this).parents('table'),
			replaceTarget: true,
			data: form.formToArray(),
			success: function(){
				//$("#spinner").toggle(false);
			}
		}
		//$("#spinner").toggle(true);
		form.ajaxSubmit(options);
		$('[name=table_only]').remove();
		$(form).attr('action', stored_form_action)
		return false;
	});

	// wait for all .busy (calculating) elements to lose their busy class
	$('.workflow_action_button').live('click', function(event){
		r = 0;
		for(r=0;r<15;r++){
			busy = $('.busy');
			if(busy.length == 0){
				break;
			}
		}
		if(r == 14){
			portalMessage("Some results failed to calculate, and the form was not submitted.");
			$('.busy').removeClass('busy');
			return false;
		}
	});

});
});
