window.bika.lims.controllers =  {

    "body":
        ['SiteView'],

    ".template-base_edit.portaltype-method":
        ['MethodEditView'],

    ".template-base_edit.portaltype-analysisservice":
        ['AnalysisServiceEditView'],

    ".template-base_edit.portaltype-instrumentcertification":
        ['InstrumentCertificationEditView'],

    ".template-base_edit.portaltype-bikasetup":
        ['BikaSetupEditView'],

    "#ar_publish_container":
        ['AnalysisRequestPublishView'],

    ".template-base_edit.portaltype-artemplate":
        ['ARTemplateEditView'],

    ".template-base_edit.portaltype-client":
        ['ClientEditView'],

    ".template-referenceanalyses.portaltype-instrument":
        ['InstrumentReferenceAnalysesView'],

    ".template-analyses.portaltype-referencesample":
        ['ReferenceSampleAnalysesView'],

    ".template-manage_results.portaltype-analysisrequest":
        ['AnalysisRequestManageResultsView'],

    ".template-base_view.portaltype-analysisrequest":
        ['AnalysisRequestViewView']

    // Add here your view-controller/s assignment

};

/**
 * Initializes only the js controllers needed for the current view
 */
window.bika.lims.initview = function() {
    var loaded = new Array();
    var controllers = window.bika.lims.controllers;
    for (var key in controllers) {
        if ($(key).length) {
            controllers[key].forEach(function(js) {
                if ($.inArray(js, loaded) < 0) {
                    console.debug('[bika.lims.loader] Loading '+js);
                    try {
                        obj = new window[js]();
                        obj.load();
                        loaded.push(js);
                    } catch (e) {
                       // statements to handle any exceptions
                       console.warn('[bika.lims.loader] Unable to load '+js+": "+ e.message);
                    }
                }
            });
        }
    }
    return loaded.length;
};

/**
 * Initializes all bika.lims js stuff
 */
window.bika.lims.initialize = function() {
    return window.bika.lims.initview();
};


(function( $ ) {
$(document).ready(function(){

    // Initializes bika.lims
    window.bika.lims.initialize();

});
}(jQuery));
