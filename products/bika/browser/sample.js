jQuery( function($) {
	
	$(document).ready(function(){
		$("#DateSampled").datepicker({'dateFormat': 'yy-mm-dd', showAnim: ''});
		$(".sampletype").autocomplete({ minLength: 0, source: autocomplete_sampletype});
		$(".samplepoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});
	});
});
