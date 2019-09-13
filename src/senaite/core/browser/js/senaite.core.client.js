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
