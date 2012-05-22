(function( $ ) {

var bsc = bsc || {
	init: function () {
		if ('localStorage' in window && window.localStorage !== null) {
			bsc.storage = localStorage;
		} else {
			bsc.storage = {};
		}
		t = new Date().getTime();
		stored_counter = bsc.storage['bsc_counter'];
		$.getJSON(portal_url+'/bsc_counter?'+t, function(counter) {
			if (counter != stored_counter){
				$.getJSON(portal_url+'/bsc_browserdata?'+t, function(data){
					bsc.storage['bsc_counter'] = counter;
					bsc.storage['bsc_browserdata'] = $.toJSON(data);
					bsc.data = data;
				});
			} else {
				bsc.data = $.parseJSON(bsc.storage['bsc_browserdata']);
			}
		});
	}
};
bsc.init();
window.bsc = bsc;

jarn.i18n.loadCatalog('bika');
jarn.i18n.setTTL(3600000); // 1 hour refresh
window.jsi18n = jarn.i18n.MessageFactory('bika');

function enableAddAttachment(this_field) {
	// XX move this to worksheet or AR or wherever it actually belongs
	attachfile = document.getElementById('AttachFile').value
	service = document.getElementById('Service').value
	analysis = document.getElementById('Analysis').value

	if (this_field == 'Analysis') {
		document.getElementById('Service').value = '';
	}
	if (this_field == 'Service') {
		document.getElementById('Analysis').value = '';
	}

	document.getElementById('addButton').disabled = false;
	if (attachfile == '') {
		document.getElementById('addButton').disabled = true
	} else {
		if ((service == '') && (analysis == '')) {
			document.getElementById('addButton').disabled = true
		}
	}

	return
}

$(document).ready(function(){

	_ = window.jsi18n;

	$('input.datepicker').live('click', function() {
		$(this).datepicker({
			showOn:'focus',
			showAnim:'',
			dateFormat:'dd M yy',
			changeMonth:true,
			changeYear:true
		})
		.click(function(){$(this).attr('value', '');})
		.focus();

	});

	$('input.datepicker_nofuture').live('click', function() {
		$(this).datepicker({
			showOn:'focus',
			showAnim:'',
			dateFormat:'dd M yy',
			changeMonth:true,
			changeYear:true,
			maxDate: '+0d'
		})
		.click(function(){$(this).attr('value', '');})
		.focus();
	});

	// Analysis Service popup trigger
	$(".service_title").live('click', function(){
		var dialog = $('<div></div>');
		dialog
			.load(window.portal_url + "/analysisservice_popup",
				{'service_title':$(this).text(),
				 '_authenticator': $('input[name="_authenticator"]').val()}
			)
			.dialog({
				width:450,
				height:450,
				closeText: _("Close"),
				resizable:true,
				title: "<img src='" + window.portal_url + "/++resource++bika.lims.images/analysisservice.png'/>&nbsp;" + $(this).text()
			});
	});

	$('body').append('<div id="global-spinner" class="global-spinner" style="display:none"><img id="img-global-spinner" src="spinner.gif" alt="Loading"/></div>');
	$('#global-spinner')
		.ajaxStart(function() { $(this).toggle(true); })
		.ajaxStop(function() { $(this).toggle(false); });
	// we don't use #kss-spinner but it gets in the way.
	$("#kss-spinner").empty();

	$(".numeric").live('keypress', function(event) {

		// Backspace, tab, enter, end, home, left, right, ., <, >, and -
		// We don't support the del key in Opera because del == . == 46.
		var allowedKeys = [8, 9, 13, 35, 36, 37, 39, 46, 60, 62, 45];
		// IE doesn't support indexOf
		var isAllowedKey = allowedKeys.join(",").match(new RegExp(event.which));
		// Some browsers just don't raise events for control keys. Easy.
		// e.g. Safari backspace.
		if (!event.which || // Control keys in most browsers. e.g. Firefox tab is 0
			(48 <= event.which && event.which <= 57) || // Always 0 through 9
			isAllowedKey) { // Opera assigns values for control keys.
			return;
		} else {
			event.preventDefault();
		}
	});

});
}(jQuery));
