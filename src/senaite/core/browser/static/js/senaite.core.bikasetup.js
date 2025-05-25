/** Bika Setup Controller
 *
 * This controller is loaded for the old bika setup view, e.g.:
 * `/senaite/bika_setup`
 *
 */
function BikaSetupEditView() {
    const that = this;

    const $restrictUserAccess = $("#archetypes-fieldname-RestrictWorksheetUsersAccess #RestrictWorksheetUsersAccess");
    const $restrictWSManagement = $("#archetypes-fieldname-RestrictWorksheetManagement #RestrictWorksheetManagement");
    const $multiVerificationField = $("#archetypes-fieldname-TypeOfmultiVerification");
    const $numVerificationsSelect = $("#NumberOfRequiredVerifications");

    /**
     * Entry-point method for BikaSetupEditView
     */
    that.load = function () {
        // Handle RestrictWorksheetUsersAccess toggle
        $restrictUserAccess.on("change", function () {
            if ($(this).is(":checked")) {
                $restrictWSManagement.prop("checked", true);
                $restrictWSManagement.on("click.prevent", function (e) {
                    e.preventDefault();
                });
            } else {
                $restrictWSManagement.off("click.prevent");
            }
        });

        // Initial state of multi-verification visibility
        toggleMultiVerificationField($numVerificationsSelect.val());

        // Handle change on NumberOfRequiredVerifications
        $numVerificationsSelect.on("change", function () {
            toggleMultiVerificationField($(this).val());
        });

        // Trigger initial checkbox logic
        $restrictUserAccess.trigger("change");
    };

    /**
     * Show/hide multi-verification type field
     */
    function toggleMultiVerificationField(value) {
        if (parseInt(value, 10) > 1) {
            $multiVerificationField.show();
        } else {
            $multiVerificationField.hide();
        }
    }
}
