(function( $ ) {

jarn.i18n.loadCatalog('bika');
window.jsi18n_bika = jarn.i18n.MessageFactory('bika');
jarn.i18n.loadCatalog('plone');
window.jsi18n_plone = jarn.i18n.MessageFactory('plone');

var bika_utils = bika_utils || {

	init: function () {
		if ('localStorage' in window && window.localStorage !== null) {
			bika_utils.storage = localStorage;
		} else {
			bika_utils.storage = {};
		}
		t = new Date().getTime();
		stored_counter = bika_utils.storage['bika_bsc_counter'];
		$.getJSON(portal_url+'/bika_bsc_counter?'+t, function(counter) {
			if (counter != stored_counter){
				$.getJSON(portal_url+'/bika_browserdata?'+t, function(data){
					bika_utils.storage['bika_bsc_counter'] = counter;
					bika_utils.storage['bika_browserdata'] = $.toJSON(data);
					bika_utils.data = data;
				});
			} else {
				bika_utils.data = $.parseJSON(bika_utils.storage['bika_browserdata']);
			}
		});
	},

	portalMessage: function(message) {
		str = "<dl class='portalMessage error'>"+
			"<dt>"+window.jsi18n_bika('Error')+"</dt>"+
			"<dd><ul>" + window.jsi18n_bika(message) +
			"</ul></dd></dl>";
		$('.portalMessage').remove();
		$(str).appendTo('#viewlet-above-content');
	}
}

bika_utils.init();
window.bika_utils = bika_utils;

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

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

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

	$('input.datepicker_2months').live('click', function() {
		$(this).datepicker({
			showOn:'focus',
			showAnim:'',
			dateFormat:'dd M yy',
			changeMonth:true,
			changeYear:true,
			maxDate: '+0d',
			numberOfMonths: 2
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

	// Archetypes :int inputs get numeric class
	$("input[name*='\\:int']").addClass('numeric');

});
}(jQuery));
