/**
 * Controller class for Method's Edit view
 */
function MethodEditView() {

    var that = this;

    /**
     * Entry-point method for MethodEditView
     */
    that.load = function() {

        loadInstruments();

        $('#ManualEntryOfResults').change(function() {
            if ($('#_AvailableInstruments option').length == 0
                && $(this).is(':checked') == false) {
                $(this).prop('checked', true);
                return;
            }
        });

    }

    /**
     * Loads the selected instruments for the current method. Merges the
     * items from the Available Instrument multiselect with the
     * Instruments multiselect element. If no instrument is linked to the
     * method, selects and disables the Manual Entry of Results checkbox
     */
    function loadInstruments() {
        $('#archetypes-fieldname-_AvailableInstruments').hide();
        $('#_Instruments').prop('disabled', true);
        $('#_Instruments').css('width', '250px');
        $('#_Instruments option').prop('selected', true);
        if ($('#_Instruments option').length == 0) {
            $('#ManualEntryOfResults').prop('checked', true);
        }
        $('#_AvailableInstruments option').each(function() {
            var uid = $(this).val();
            if ($('#_Instruments option[value="'+uid+'"]').length == 0) {
                $(this).css('color', '#8f8f8f');
                $(this).appendTo('#_Instruments');
            }
        });
    }
}
