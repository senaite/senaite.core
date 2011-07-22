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

	$('#edit_form').ajaxForm({
		url: window.location.href,
		dataType:  'json',
		data: $(this).formToArray(),
		beforeSubmit: function(formData, jqForm, options) {
			$("input[class~='context']").attr('disabled',true);
			$("#spinner").toggle(true);
		},
		success: function(responseText, statusText, xhr, $form)  {
			if (responseText['success'] != undefined) {
				window.location.replace(window.location.href.replace("/base_edit", "/base_view"));
			}
			else {
				portalMessage(responseText['errors'].join("<br/>"));
				window.scroll(0, 0);
				$("input[class~='context']").removeAttr('disabled');
				$("#spinner").toggle(false);
			}
		},
		error: function(XMLHttpRequest, statusText, errorThrown) {
			portalMessage(statusText);
			window.scroll(0, 0);
			$("input[class~='context']").removeAttr('disabled');
			$("#spinner").toggle(false);
		}
	});

	});
});
