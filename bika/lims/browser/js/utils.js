jQuery( function($) {
	function showMethod(path, service )
	{
	    window.open(path + '/bika_analysisservices/' + service + '/analysis_method','analysismethod', 'toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=400,height=400');
	}

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

		if ( ! window.jsi18n) {
			// jarn.i18n.setTTL(1000); // testing 10 seconds
			jarn.i18n.loadCatalog('bika');
			window.jsi18n = jarn.i18n.MessageFactory('bika');
		}
		_ = window.jsi18n;

		$('input.datepicker').live('click', function() {
			$(this).datepicker({
				showOn:'focus',
				showAnim:'',
				dateFormat:'dd M yy',
				changeMonth:true,
				changeYear:true
			}).focus();
		});

		$('input.datepicker_nofuture').live('click', function() {
			$(this).datepicker({
				showOn:'focus',
				showAnim:'',
				dateFormat:'dd M yy',
				changeMonth:true,
				changeYear:true,
				maxDate: '+0d'
			}).focus();
		});

		$('body').append('<div id="global-spinner" class="global-spinner" style="display:none"><img id="img-global-spinner" src="spinner.gif" alt="Loading"/></div>');
		$('#global-spinner')
			.ajaxStart(function() { $(this).toggle(true); })
			.ajaxStop(function() { $(this).toggle(false); });
		// we don't use #kss-spinner but it gets in the way.
		$("#kss-spinner").empty();

		$(".numeric").live('keypress', function(event) {

		//console.log("got " + event.which);

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
//			  (48 == event.which && $(this).attr("value")) || // No 0 first digit
		  } else {
			event.preventDefault();
		  }
		});
	});

});


