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
