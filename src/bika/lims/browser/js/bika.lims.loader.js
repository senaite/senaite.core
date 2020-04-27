window.bika = window.bika || { lims: {} };

/**
 * Dictionary of JS objects to be loaded at runtime.
 * The key is the DOM element to look for in the current page. The
 * values are the JS objects to be loaded if a match is found in the
 * page for the specified key. The loader initializes the JS objects
 * following the order of the dictionary.
 */
window.bika.lims.controllers =  {

    /** JS Utilities **/

    "html":
        ['CommonUtils'],

    // Barcode utils
    ".barcode, .qrcode":
        ['BarcodeUtils'],

    // Range graphics
    ".range-chart":
        ['RangeGraph'],

    // Atachments
    ".attachments":
        ['AttachmentsUtils'],

    /** JS objects to be loaded always **/

    "body":
        ['SiteView'],


    /** JS objects to be loaded on specific views or pages **/

    // Methods
    ".portaltype-method.template-base_edit":
        ['MethodEditView'],

    // Analysis Services
    ".portaltype-analysisservice.template-base_edit":
        ['AnalysisServiceEditView'],

    // Analysis Profile
    ".portaltype-analysisprofile.template-base_edit":
        ['AnalysisProfileEditView'],

    // Instruments
    ".portaltype-instrument.template-referenceanalyses":
        ['InstrumentReferenceAnalysesView'],

    ".portaltype-instrumentcertification.template-base_edit":
        ['InstrumentCertificationEditView'],

    ".portaltype-instrument.template-base_edit":
            ['InstrumentEditView'],

    // Editing a calculation
    ".portaltype-calculation":
        ['CalculationEditView'],

    // Bika Setup
    ".portaltype-bikasetup.template-base_edit":
        ['BikaSetupEditView'],


    // Clients
    ".portaltype-client.template-base_edit":
        ['ClientEditView'],

    "div.overlay #client-base-edit":
        ['ClientOverlayHandler'],

    // Reference Samples
    ".portaltype-referencesample.template-analyses":
        ['ReferenceSampleAnalysesView'],

    // Analysis Request Templates
    ".portaltype-artemplate.template-base_edit":
        ['ARTemplateEditView'],

    // Analysis Requests
    ".portaltype-analysisrequest":
        ['AnalysisRequestView',
     ],
     // Analysis request, but not in ARAdd view
     ".portaltype-analysisrequest:not(.template-ar_add)":
        ['RejectionKickOff',],

    ".portaltype-analysisrequest.template-base_view":
        ['WorksheetManageResultsView',
         'AnalysisRequestViewView',
         'AnalysisRequestManageResultsView',
         'RejectionKickOff',],

    ".portaltype-analysisrequest.template-manage_results":
        ['WorksheetManageResultsView',
         'AnalysisRequestManageResultsView'],

    ".portaltype-analysisrequest.template-analyses":
        ['AnalysisRequestAnalysesView'],

	// Common and utilities for AR Add forms
	".portaltype-analysisrequest.template-ar_add": ['AnalysisRequestAddView'],

  // AR Add 2
	"#analysisrequest_add_form": ['AnalysisRequestAdd'],

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

    ".portaltype-worksheet.template-add_blank":
        ['WorksheetAddQCAnalysesView'],

    ".portaltype-worksheet.template-add_control":
        ['WorksheetAddQCAnalysesView'],

    ".portaltype-worksheet.template-add_duplicate":
        ['WorksheetAddDuplicateAnalysesView'],

    ".portaltype-worksheet.template-manage_results":
        ['WorksheetManageResultsView'],

    ".portaltype-worksheettemplate.template-base_edit":
        ['WorksheetTemplateEdit'],

    "#worksheet-printview-wrapper":
        ['WorksheetPrintView'],

    ".portaltype-reflexrule.template-base_edit":
        ['ReflexRuleEditView'],

    ".template-labcontacts.portaltype-department":
        ['DepartmentLabContactsView'],

    // Reports folder (not AR Reports)
    ".portaltype-reportfolder":
        ['ReportFolderView'],

    // If RemarksWidget is in use on this page,
    // load RemarksWIdgetview
    ".ArchetypesRemarksWidget": ["RemarksWidgetView"],

    // Add here your view-controller/s assignment

};



var _bika_lims_loaded_js = new Array();

/**
 * Initializes only the js controllers needed for the current view.
 * Initializes the JS objects from the controllers dictionary for which
 * there is at least one match with the dict key. The JS objects are
 * loaded in the same order as defined in the controllers dict.
 */
window.bika.lims.initview = function() {
    return window.bika.lims.loadControllers(false, []);
};
/**
 * 'all' is a bool variable used to load all the controllers.
 * 'controllerKeys' is an array which contains specific controllers' keys which aren't
 * in the current view, but you want to be loaded anyway. To deal with overlay
 * widgets, for example.
 * Calling the function "loadControllers(false, [array with desied JS controllers keys from
 * window.bika.lims.controllers])", allows you to force bika to load/reload JS controllers defined inside the array.
 */
window.bika.lims.loadControllers = function(all, controllerKeys) {
    var controllers = window.bika.lims.controllers;
    var prev = _bika_lims_loaded_js.length;
    for (var key in controllers) {
        // Check if the key have value. Also check if this key exists in the controllerKeys array.
        // If controllerKeys contains the key, the JS controllers defined inside window.bika.lims.controllers
        // and indexed with that key will be reloaded/loaded (wherever you are.)
        if ($(key).length || $.inArray(key, controllerKeys) >= 0) {
            controllers[key].forEach(function(js) {
                if (all == true || $.inArray(key, controllerKeys) >= 0 || $.inArray(js, _bika_lims_loaded_js) < 0) {
                    console.debug('[bika.lims.loader] Loading '+js);
                    obj = new window[js]();
                    obj.load();
                    // Register the object for further access
                    window.bika.lims[js]=obj;
                    _bika_lims_loaded_js.push(js);
                }
            });
        }
    }
    return _bika_lims_loaded_js.length - prev;

};

window.bika.lims.initialized = false;
/**
 * Initializes all bika.lims js stuff
 */
window.bika.lims.initialize = function() {
    return window.bika.lims.initview();
};

window.jarn.i18n.loadCatalog("senaite.core");
window.jarn.i18n.loadCatalog("plone");
var _ = window.jarn.i18n.MessageFactory("senaite.core");
var PMF = jarn.i18n.MessageFactory('plone');


(function( $ ) {
$(document).ready(function(){

    // Initializes bika.lims
    var length = window.bika.lims.initialize();
    window.bika.lims.initialized = true;

});
}(jQuery));
