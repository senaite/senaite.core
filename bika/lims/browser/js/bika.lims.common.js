/**
 * Global vars
 */

window.jarn.i18n.loadCatalog("bika");
window.jarn.i18n.loadCatalog("plone");
var _ = window.jarn.i18n.MessageFactory("bika");
var PMF = jarn.i18n.MessageFactory('plone');


/**
 * Global functions
 */
(function( $ ) {
"use strict";

/**
 * Analysis Service dependants and dependencies retrieval
 */
window.bika.lims.AnalysisService = window.bika.lims.AnalysisService || {
    Dependants: function(service_uid){
        var request_data = {
            catalog_name: "bika_setup_catalog",
            UID: service_uid
        };
        var deps = {};
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read(request_data, function(data){
            if (data.objects != null && data.objects.length > 0) {
                deps = data.objects[0].ServiceDependants;
            } else {
                deps = [];
            }
        });
        $.ajaxSetup({async:true});
        return deps;
    },
    Dependencies: function(service_uid){
        var request_data = {
            catalog_name: "bika_setup_catalog",
            UID: service_uid
        };
        var deps = {};
        $.ajaxSetup({async:false});
        window.bika.lims.jsonapi_read(request_data, function(data){
            if (data.objects != null && data.objects.length > 0) {
                deps = data.objects[0].ServiceDependencies;
            } else {
                deps = [];
            }
        });
        $.ajaxSetup({async:true});
        return deps;
    }
};


}(jQuery));
