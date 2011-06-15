jQuery( function($) {
	
	$(document).ready(function(){
		$("#DateSampled").datepicker({'dateFormat': 'yy-mm-dd', showAnim: ''});
        $("#ClientReference").focus();

        function portalMessage(message){
            str = "<dl class='portalMessage error'>"+
                    "<dt i18n:translate='error'>Error</dt>"+
                    "<dd><ul>" + message +
                    "</ul></dd></dl>";
                    $('.portalMessage').remove();
                    $(str).appendTo('#viewlet-above-content');
        }

        // Sample Edit ajax form submits
        var options = { 
            url: window.location.href,
            dataType:  'json', 
            data: $(this).formToArray(),
            beforeSubmit: function(formData, jqForm, options) {
                $("input[class~='context']").attr('disabled',true);
                $("#spinner").toggle(true);
            },
            success: function(responseText, statusText, xhr, $form)  {  
                window.location.replace(window.location.href.replace("/base_edit","/base_view"));
            },
            error: function(XMLHttpRequest, statusText, errorThrown) {
                $("input[class~='context']").removeAttr('disabled');
                $("#spinner").toggle(false);
                portalMessage(statusText);
            },
        };

        $('#edit_form').ajaxForm(options);

	});
});
