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

		// All jquery autocomplete widgets get a down-arrow keypress when
		// double clicked
		//	this is terrible
		$("input[class~='ui-autocomplete-input']").live('click', function(){
			$(this).trigger({type:'keydown', which:40});
			$(this).trigger({type:'keyup', which:40});
		});


	});

});


