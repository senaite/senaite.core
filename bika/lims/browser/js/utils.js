(function( $ ) {

jarn.i18n.loadCatalog('bika');
window.jsi18n_bika = jarn.i18n.MessageFactory('bika');
jarn.i18n.loadCatalog('plone');
window.jsi18n_plone = jarn.i18n.MessageFactory('plone');

function portalMessage(message) {
	str = "<dl class='portalMessage error'>"+
		"<dt>"+window.jsi18n_bika('Error')+"</dt>"+
		"<dd><ul>" + window.jsi18n_bika(message) +
		"</ul></dd></dl>";
	$('.portalMessage').remove();
	$(str).appendTo('#viewlet-above-content');
}

function log(e) {
	console.log(e.message);
	message = "Javascript: " + e.message + " url: " + window.location.url;
	$.ajax({
		type: 'POST',
		url: 'js_log',
		data: {'message':message,
				'_authenticator': $('input[name="_authenticator"]').val()}
	});
}

function calculate_partitions(service_uids, st_uid, st_minvol){
	parts = [];

	// loop through each selected service, assigning or creating
	// partitions as we go.
//	console.log(service_uids);
	for(si=0;si<service_uids.length;si++){
		service_uid = service_uids[si];
//		console.log("-----");
//		console.log("service_uid: "+ service_uid);

		service_data = window.bika_utils.data.services[service_uid];
		if (service_data == undefined || service_data == null){
			service_data = {'Separate':false,
			                'Container':[],
							'Preservation':[],
							'PartitionSetup':[],
							'backrefs':[],
							'deps':{}}
//			console.log("service_data undefined, create new: "+service_data.toSource());
		}

		// discover if a specific part_setup exists for this
		// sample_type and service_uid
		part_setup = '';
		$.each(service_data['PartitionSetup'],
			function(x, ps){
				if(ps['sampletype'] == st_uid){
					part_setup = ps;
					return false;
				}
			}
		);
		if (part_setup != '') {
//			console.log("part_setup found: "+part_setup.toSource());
			// if it does, we use it instead of defaults.
			separate = part_setup['separate'];
			container = part_setup['container'];
			preservation = part_setup['preservation'];
			minvol = parseFloat(part_setup['vol'].split(" ")[0]);
		} else {
//			console.log("part_setup not found, using service_data " + service_data.toSource());
			// Otherwise grab service/sampletype defaults
			separate = service_data['Separate'];
			container = service_data['Container'];
			preservation = service_data['Preservation'];
			minvol = st_minvol;
		}

		if (separate) {
			// create a separate partition for this analysis.
			// partition container and preservation remain plural.
			part = {'services': [service_uid],
					'separate': true,
					'container': container,
					'preservation': preservation,
					'volume': minvol
					};
//			console.log("partition must be separate.  created part: " + part.toSource())
			parts.push(part);

		} else {

			// So now we either need to find an existing partition
			// which permits us to add this analysis to it, or
			// create a new one.
//			console.log("searching for a partition")
			found_part = '';

			// convert container types to containers
			new_container = [];
			for(ci=0;ci<container.length;ci++){
				cc = window.bika_utils.data.containers[container[ci]];
				if(cc == undefined || cc == null){
					// cc is a container type.  add matching containers
					$.each(window.bika_utils.data.containers, function(ii,vv){
						if(container[ci] == vv['containertype']){
							new_container.push(vv['uid']);
						}
					});
				} else {
					new_container.push(cc['uid']);
				}
			}
			container = new_container;

			for(x=0; x<parts.length;x++){
				part = parts[x];

				// make sure this partition isn't flagged as separate
				if (part['separate']) {
					continue;
				}

				// if no container info is provided by either the
				// partition OR the service, this partition is available
				var c_intersection = [];
				if (part['container'].length > 0 || container.length > 0) {
					// check our containers against this partition's
					c_intersection = $.grep(container, function(c, y){
						return part['container'].indexOf(c) > -1;
					});
					if (c_intersection.length == 0){
//						console.log("No match intersecting containers " + container + " -AND- " + part['container']);
						// no match
						continue;
					}
				} else {
//				    console.log("Not intersecting containers");
				}

				// if no preservation info is provided by either the
				// partition OR the service, this partition is available
				var p_intersection = [];
				if (part['preservation'].length > 0 || preservation.length > 0) {
					// check our preservation against this partition's
					p_intersection = $.grep(preservation, function(p, y){
						return part['preservation'].indexOf(p) > -1;
					});
					if (p_intersection.length == 0){
//						console.log("No match intersecting preservations " + preservation + " -AND- " + part['preservation']);
						// no match
						continue;
					}
				} else {
//				    console.log("Not intersecting preservations");
				}

				// filter containers on capacity.
				if (part_setup != ''){
					newvol = parts[x]['volume'] + minvol;
					if (c_intersection.length > 0) {
						cc_intersection = $.grep(c_intersection, function(c, y){
							cc = window.bika_utils.data.containers[c];
							cc_cap = parseFloat(cc['capacity'].split(" ")[0]);
							return cc_cap > newvol;
						});
						if (cc_intersection.length == 0){
	//						console.log("No large enough container for " + newvol);
							// no match
							continue;
						}
						c_intersection = cc_intersection;
						parts[x]['volume'] = newvol;
					} else {
	//				    console.log("Not intersecting container volumes");
					}
				}

				// all the conditions passed:
				found_part = x;
//				console.log("Found a partition: " + x + ", " + parts[x].toSource());
				parts[x]['services'].push(service_uid);
				parts[x]['container'] = c_intersection;
				parts[x]['preservation'] = p_intersection;
//				console.log("Modified partition: " + x + ", " + parts[x].toSource());
				break;
			}

			if (found_part === ''){
				// No home found - make a new part for this analysis
				part = {'services': [service_uid],
						'separate': false,
						'container': container,
						'preservation': preservation,
						'volume': minvol
						};
//				console.log("No partition found, created new:" + part.toSource());
				parts.push(part);
			}
		}
	}
	return parts;
}

var bika_utils = bika_utils || {

	init: function () {
		if ('localStorage' in window && window.localStorage !== null) {
			bika_utils.storage = localStorage;
		} else {
			bika_utils.storage = {};
		}
		t = new Date().getTime();
		stored_counter = bika_utils.storage['bika_bsc_counter'];
		$.getJSON(portal_url+'/bika_bsc_counter?'+t, function(counter) {
			if (counter != stored_counter){
				$.getJSON(portal_url+'/bika_browserdata?'+t, function(data){
					bika_utils.storage['bika_bsc_counter'] = counter;
					bika_utils.storage['bika_browserdata'] = $.toJSON(data);
					bika_utils.data = data;
				});
			} else {
				data = $.parseJSON(bika_utils.storage['bika_browserdata']);
				bika_utils.data = data
			}
		});
	},

	portalMessage: portalMessage,

	calculate_partitions: calculate_partitions

}

bika_utils.init();
window.bika_utils = bika_utils;

function enableAddAttachment(this_field) {
	// XX move this to worksheet or AR or wherever it actually belongs
	attachfile = document.getElementById('AttachFile').value
	service = document.getElementById('Service').value
	analysis = document.getElementById('Analysis').value

	if (this_field == 'Analysis') {
		document.getElementById('Service').value = '';
	}
	if (this_field == 'Service') {
		document.getElementById('Analysis').value = '';
	}

	document.getElementById('addButton').disabled = false;
	if (attachfile == '') {
		document.getElementById('addButton').disabled = true
	} else {
		if ((service == '') && (analysis == '')) {
			document.getElementById('addButton').disabled = true
		}
	}

	return
}


$(document).ready(function(){

	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

	dateFormat = _("date_format_short_datepicker");

	$('input.datepicker').live('click', function() {
		$(this).datepicker({
			showOn:'focus',
			showAnim:'',
			changeMonth:true,
			changeYear:true,
			dateFormat:dateFormat
		})
		.click(function(){$(this).attr('value', '');})
		.focus();

	});

	$('input.datepicker_nofuture').live('click', function() {
		$(this).datepicker({
			showOn:'focus',
			showAnim:'',
			changeMonth:true,
			changeYear:true,
			maxDate: '+0d',
			dateFormat: dateFormat
		})
		.click(function(){$(this).attr('value', '');})
		.focus();
	});

	$('input.datepicker_2months').live('click', function() {
		$(this).datepicker({
			showOn:'focus',
			showAnim:'',
			changeMonth:true,
			changeYear:true,
			maxDate: '+0d',
			numberOfMonths: 2,
			dateFormat: dateFormat
		})
		.click(function(){$(this).attr('value', '');})
		.focus();
	});

	// Analysis Service popup trigger
	$(".service_title").live('click', function(){
		var dialog = $('<div></div>');
		dialog
			.load(window.portal_url + "/analysisservice_popup",
				{'service_title':$(this).text(),
				 '_authenticator': $('input[name="_authenticator"]').val()}
			)
			.dialog({
				width:450,
				height:450,
				closeText: _("Close"),
				resizable:true,
				title: "<img src='" + window.portal_url + "/++resource++bika.lims.images/analysisservice.png'/>&nbsp;" + $(this).text()
			});
	});

	$('#kss-spinner')
		.empty()
		.append('<img src="spinner.gif" alt="Loading"/>')
		.ajaxComplete(function() { $(this).toggle(false); });

	$(".numeric").live('keypress', function(event) {

		// Backspace, tab, enter, end, home, left, right, ., <, >, and -
		// We don't support the del key in Opera because del == . == 46.
		var allowedKeys = [8, 9, 13, 35, 36, 37, 39, 46, 60, 62, 45];
		// IE doesn't support indexOf
		var isAllowedKey = allowedKeys.join(",").match(new RegExp(event.which));
		// Some browsers just don't raise events for control keys. Easy.
		// e.g. Safari backspace.
		if (!event.which || // Control keys in most browsers. e.g. Firefox tab is 0
			(48 <= event.which && event.which <= 57) || // Always 0 through 9
			isAllowedKey) { // Opera assigns values for control keys.
			return;
		} else {
			event.preventDefault();
		}
	});

	// Archetypes :int inputs get numeric class
	$("input[name*='\\:int']").addClass('numeric');

});
}(jQuery));

