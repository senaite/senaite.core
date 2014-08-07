/**
 * Controller class for calculation events
 */
function AttachmentsUtils() {

    var that = this;

    that.load = function() {

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
                $("#addButton").prop("disabled", true);
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
                        $("span[attachment_uid='"+attachment_uid+"']").remove();
                    }
                },
                data: {
                    'attachment_uid': attachment_uid,
                    '_authenticator': $('input[name="_authenticator"]').val()
                },
            }
            $.ajax(options);
        });

        // Dropdown grid of Analyses in attachment forms
        $("#Analysis" ).combogrid({
            colModel: [{'columnName':'analysis_uid','hidden':true},
                       {'columnName':'slot','width':'10','label':_('Slot')},
                       {'columnName':'service','width':'35','label':_('Service')},
                       {'columnName':'parent','width':'35','label':_('Parent')},
                       {'columnName':'type','width':'20','label':_('Type')}],
            url: window.location.href.replace("/manage_results","") + "/attachAnalyses?_authenticator=" + $('input[name="_authenticator"]').val(),
            showOn: true,
            width: '650px',
            select: function( event, ui ) {
                $( "#Analysis" ).val(ui.item.service + " (slot "+ui.item.slot+")");
                $( "#analysis_uid" ).val(ui.item.analysis_uid);
                $(this).change();
                return false;
            }
        });
    }
}
