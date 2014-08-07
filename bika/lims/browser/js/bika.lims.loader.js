/**
 * Dictionary of JS objects to be loaded at runtime.
 * The key is the DOM element to look for in the current page. The
 * values are the JS objects to be loaded if a match is found in the
 * page for the specified key. The loader initializes the JS objects
 * following the order of the dictionary.
 */
window.bika.lims.controllers =  {

    /** JS objects to be loaded always **/
    "body":
        ['SiteView'],


    /** JS objects to be loaded on specific views or pages **/

    // Calculation events
    ".ajax_calculate":
        ['CalculationEvents'],


    // Bika Listing Table
    "table.bika-listing-table":
        ['BikaListingTableView'],


    // Methods
    ".portaltype-method.template-base_edit":
        ['MethodEditView'],


    // Analysis Services
    ".portaltype-analysisservice.template-base_edit":
        ['AnalysisServiceEditView'],


    // Instruments
    ".portaltype-instrument.template-referenceanalyses":
        ['InstrumentReferenceAnalysesView'],

    ".portaltype-instrumentcertification.template-base_edit":
        ['InstrumentCertificationEditView'],


    // Bika Setup
    ".portaltype-bikasetup.template-base_edit":
        ['BikaSetupEditView'],


    // Clients
    ".portaltype-client.template-base_edit":
        ['ClientEditView'],


    // Reference Samples
    ".portaltype-referencesample.template-analyses":
        ['ReferenceSampleAnalysesView'],


    // Samples
    ".portaltype-sample":
        ['SampleView'],


    // Analysis Request Templates
    ".portaltype-artemplate.template-base_edit":
        ['ARTemplateEditView'],


    // Analysis Requests
    ".portaltype-analysisrequest":
        ['SampleView',
         'AnalysisRequestView'],

    ".portaltype-analysisrequest.template-base_view":
        ['WorksheetManageResultsView',
         'AnalysisRequestViewView',
         'AnalysisRequestManageResultsView'],

    ".portaltype-analysisrequest.template-manage_results":
        ['WorksheetManageResultsView',
         'AnalysisRequestManageResultsView'],

    ".portaltype-analysisrequest.template-analyses":
        ['AnalysisRequestAnalysesView'],

    ".portaltype-analysisrequest.template-ar_add":
        ['AnalysisRequestAddView'],


    // Analysis Request Imports
    ".portaltype-arimport.template-arimport_view":
        ['AnalysisRequestImportView'],

    ".portaltype-arimport.template-base_edit":
        ['AnalysisRequestImportView'],

    "#ar_publish_container":
        ['AnalysisRequestPublishView'],


    // Supply Orders
    ".portaltype-supplyorder.template-base_edit":
        ['SupplyOrderEditView'],


    // Imports
    ".portaltype-plone-site.template-import":
        ['InstrumentImportView'],


    // Batches
    ".portaltype-batchfolder":
        ['BatchFolderView'],

    // Worksheets
    ".portaltype-worksheetfolder":
        ['WorksheetFolderView'],

    ".portaltype-worksheet.template-add_analyses":
        ['WorksheetAddAnalysesView'],

    ".portaltype-worksheet.template-add_blank":
        ['WorksheetAddQCAnalysesView'],

    ".portaltype-worksheet.template-add_control":
        ['WorksheetAddQCAnalysesView'],

    ".portaltype-worksheet.template-add_duplicate":
        ['WorksheetAddDuplicateAnalysesView'],

    ".portaltype-worksheet.template-manage_results":
        ['WorksheetManageResultsView'],

    // Add here your view-controller/s assignment

};



/**
 * Initializes only the js controllers needed for the current view.
 * Initializes the JS objects from the controllers dictionary for which
 * there is at least one match with the dict key. The JS objects are
 * loaded in the same order as defined in the controllers dict.
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
