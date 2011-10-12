jQuery( function($) {
	function showMethod(path, service )
	{
	    window.open(path + '/bika_analysisservices/' + service + '/analysis_method','analysismethod', 'toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=400,height=400');
	}

	function enableAddAttachment(this_field) {
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


		$(".numeric").live('keypress', function(event) {
		  // Backspace, tab, enter, end, home, left, right
		  // We don't support the del key in Opera because del == . == 46.
		  var controlKeys = [8, 9, 13, 35, 36, 37, 39, 46];
		  // IE doesn't support indexOf
		  var isControlKey = controlKeys.join(",").match(new RegExp(event.which));
		  // Some browsers just don't raise events for control keys. Easy.
		  // e.g. Safari backspace.
		  if (!event.which || // Control keys in most browsers. e.g. Firefox tab is 0
			  (48 <= event.which && event.which <= 57) || // Always 1 through 9
			  isControlKey) { // Opera assigns values for control keys.
			return;
//			  (48 == event.which && $(this).attr("value")) || // No 0 first digit
		  } else {
			event.preventDefault();
		  }
		});


		// All jquery autocomplete widgets get a down-arrow keypress when
		// double clicked
//		$("input[class~='ui-autocomplete-input']").live('click', function(){
//			$(this).trigger({type:'keydown', which:40});
//			$(this).trigger({type:'keyup', which:40});
//		});


	});

});


