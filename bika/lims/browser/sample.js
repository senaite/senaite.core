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
            complete: function(XMLHttpRequest, textStatus) {
                $("input[class~='context']").removeAttr('disabled');
                $("#spinner").toggle(false);
            },
            success: function(responseText, statusText, xhr, $form)  {  
                if(responseText['success'] != undefined){
                    window.location.replace(window.location.href.replace("/base_edit","/base_view"));
                }
                msg = ""
                if(responseText['errors'] != undefined){
                    for(error in responseText['errors']){
                        x = error.split(".");
                        if (x.length == 2){
                            e = x[1] + " (Column " + x[0] + "): ";
                        } else {
                            e = "";
                        }
                        msg = msg + e + responseText['errors'][error] + "<br/>";
                    };
                    portalMessage(msg);
                }
                window.scroll(0,0);
            },
            error: function(XMLHttpRequest, statusText, errorThrown) {
                portalMessage(statusText);
            },
        };

        $('#edit_form').ajaxForm(options);

	});
});
