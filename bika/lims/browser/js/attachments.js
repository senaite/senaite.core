jQuery( function($) {
$(document).ready(function(){

	// Worksheets need to check these before enabling Add button
    $("#AttachFile,#Service,#Analysis").change(function(event){
        attachfile = $("#AttachFile").val();
        if(attachfile == undefined){attachfile = '';}
        service = $("#Service").val();
        if(service == undefined){service = '';}
        analysis = $("#Analysis").val();
        if(analysis == undefined){analysis= '';}

        if (this.id == 'Service') {
            $("#Analysis").val('');
        }
        if (this.id == 'Analysis') {
            $("#Service").val('');
        }

        if (attachfile != '' && ((service != '') || (analysis != ''))) {
            $("#addButton").removeAttr("disabled");
        } else {
            $("#addButton").attr("disabled", true);
        }
    });

	// This is the button next to analysis attachments in ARs and Worksheets
	$('.deleteAttachmentButton').live("click", function(){
		attachment_uid = $(this).attr("attachment_uid");
		options = {
			url: 'delete_analysis_attachment',
			type: 'POST',
			success: function(responseText, statusText, xhr, $form) {
				if(responseText == "success"){
					$("span[attachment_uid="+attachment_uid+"]").remove();
				}
			},
			data: {
				'attachment_uid': attachment_uid,
				'_authenticator': $('input[name="_authenticator"]').val()
			},
		}
		$.ajax(options);
	});


});
});


