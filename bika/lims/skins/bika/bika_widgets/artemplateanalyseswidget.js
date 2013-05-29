// ./artemplateanalyseswidget.pt
// ../../../browser/widgets/artemplateanalyseswidget.py

// Most of this code is shared in ../../../browser/js/ar_analyses.pt
// There are a few differences, because this widget holds a dictionary,
// where the AR form reads and writes ARAnalysesField.
// Also note, the form_id is different, so checkboxes are called
// analyses_cb_* here, an list_cb_* there, ar_x_Analyses there, uids:list here.

(function( $ ) {

////////////////////////////////////////
function expand_cat(service_uid){
	cat = $("[name=Partition."+service_uid+":records]").parents('tr').attr('cat');
	th = $('th[cat='+cat+']');
	if ($(th).hasClass('collapsed')){
		table = $(th).parents('.bika-listing-table');
		// show sub TR rows
		$(table)
			.children('tbody')
			.children('tr[cat='+cat+']')
			.toggle(true);
		$(th).removeClass('collapsed').addClass('expanded');
	}
}

////////////////////////////////////////
function check_service(service_uid){
	// Add partition dropdown
	element = $("[name=Partition."+service_uid+":records]");
	select = '<select class="listing_select_entry" '+
		'name="Partition.'+service_uid+':records" '+
		'field="Partition" uid="'+service_uid+'" '+
		'style="font-size: 100%">';
	$.each(($('#Partitions_table td input').filter("[id^='Partitions-part_id']")), function(i,v) {
		partid = $($(v)).val();
		select = select + '<option value="'+partid+'">'+partid+
			'</option>';
	});
	select = select + "</select>";
	$(element).after(select);
	// remove hidden field
	$(element).remove();
	expand_cat(service_uid);
}

////////////////////////////////////////
function uncheck_service(service_uid){
	element = $("[name=Partition."+service_uid+":records]");
	$(element).after(
		"<input type='hidden' name='Partition."+service_uid+":records'"+
		"value=''/>"
	);
	$(element).remove();
}

////////////////////////////////////////
function calcdependencies(elements, auto_yes) {
	// elements is a list of jquery checkbox objects
	var element = elements.shift();
	if(auto_yes == undefined){ auto_yes = false ; }

	service_uid = $(element).attr('id').split("_cb_")[1];
	service_data = window.bika_utils.data.services[service_uid];

	if (service_data == undefined || service_data == null){
		// if service_uid is not in bika_utils.data.services, there are no deps.
		return;
	}
	var deps = service_data['deps'];
	var backrefs = service_data['backrefs'];

	if ($(element).attr("checked") == true){
		// selecting a service; discover services it depends on.
		var affected_services = [];
		var affected_titles = [];
		// actions are discovered and stored in dep_args, until confirmation dialog->Yes.
		var dep_args = [];

		if (deps == undefined || deps == null) {
			pocdata = [];
		} else {
			pocdata = deps;
		}
		$.each(pocdata, function(pocid_poctitle, catdata){
			var poc = pocid_poctitle.split("_");
			$.each(catdata, function(catid_cattitle, servicedata){
				var cat = catid_cattitle.split("_");
				var services = [];
				$.each(servicedata, function(i, serviceuid_servicetitle){
					service = serviceuid_servicetitle.split("_");
					// if the service is already checked, skip it.
					if (! $('#analyses_cb_'+service[0]).attr("checked") ){
						// this one is for the current category
						services.push(service[0]);
						// and this one decides if the confirmation box gets shown at all.
						affected_services.push(service[0]);
						// this one is for the pretty message box.
						affected_titles.push(service[1] + " ("+cat[1]+")");
					}
				});
				// we want to confirm, then process these all at once
				if(services.length > 0){
					dep_args.push([poc[0], cat[0], services]);
				}
			});
		});

		if (affected_services.length > 0) {
			$("body").append(
				"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
				_("<p>${service} requires the following services to be selected:</p><br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
					{service:$(element).attr('item_title'),
					 deps: affected_titles.join("<br/>")})+"</div>");
				function add_Yes(){
					$.each(dep_args, function(i,args){
						$.each(args[2], function(x,serviceUID){
							if(! $('#analyses_cb_'+serviceUID).attr("checked") ){
								check_service(serviceUID);
								$('#analyses_cb_'+serviceUID).attr("checked", true);
								expand_cat(serviceUID);
							}
						});
					});
					$(this).dialog("close");
					$('#messagebox').remove();
				}
				function add_No(){
					if($(element).attr("checked") ){
						uncheck_service($(element).attr('value'));
						$(element).attr("checked", false);
					}
					$(this).dialog("close");
					$('#messagebox').remove();
			}
			if (auto_yes) {
				$('#messagebox').remove();
				add_Yes();
			} else {
				yes = _("Yes");
				no = _("No");
				$("#messagebox").dialog({width:450,
				                         modal: true,
										 resizable: false,
										 closeOnEscape: false,
										 buttons:{yes: add_Yes,
										          no: add_No}
										});
			}
		}
	}
	else {
		// unselecting a service; discover back dependencies
		var affected_titles = [];
		var affected_services = [];
		s_uids = backrefs;
		if (s_uids == undefined || s_uids == null) {
			s_uids = [];
		}
		if (s_uids.length > 0){
			$.each(s_uids, function(i, serviceUID){
				cb = $('#analyses_cb_' + serviceUID);
				if (cb.attr("checked")){
					affected_services.push(serviceUID);
					affected_titles.push(cb.attr('item_title'));
				}
			});
			$("body").append(
				"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
				_("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
					{service:$(element).attr('item_title'),
					 deps: affected_titles.join("<br/>")})+"</div>");
			yes = _("Yes");
			no = _("No");
			if (affected_services.length > 0) {
				$("#messagebox").dialog({width:450,
				                         modal: true,
				                         resizable:false,
										 closeOnEscape: false,
										 buttons:{
					yes: function(){
						$.each(affected_services, function(i,serviceUID){
							se = $('#analyses_cb_'+serviceUID);
							uncheck_service(serviceUID);
							$(se).attr('checked', false);
						});
						$(this).dialog("close");
						$('#messagebox').remove();
					},
					no:function(){
						service_uid = $(element).attr('value');
						check_service(service_uid);
						$(element).attr('checked', true);
						$(this).dialog("close");
						$('#messagebox').remove();
					}
				}});
			} else {
				$('#messagebox').remove();
			}
		}
	}
}

////////////////////////////////////////
function calculate_parts(){

	// get SampleType
	st_title = $("#SampleType").val();
	st_uid = window.bika_utils.data.st_uids[st_title];
	if (st_uid != undefined && st_uid != null){
		st_minvol = sampletype['minvol'].split(" ")[0];
		if(st_minvol.length == 0){
			st_minvol = 0;
		} else {
			st_minvol = parseFloat(st_minvol, 10);
		}
	} else {
		st_uid = '';
		st_minvol = 0;
	}

	// get selected services
	selected = $('[name$="uids\\:list"]').filter(':checked');
	service_uids = []
	for(i=0;i<selected.length;i++){
		service_uids.push($(selected[i]).attr('value'));
	}

	parts = window.bika_utils.calculate_partitions(service_uids, st_uid, st_minvol);

	return parts;
}

////////////////////////////////////////
function setAnalysisProfile(){
	// get profile services list
	var analysisprofiles = $.parseJSON($("#AnalysisProfiles").attr('value'));
	// clear existing selection
	$('input[id^=analyses_cb_]').filter(":checked").attr("checked", false);
	$.each($("select[name^=Partition]"), function(i,element){
		$(element).after(
			"<input type='hidden' name='"+$(element).attr('name')+"' value=''/>"
		);
		$(element).remove();
	});

	// select individual services
	var profile_uid = $(this).attr('uid');
	var service_uids = analysisprofiles[profile_uid];
	if (service_uids != undefined && service_uids != null) {
		$.each(service_uids, function(i,service_uid){
			check_service(service_uid);
			$('input[id^=analyses_cb_'+service_uid+']').attr("checked", true);
		});
	}
	// calculate automatic partitions
	var parts = calculate_parts();

	// reset partition table
	for (var i = $(".records_row_Partitions").length - 1; i >= 1; i--) {
		e = $(".records_row_Partitions")[i];
		// remove part from Partition selector dropdowns
		part = $($(e).find("input[id*='Partitions-part_id']")[0]).val();
		$('select[name^="Partition\\."]').find("option[value='"+part+"']").remove();
		// remove row from partition list
		$(e).remove();
	};

	function setPartitionFields(part_nr, part_data) {
		var first_part_row = $(".records_row_Partitions")[part_nr];
		var container = '';
		var container_title = '';
		if(part_data['container'] != undefined && part_data['container'] != null){
			container = part_data['container'][0];
			// if container is not in bika_utils.data, it's a container type.
			// resolve to a container.
			if (!(container in window.bika_utils.data['containers'])){
				for(c in window.bika_utils.data['containers']){
					c_obj = window.bika_utils.data['containers'][c];
					if(c_obj['containertype'] == container){
						container = c_obj.uid;
						break
					}
				}
			}
			if(container != ''){
				container_title = window.bika_utils.data['containers'][container].title;
			}
		}
		$(first_part_row).find("input[id*='Partitions-Container']").val(container_title);

        var preservation = '';
        var preservation_title = '';
		if(part_data['preservation'] != undefined && part_data['preservation'] != null){
			preservation = part_data['preservation'][0];
			preservation_title = window.bika_utils.data['preservations'][preservation].title;
		}
		$(first_part_row).find("input[id*='Partitions-Preservation']").val(preservation_title);
	}

    // Edit existing first row
	if (parts.length > 0){
		setPartitionFields(0, parts[0])
	}

	// Add rows and set container and preservation of part-2 and up
	nr_parts = parts.length;
	for(i=1;i<parts.length;i++){
		$("#Partitions_more").click();
		setPartitionFields(i, parts[i]);
	}
}

////////////////////////////////////////
function click_uid_checkbox(){
	calcdependencies([this]);
	service_uid = $(this).val();
	if ($(this).attr("checked")){
		check_service(service_uid);
	} else {
		uncheck_service(service_uid);
	}
	$("#AnalysisProfile").val('');
}

$(document).ready(function(){

	_ = jarn.i18n.MessageFactory('bika');
	PMF = jarn.i18n.MessageFactory('plone');

	$("[name='uids:list']").live('click', click_uid_checkbox);

	$("#AnalysisProfile").bind('selected', setAnalysisProfile);

});
}(jQuery));
