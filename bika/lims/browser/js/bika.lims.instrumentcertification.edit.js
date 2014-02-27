/**
 * Controller class for Instrument Certification Edit view
 */
function InstrumentCertificationEditView() {

    var that = this;

    /**
     * Entry-point method for InstrumentCertificationEditView
     */
    that.load = function() {

        $('#Internal').live('change', function() {
            loadAgency();
        });

        loadAgency();
    }

    /**
     * Loads the Agency Field. If the certification is set as Internal,
     * the Agency field is hided.
     */
    function loadAgency() {
        if ($('#Internal').is(':checked')) {
            $('#archetypes-fieldname-Agency').hide();
        } else {
            $('#archetypes-fieldname-Agency').fadeIn('slow');
        }
    }
}
