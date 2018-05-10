/**
 * Controller class for Samples Folder View
 */
function PrintSamplesSheetView() {
    "use strict";
    var that = this;

    that.load = function() {
        $('a.context_action_link').click(print_samples_trigger);
    };
    /**
    * Function fired when Print Sample Sheets is clicked both from
    * Samples Folder View or Client Samples Folder View.
    * It makes a POST of the samples form to print_sampling_sheets.
    *
    * To do so, it first cancels the default action of the Print
    * Samples Sheet anchor. It is a GET to print_sampling_sheets
    * that would override the POST with the consequent data loss.
    * Secondly, the form action is overridden before submitting
    * because by default the POST is made to workflow_action
    */
    function print_samples_trigger(event){
        event.preventDefault();
        $('form#samples')[0].action = 'print_sampling_sheets';
        $('form#samples').submit();
        }
    }
