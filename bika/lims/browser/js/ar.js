// ar.js and sample.js are nearly identical
(function( $ ) {
"use strict";

function workflow_transition_sample(event){
    jarn.i18n.loadCatalog('plone');
	var PMF = window.jarn.i18n.MessageFactory("plone");
	event.preventDefault();
	if ($("#DateSampled").val() !== "" && $("#Sampler").val() !== "") {
		var requestdata = {};
		requestdata.workflow_action = "sample";
		$.each($("form[name='header_form']").find("input,select"), function(i,v){
			var name = $(v).attr("name");
			var value =  $(v).attr("type") == "checkbox" ? $(v).prop("checked") : $(v).val();
			requestdata[name] = value;
		});
		var requeststring = $.param(requestdata);
		// sending only the username, because it's all we have access to.
		var href = window.location.href.split("?")[0] + "?" + requeststring;
		window.location.href = href;
	} else {
		var message = "";
		if ($("#DateSampled").val() === ""){
			message = message + PMF("${name} is required, please correct.", {"name":"Date Sampled"});
		}
		if ($("#Sampler").val() === ""){
			if(message !== "") { message = message + "<br/>"; }
			message = message + PMF("${name} is required, please correct.", {"name":"Sampler"});
		}
		window.bika.lims.portalMessage(message);
	}
}

function workflow_transition_preserve(event){
	event.preventDefault();
    jarn.i18n.loadCatalog('bika');
	var _ = window.jarn.i18n.MessageFactory("bika");
	var message = _("You must preserve individual Sample Partitions");
	window.bika.lims.portalMessage(message);
}

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

    // jarn.i18n.loadCatalog('bika');
	// var _ = window.jarn.i18n.MessageFactory("bika");
    // jarn.i18n.loadCatalog('plone');
	// var PMF = window.jarn.i18n.MessageFactory("plone");

	// Plone "Sample" transition is only available when Sampler and DateSampled
	// are completed
	$("#workflow-transition-sample").click(workflow_transition_sample);

	$("#workflow-transition-publish").click(workflow_transition_publish);
	$("#workflow-transition-republish").click(workflow_transition_publish);

	// Disable Plone UI for preserve transition
	$("#workflow-transition-preserve").click(workflow_transition_preserve);

	function autocomplete_sampletype(request,callback){
		$.getJSON("ajax_sampletypes",
			{
				"term":request.term,
				"_authenticator": $("input[name='_authenticator']").val()
			},
			function(data){
				callback(data);
			}
		);
	}
	function autocomplete_samplepoint(request,callback){
		$.getJSON("ajax_samplepoints",
			{
				"term":request.term,
				"_authenticator": $("input[name='_authenticator']").val()
			},
			function(data){
				callback(data);
			}
		);
	}
	$("#SampleType").autocomplete({ minLength: 0, source: autocomplete_sampletype});
	$("#SamplePoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});

});
}(jQuery));
