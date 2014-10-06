/**
 * Controller class for BikaSetup Edit view
 */
function BikaSetupEditView() {

    var that = this;

    var restrict_useraccess  = $('#archetypes-fieldname-RestrictWorksheetUsersAccess #RestrictWorksheetUsersAccess');
    var restrict_wsmanagement = $('#archetypes-fieldname-RestrictWorksheetManagement #RestrictWorksheetManagement');

    /**
     * Entry-point method for BikaSetupEditView
     */
    that.load = function() {

        $(restrict_useraccess).change(function() {

            if ($(this).is(':checked')) {

                // If checked, the checkbox for restrict the management
                // of worksheets must be checked too and readonly
                $(restrict_wsmanagement).prop('checked', true);
                $(restrict_wsmanagement).click(function(e) {
                    e.preventDefault();
                });

            } else {

                // The user must be able to 'un-restrict' the worksheet
                // management
                $(restrict_wsmanagement).unbind("click");

            }
        });

        $(restrict_useraccess).change();
    }
}
