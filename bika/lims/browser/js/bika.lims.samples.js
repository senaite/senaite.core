/**
 * Controller class for Samples Folder View
 */
function SamplesFolderView() {
    "use strict";
    var that = this;

    that.load = function() {
        $('a.context_action_link').click(print_samples_trigger);
    };

    function print_samples_trigger(event){
        /*
        This function triggers when the print button is clicked.
        It gets all selected samples and buils the url redirections with
        their uid so the printing function could get back the samples.
        If no samples selected, it shows an error.
        */
        event.preventDefault();
        var s_uids = [];
        // Gets the selected samples if they are in 'scheduled sampling' state or
        // in 'to be sampled' state
        $("input[id^='samples_cb_']:checked").each(function(){
            var tr = $(this).closest('tr');
            var uid = $(tr).attr('uid');
            var tr_state = $(tr).find('.state_title').attr('class');
            if (tr_state.indexOf("state-scheduled_sampling") >= 0 ||
                tr_state.indexOf("state-to_be_sampled") >= 0){
                s_uids.push(uid);
            }
        });
        if (s_uids.length < 1) {
            // give an error
            var message = "At least one selected item in 'scheduled" +
                " sampling' state or 'to be sampled' state is needed to print";
            window.bika.lims.portalMessage(message);
        }
        else {
            // Getting the url
            var href = $('a.context_action_link').attr('href');
            href += "?samples=";
            // Add the uids in the url and redirect
            window.location.href = $('base').attr('href') + href + s_uids.join();
        }
    }
}
