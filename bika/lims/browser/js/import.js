(function( $ ) {
$(document).ready(function(){

	_ = jarn.i18n.MessageFactory('bika');
	PMF = jarn.i18n.MessageFactory('plone');

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
				$("#intermediate").empty()
				if(responseText['errors'].length > 0){
					str = "<h3>"+ _("Errors found") + "</h3><ul class='errors'>"					
					$.each(responseText['errors'], function(i,v){
						str = str + "<li>" + v + "</li>";
					});
					str = str + "</ul>";
					$("#intermediate").append(str).toggle(true);
				}
				if(responseText['log'].length > 0){
					str = "<h3>"+ _("Log trace") + "</h3><ul>"
					$.each(responseText['log'], function(i,v){
						str = str + "<li>" + v + "</li>";
					});
					str = str + "</ul>";
					$("#intermediate").append(str).toggle(true);
				}
			}
		}
		form.ajaxSubmit(options);
		return false;
	});

});
}(jQuery));
