/**
 * Controller class for Client's Edit view
 */
function ClientEditView() {
    const that = this;

    const $decimalMarkField = $("#archetypes-fieldname-DecimalMark");
    const $decimalMarkToggle = $("#DefaultDecimalMark");

    /**
     * Entry-point method
     */
    that.load = function () {
        initializeDecimalMarkBehavior();
    };

    /**
     * Controls visibility of DecimalMark field based on toggle
     */
    function initializeDecimalMarkBehavior() {
        toggleDecimalMarkVisibility($decimalMarkToggle.is(":checked"));

        $decimalMarkToggle.on("change", function () {
            toggleDecimalMarkVisibility($(this).is(":checked"));
        });
    }

    function toggleDecimalMarkVisibility(isChecked) {
        if (isChecked) {
            $decimalMarkField.fadeOut();
        } else {
            $decimalMarkField.fadeIn();
        }
    }
}
