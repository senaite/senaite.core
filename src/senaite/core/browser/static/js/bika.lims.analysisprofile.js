/**
 * Controller class for Analysis Profile Edit view
 */
function AnalysisProfileEditView() {

    var that = this;

    var price_fd = $('#archetypes-fieldname-AnalysisProfilePrice');
    var price_in = $('#archetypes-fieldname-AnalysisProfilePrice #AnalysisProfilePrice');
    var vat_fd = $('#archetypes-fieldname-AnalysisProfileVAT');
    var vat_in = $('#archetypes-fieldname-AnalysisProfileVAT #AnalysisProfileVAT');
    var useprice_chk = $('#archetypes-fieldname-UseAnalysisProfilePrice #UseAnalysisProfilePrice');

    /**
     * Entry-point method for AnalysisProfileEditView
     */
    that.load = function() {
        $(useprice_chk).change(function() {
            if ($(this).is(':checked')) {
                $(price_fd).show();
                $(vat_fd).show();
            } else {
                $(price_fd).hide();
                $(vat_fd).hide();
                $(price_in).val('0');
                $(vat_in).val('0');
            }
        });
        $(useprice_chk).change();
    }
}
