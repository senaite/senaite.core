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

	// a reference definition is selected from the dropdown
	// see referenceresultswidget.js
	$('#ReferenceDefinition\\:list').change(function(){
		ref_def_uid = $(this).val();

		if (ref_def_uid == '') {
			// No reference definition selected; reset widget.
			$('tbody.analysisservices').empty();
			$($('tr[class~="expanded"]').children()[1]).empty()
			$($('tr[class~="expanded"]').children()[2]).empty()
			$($('tr[class~="expanded"]').children()[3]).empty()
			$($('tr[class~="expanded"]').children()[4]).empty()
			$('tr[class~="expanded"]').removeClass("expanded").addClass("initial");
			return;
		}

		$.ajax({
			url: 'get_reference_definition_results',
			dataType: 'json',
			data: {uid: ref_def_uid},
			beforeSubmit: function(formData, jqForm, options) {
				$('#ReferenceDefinition\\:list').attr('disabled',true);
			},
			success: function(responseText, statusText, xhr, $form) {
				if (responseText['results'] != undefined) {
					// Got correct values from server
					results = $.parseJSON(responseText['success']);
					// expand categories
					$.each(responseText['categories'], function(i, cat_uid){
						tr = $('tr[name="'+cat_uid+'"]');
						if (tr.hasClass('collapsed')){ tr.click(); }
					});
					// insert result values
					$.each(responseText['results'], function(i, result){
						$($($('#'+result.uid).children()[1]).children()[0]).val(result['result']);
						$($($('#'+result.uid).children()[2]).children()[0]).val(result['error']);
						$($($('#'+result.uid).children()[3]).children()[0]).val(result['min']);
						$($($('#'+result.uid).children()[4]).children()[0]).val(result['max']);
					});
				}
				else {
					portalMessage(responseText['errors'].join("<br/>"));
					window.scroll(0, 0);
					$('#ReferenceDefinition\\:list').removeAttr('disabled');
				}
			},
			error: function(XMLHttpRequest, statusText, errorThrown) {
				portalMessage(statusText);
				window.scroll(0, 0);
				$('#ReferenceDefinition\\:list').removeAttr('disabled');
			},
		});
	});

	$('#ReferenceDefinition\\:list').change(); // THIS is right, but.
	// The python needs to return values from the existing field, and there needs to be sent
	// a parameter from here to inform python to do so.
	// we don't want python sending us existing ref values, when actually
	// we _wanted_ to reset the values.
});
});
