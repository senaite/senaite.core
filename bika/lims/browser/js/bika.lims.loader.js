/**
 * JS responsible of loading the controller classes of views and forms.
 * Must be embedded to the HTML after the rest of javascripts.
 */
(function( $ ) {
$(document).ready(function(){

    // Correlations between views and js classes to be loaded
    var views = {
        ".template-base_edit.portaltype-method":
            ['MethodEditView'],
        ".template-base_edit.portaltype-analysisservice":
            ['AnalysisServiceEditView'],
        ".template-base_edit.portaltype-instrumentcertification":
            ['InstrumentCertificationEditView'],
        ".template-base_edit.portaltype-bikasetup":
            ['BikaSetupEditView']
    };

    // Instantiate the js objects needed for the current view
    var loaded = new Array();
    for (var key in views) {
        if ($(key).length) {
            views[key].forEach(function(js) {
                if ($.inArray(js, loaded) < 0) {
                    obj = new window[js]();
                    obj.load();
                    loaded.push(js);
                }
            });
        }
    }
});
}(jQuery));
