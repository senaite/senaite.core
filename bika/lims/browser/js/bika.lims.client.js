/**
 * Controller class for Client's Edit view
 */
function ClientEditView() {

    var that = this;
    var acheck = "#archetypes-fieldname-DecimalMark";
    var check  = "#DefaultDecimalMark"

    /**
     * Entry-point method for ClientEditView
     */
    that.load = function() {

        loadDecimalMarkBehavior();

    }

    /**
     * When the Avoid Client's Decimal Mark Selection checkbox is set,
     * the function will disable Select Decimal Mark dropdown list.
     */
    function loadDecimalMarkBehavior() {

        loadDMVisibility($(check));

        $(check).click(function(){
            loadDMVisibility($(this));
        });

        function loadDMVisibility(dmcheck) {
            if (dmcheck.is(':checked')) {
                $(acheck).fadeOut().hide();
            } else {
                $(acheck).fadeIn();

            }
        }
    }
}
/**
* Client's overlay edit view Handler. Used by add buttons to
* manage the behaviour of the overlay.
*/
function ClientOverlayHandler() {
  var that = this;

  // Needed for bika.lims.loader to register the object at runtime
  that.load = function() {}

  /**
   * Event fired on overlay.onLoad()
   * Hides undesired contents from inside the overlay and also
   * loads additional javascripts still not managed by the bika.lims
   * loader
   */
  that.onLoad = function(event) {

      // Address widget
      $.ajax({
          url: 'bika_widgets/addresswidget.js',
          dataType: 'script',
          async: false
      });
  }
}

function ClientSamplesView() {
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
        // Getting the url
        var href = $('a.context_action_link').attr('href');
        if (s_uids.length < 1) {
            window.location.href = $('base').attr('href') + href;
        }
        else {
            href += "?items=";
            // Add the uids in the url and redirect
            window.location.href = $('base').attr('href') + href + s_uids.join();
        }
    }
}