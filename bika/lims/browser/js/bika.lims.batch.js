/**
 * Controller class for Batch Folder View
 */
function BatchFolderView() {

    var that = this;

    that.load = function() {

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

        $("#cancel_transition").click(function(event){
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
    }
}
