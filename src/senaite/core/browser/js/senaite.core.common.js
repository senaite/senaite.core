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
                    UID: service_uid,
                    include_methods: 'getServiceDependantsUIDs',
                };
                var deps = {};
                $.ajaxSetup({async:false});
                window.bika.lims.jsonapi_read(request_data, function(data){
                    if (data.objects != null && data.objects.length > 0) {
                        deps = data.objects[0].getServiceDependantsUIDs;
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
                    UID: service_uid,
                    include_methods: 'getServiceDependenciesUIDs',
                };
                var deps = {};
                $.ajaxSetup({async:false});
                window.bika.lims.jsonapi_read(request_data, function(data){
                    if (data.objects != null && data.objects.length > 0) {
                        deps = data.objects[0].getServiceDependenciesUIDs;
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
        window.bika.lims.warning = function(e) {
            var message = "(" + window.location.href + "): " + e;
            $.ajax({
                type: "POST",
                url: "js_warn",
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

        /**
         * Update or modify a query filter for a reference widget.
         * This will set the options, then re-create the combogrid widget
         * with the new filter key/value.
         * If filtervalue is empty, the function will delete the query element.
         *
         * @param {object} element - the input element as combogrid.
         * @param {string} filterkey - the new filter key to filter by.
         * @param {string} filtervalue - the value of the new filter.
         * @param {string} querytype - it can be 'base_query' or 'search_query'
         */
        window.bika.lims.update_combogrid_query = function(
                element, filterkey, filtervalue, querytype) {

            if (!$(element).is(':visible')) {
                return;
            };
            if (!querytype) {
                querytype = 'base_query';
            };
            var query =  jQuery.parseJSON($(element).attr(querytype));
            // Adding the new query filter
            if (filtervalue) {
                query[filterkey] = filtervalue;
                };
            // Deleting the query filter
            if (filtervalue === '' && query[filterkey]){
                delete query[filterkey];
            };
            $(element).attr(querytype, JSON.stringify(query));

            var options = jQuery.parseJSON(
                $(element).attr("combogrid_options"));

            // Building new ajax request
            options.url = window.portal_url + "/" + options.url;
            options.url = options.url + "?_authenticator=" +
                $("input[name='_authenticator']").val();
            options.url = options.url + "&catalog_name=" +
                $(element).attr("catalog_name");

            options.url = options.url + "&base_query=" +
                encodeURIComponent($(element).attr("base_query"));
            options.url = options.url + "&search_query=" +
                encodeURIComponent($.toJSON(query));

            var col_model = options.colModel;
            var search_fields = options.search_fields;
            var discard_empty = options.discard_empty;
            var min_length = options.minLength;

            options.url = options.url + "&colModel=" +
                $.toJSON(col_model);

            options.url = options.url + "&search_fields=" +
                $.toJSON(search_fields)

            options.url = options.url + "&discard_empty=" +
                $.toJSON(discard_empty);

            options.url = options.url + "&minLength=" +
                $.toJSON(min_length);

            options.force_all = "false";

            // Apply changes
            $(element).combogrid(options);
        };

        // Priority Selection Widget
        $('.ArchetypesPrioritySelectionWidget select').change(function(e){
            var val = $(this).find('option:selected').val();
            $(this).attr('value', val);
        });
        $('.ArchetypesPrioritySelectionWidget select').change();

    }
    that.svgToImage = function(svg) {
        var url = 'data:image/svg+xml;base64,' + btoa(svg);
        return '<img src="'+url+'"/>';
    };
}
