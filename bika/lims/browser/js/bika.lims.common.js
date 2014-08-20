/**
 * Global vars
 */

function CommonUtils() {

    var that = this;

    /**
     * Entry-point method for CommonUtils
     */
    that.load = function() {

        window.bika = window.bika || {
            lims: {}
        };

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

        window.bika.lims.portalMessage = function (message) {
            var str = "<dl class='portalMessage error'>"+
                "<dt>"+_("Error")+"</dt>"+
                "<dd><ul>" + message +
                "</ul></dd></dl>";
            $(".portalMessage").remove();
            $(str).appendTo("#viewlet-above-content");
        };

        window.bika.lims.log = function(e) {
            if (window.location.url == undefined || window.location.url == null) {
                return;
            }
            var message = "(" + window.location.url + "): " + e;
            $.ajax({
                type: "POST",
                url: "js_log",
                data: {"message":message,
                        "_authenticator": $("input[name='_authenticator']").val()}
            });
        };

        window.bika.lims.error = function(e) {
            var message = "(" + window.location.href + "): " + e;
            $.ajax({
                type: "POST",
                url: "js_err",
                data: {"message":message,
                        "_authenticator": $("input[name='_authenticator']").val()}
            });
        };

        window.bika.lims.jsonapi_cache = {};
        window.bika.lims.jsonapi_read = function(request_data, handler) {
            window.bika.lims.jsonapi_cache = window.bika.lims.jsonapi_cache || {};
            // if no page_size is specified, we need to explicitly add one here: 0=all.
            var page_size = request_data.page_size;
            if (page_size == undefined) {
                request_data.page_size = 0
            }
            var jsonapi_cacheKey = $.param(request_data);
            var jsonapi_read_handler = handler;
            if (window.bika.lims.jsonapi_cache[jsonapi_cacheKey] === undefined){
                $.ajax({
                    type: "POST",
                    dataType: "json",
                    url: window.portal_url + "/@@API/read",
                    data: request_data,
                    success: function(data) {
                        window.bika.lims.jsonapi_cache[jsonapi_cacheKey] = data;
                        jsonapi_read_handler(data);
                    }
                });
            } else {
                jsonapi_read_handler(window.bika.lims.jsonapi_cache[jsonapi_cacheKey]);
            }
        };
    }
}
