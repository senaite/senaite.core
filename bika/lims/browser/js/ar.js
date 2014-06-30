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

$(document).ready(function(){

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
});
}(jQuery));
