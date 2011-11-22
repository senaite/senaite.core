jQuery( function($) {
$(document).ready(function(){

	// review_state
	$(".review_state_selector a").click(function(){
		form_id = $(this).parents("form").attr("id");
		review_state = $(this).attr("value");
		window.location.href = window.location.href.split("?")[0] +
		                       $.query.set(form_id + "_review_state", review_state);
		return false;
	});

	// pagesize
	$("select[name='pagesize']").live('change', function(){
		form_id = $(this).parents("form").attr("id");
		pagesize = $(this).val();
		window.location.href = window.location.href.split("?")[0] +
		                       $.query.set(form_id + "_pagesize", pagesize);
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

	// Click column header - set or modify sort order.
	$("th.sortable").click(function(){
		form_id = $(this).parents("form").attr("id");
		column_id = this.id.split("-")[1];
		sort_on = $.query.get(form_id + "_" + "sort_on");
		sort_order = $.query.get(form_id + "_" + "sort_order");
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
		// remove sort_on class from any previously sort_on columns
		window.location.href = window.location.href.split("?")[0] +
		                       $.query.set(form_id + "_" + "sort_on", sort_on)
									  .set(form_id + "_" + "sort_order", sort_order);
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

	// batching pagenumber links
	$("a[pagenumber]").click(function(){
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

});
});
