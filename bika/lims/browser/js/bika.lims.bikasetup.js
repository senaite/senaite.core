/**
 * Controller class for BikaSetup Edit view
 */
function BikaSetupEditView() {

    var that = this;

    var restrict_useraccess = $('#archetypes-fieldname-RestrictWorksheetUsersAccess #RestrictWorksheetUsersAccess');
    var restrict_wsmanagement = $('#archetypes-fieldname-RestrictWorksheetManagement #RestrictWorksheetManagement');

    /**
     * Entry-point method for BikaSetupEditView
     */
    that.load = function () {
        // Controller to avoid introducing no accepted prefix separator.
        $('input[id^="Prefixes-separator-"]').each(function() {
            toSelectionList(this);
        });
        // After modify the selection list, the hidden input should update its own value with the
        // selected value on the list
        $('select[id^="Prefixes-separator-"]').bind('select change', function () {
            var selection = $(this).val();
            var id = $(this).attr('id');
            $('input#'+id).val(selection)
        });

        $(restrict_useraccess).change(function () {

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
    };

    function toSelectionList(pointer) {
        /*
        The function generates a selection list to choose the prefix separator. Doing that, we can be
        sure that the user will only be able to select a correct separator.
         */
        var def_value = pointer.value;
        var current_id = pointer.id;
        // Allowed separators
        var allowed_elements = ['','-','_'];
        var selectbox = '<select id="'+current_id+'">'+'</select>';
        $(pointer).after(selectbox);
        $(pointer).hide();
        for(var i = 0; i < allowed_elements.length; i++) {
            var selected = 'selected';
            if (allowed_elements[i] != def_value) {selected = ''}
            var option =  "<option "+selected+" value="+allowed_elements[i]+">"+allowed_elements[i]+"</option>";
            $('select#'+current_id).append(option)
        }
    }
}

