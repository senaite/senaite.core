// ar.js and sample.js are nearly identical
// they are both loaded in AR and sample views, so they must be careful
// not to overlap.  The functions that are common go in sample.js
(function( $ ) {
"use strict";

function workflow_transition_publish(event){
    event.preventDefault();
    var requestdata = {};
    var spec_uid = $("#PublicationSpecification_uid").val();
    requestdata.PublicationSpecification = spec_uid;
    requestdata.workflow_action = "publish";
    var requeststring = $.param(requestdata);
    var href = window.location.href.split("?")[0]
        .replace("/base_view", "")
        .replace("/view", "") + "/workflow_action?" + requeststring;
    window.location.href = href;
}

function workflow_transition_republish(event){
    event.preventDefault();
    var requestdata = {};
    var spec_uid = $("#PublicationSpecification_uid").val();
    requestdata.PublicationSpecification = spec_uid;
    requestdata.workflow_action = "republish";
    var requeststring = $.param(requestdata);
    var href = window.location.href.split("?")[0]
        .replace("/base_view", "")
        .replace("/view", "") + "/workflow_action?" + requeststring;
    window.location.href = href;
}

function addParam(address, param, val){
    var argparts;
    var parts = address.split("?");
    var url = parts[0];
    var args = [];
    if (parts.length > 1) {
        var found = false;
        args = parts[1].split("&");
        for (var arg=0; arg<args.length; arg++) {
            argparts = args[arg].split('=');
            if (argparts[0] == param) {
                args[arg] = param + '=' + val;
                found = true;
            }
        };
        if (found == false) {
            args.push(param + '=' + val);
        };
    } else {
        args.push(param + '=' + val);
    };
    return url + "?" + args.join('&');
};

$(document).ready(function(){

    $('#layout').change(function(){
        var address = $(".context_action_link").attr('href');
        var href = addParam(address, 'layout', $(this).val())
        $(".context_action_link").attr('href', href);
    });
    $('#ar_count').each(function() {
        var elem = $(this);

        // Save current value of element
        elem.data('oldVal', elem.val());

        // Look for changes in the value
        elem.bind("propertychange keyup input paste", function(event){
            var new_val = elem.val();
            // If value has changed...
            if (new_val != '' && elem.data('oldVal') != new_val) {
                // Updated stored value
                elem.data('oldVal', new_val);
                var address = $(".context_action_link").attr('href');
                var href = addParam(address, 'ar_count', $(this).val())
                $(".context_action_link").attr('href', href);
            }
        });
    });

	$("#workflow-transition-publish").click(workflow_transition_publish);
	$("#workflow-transition-republish").click(workflow_transition_publish);

    // Set the analyst automatically when selected in the picklist
    $('.portaltype-analysisrequest .bika-listing-table td.Analyst select').change(function() {
        var analyst = $(this).val();
        var key = $(this).closest('tr').attr('keyword');
        var obj_path = window.location.href.replace(window.portal_url, '');
        var obj_path_split = obj_path.split('/');
        if (obj_path_split.length > 4) {
            obj_path_split[obj_path_split.length-1] = key;
        } else {
            obj_path_split.push(key);
        }
        obj_path = obj_path_split.join('/');
        $.ajax({
            type: "POST",
            url: window.portal_url+"/@@API/update",
            data: {"obj_path": obj_path,
                   "Analyst":  analyst}
        });
    });

    if (document.location.href.search('/clients/') >= 0
        && $(".template-base_view.portaltype-analysisrequest").length > 0
        && $("#archetypes-fieldname-SamplePoint #SamplePoint").length > 0
        && $(".template-ar_add").length < 1) {

        var cid = document.location.href.split("clients")[1].split("/")[1];
        $.ajax({
            url: window.portal_url + "/clients/" + cid + "/getClientInfo",
            type: 'POST',
            data: {'_authenticator': $('input[name="_authenticator"]').val()},
            dataType: "json",
            success: function(data, textStatus, $XHR){
                if (data['ClientUID'] != '') {
                    var spelement = $("#archetypes-fieldname-SamplePoint #SamplePoint");
		    var base_query=$.parseJSON($(spelement).attr("base_query"));
                    base_query["getClientUID"] = data['ClientUID'];
                    $(spelement).attr("base_query", $.toJSON(base_query));
		    var options = $.parseJSON($(spelement).attr("combogrid_options"));
		    options.url = window.location.href.split("/ar")[0] + "/" + options.url;
		    options.url = options.url + "?_authenticator=" + $("input[name='_authenticator']").val();
		    options.url = options.url + "&catalog_name=" + $(spelement).attr("catalog_name");
		    options.url = options.url + "&base_query=" + $.toJSON(base_query);
		    options.url = options.url + "&search_query=" + $(spelement).attr("search_query");
		    options.url = options.url + "&colModel=" + $.toJSON( $.parseJSON($(spelement).attr("combogrid_options")).colModel);
		    options.url = options.url + "&search_fields=" + $.toJSON($.parseJSON($(spelement).attr("combogrid_options")).search_fields);
		    options.url = options.url + "&discard_empty=" + $.toJSON($.parseJSON($(spelement).attr("combogrid_options")).discard_empty);
		    options.force_all="false";
		    $(spelement).combogrid(options);
		    $(spelement).addClass("has_combogrid_widget");
		    $(spelement).attr("search_query", "{}");
                }
            }
        });
    }
});
}(jQuery));
