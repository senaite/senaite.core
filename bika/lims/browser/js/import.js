(function( $ ) {
$(document).ready(function(){

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

	function portalMessage(messages){
		str = "<dl class='portalMessage error'>"+
			"<dt>"+_('error')+"</dt>"+
			"<dd>";
		$.each(messages, function(i,v){
			str = str + "<ul><li>" + v + "</li></ul>";
		});
		str = str + "</dd></dl>";
		$('.portalMessage').remove();
		$('#viewlet-above-content').append(str);
	}

	// Load import form for selected data interface
    $("#exim").change(function(){
		$('.portalMessage').remove();
		$("#intermediate").toggle(false);
		if($(this).val() == ""){
			$("#import_form").empty();
		} else {
			$("#import_form").load(
				window.location.href.replace("/import", "/getImportTemplate"),
				{'_authenticator': $('input[name="_authenticator"]').val(),
				 'exim': $(this).val()
				})
		}
    });

	// Invoke import
	$("[name='firstsubmit']").live('click',  function(event){
		event.preventDefault();
		$('.portalMessage').remove();
		$("#intermediate").toggle(false);
		form = $(this).parents('form');
		options = {
			target: $('#intermediate'),
			data: form.formToArray(),
			dataType: 'json',
			success: function(responseText, statusText, xhr, $form){

				if(responseText['errors'].length > 0){
					portalMessage(responseText['errors']);
				}
				if(responseText['log'].length > 0){
					str = "<ul>"
					$.each(responseText['log'], function(i,v){
						str = str + "<li>" + v + "</li>";
					});
					str = str + "</ul>";
					$("#intermediate").empty().append(str).toggle(true);
				}
			}
		}
		form.ajaxSubmit(options);
		return false;
	});

});
}(jQuery));
