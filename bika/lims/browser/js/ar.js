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

});
}(jQuery));
