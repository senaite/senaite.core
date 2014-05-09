(function( $ ) {
$(document).ready(function(){

    jarn.i18n.loadCatalog('bika');
    _ = jarn.i18n.MessageFactory('bika');
    jarn.i18n.loadCatalog('plone');
    PMF = jarn.i18n.MessageFactory('plone');

     if($(".portaltype-batch").length == 0 &&
       window.location.href.search('portal_factory/Batch') == -1){
        $("input[id='BatchID']").after('<a style="border-bottom:none !important;margin-left:.5;"' +
                    ' class="add_batch"' +
                    ' href="'+window.portal_url+'/batches/portal_factory/Batch/new/edit"' +
                    ' rel="#overlay">' +
                    ' <img style="padding-bottom:1px;" src="'+window.portal_url+'/++resource++bika.lims.images/add.png"/>' +
                ' </a>');
        $("input[id*='BatchID']").combogrid({
            colModel: [{'columnName':'BatchUID','hidden':true},
                       {'columnName':'BatchID','width':'35','label':_('Batch ID')},
                       {'columnName':'Description','width':'65','label':_('Description')}],
            showOn: true,
            url: window.location.href.replace("/ar_add","") + "/getBatches?_authenticator=" + $('input[name="_authenticator"]').val(),
            select: function( event, ui ) {
                $(this).val(ui.item.BatchID);
                $(this).change();
                return false;
            }
        });
    }

    $('a.add_batch').prepOverlay(
        {
            subtype: 'ajax',
            filter: 'head>*,#content>*:not(div.configlet),dl.portalMessage.error,dl.portalMessage.info',
            formselector: '#batch-base-edit',
            closeselector: '[name="form.button.cancel"]',
            width:'70%',
            noform:'close',
            config: {
                closeOnEsc: false,
                onLoad: function() {
                    // manually remove remarks
                    this.getOverlay().find("#archetypes-fieldname-Remarks").remove();
//                  // display only first tab's fields
//                  $("ul.formTabs").remove();
//                  $("#fieldset-schemaname").remove();
                },
            }
        }
    );

    /**
     * Modal confirmation when user clicks on 'cancel' active button.
     * Used on batch folder views
     */
    $(".portaltype-batchfolder").append("" +
            "<div id='batch-cancel-dialog' title='"+_("Cancel batch/es?")+"'>" +
            "    <p style='padding:10px'>" +
            "        <span class='ui-icon ui-icon-alert' style=''float: left; margin: 0 7px 30px 0;'><br/></span>" +
            "        "+_("All linked Analysis Requests will be cancelled too.") +
            "    </p>" +
            "    <p style='padding:0px 10px'>" +
            "       "+_("Are you sure?") +
            "    </p>" +
            "</div>" +
            "<input id='batch-cancel-resp' type='hidden' value='false'/>");
    $("#batch-cancel-dialog").dialog({
        autoOpen:false,
        resizable: false,
        height:200,
        width:400,
        modal: true,
        buttons: {
            "Cancel selected batches": function() {
                $(this).dialog("close");
                $("#batch-cancel-resp").val('true');
                $(".portaltype-batchfolder #cancel_transition").click();
            },
            Cancel: function() {
                $("#batch-cancel-resp").val('false');
                $(this).dialog("close");
            }
        }
    });
    $(".portaltype-batchfolder #cancel_transition").click(function(event){
       if ($(".bika-listing-table input[type='checkbox']:checked").length) {
           if ($("#batch-cancel-resp").val() == 'true') {
               return true;
           } else {
               event.preventDefault();
               $("#batch-cancel-dialog").dialog("open");
               return false;
           }
       } else {
           return false;
       }
    });
});
}(jQuery));
