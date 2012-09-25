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
	$.each($('#partitions td.part_id'), function(i,v){
		partid = $($(v).children()[1]).text();
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

//////////////////////////////////////
function addPart(container,preservation){
	if(container == null || container == undefined){
		container = '';
	} else {
		container = container[0];
	}
	if(preservation == null || preservation == undefined){
		preservation = '';
	} else {
		preservation = preservation[0];
	}
	highest_part = '';
	from_tr = '';
	$.each($('#partitions td.part_id'), function(i,v){
		partid = $($(v).children()[1]).text();
		if (partid > highest_part){
			from_tr = $(v).parent();
			highest_part = partid;
		}
	});
	highest_part = highest_part.split("-")[1];
	next_part = parseInt(highest_part,10) + 1;

	// copy and re-format new partition table row
	uid	= $(from_tr).attr('uid');
	to_tr = $(from_tr).clone();
	$(to_tr).attr('id', 'folder-contents-item-part-'+next_part);
	$(to_tr).attr('uid', 'part-'+next_part);
	$(to_tr).find("#"+uid+"_row_data").attr('id', "part-"+next_part+"_row_data").attr('name', "row_data."+next_part+":records");
	$(to_tr).find("#"+uid).attr('id', 'part-'+next_part);
	$(to_tr).find("input[value='"+uid+"']").attr('value', 'part-'+next_part);
	$(to_tr).find("[uid='"+uid+"']").attr('uid', 'part-'+next_part);
	$(to_tr).find("span[uid='"+uid+"']").attr('uid', 'part-'+next_part);
	$(to_tr).find("input[name^='part_id']").attr('name', "part_id.part-"+next_part+":records").attr('value', 'part-'+next_part);
	$(to_tr).find("select[field='container_uid']").attr('name', "container_uid.part-"+next_part+":records");
	$(to_tr).find("select[field='preservation_uid']").attr('name', "preservation_uid.part-"+next_part+":records");
	$($($(to_tr).children('td')[0]).children()[1]).empty().append('part-'+next_part);

	// set part and container values
	$(to_tr).find("select[field='container_uid']").val(container);
	$(to_tr).find("select[field='preservation_uid']").val(preservation);
	$($("#partitions tbody")[0]).append($(to_tr));

	// add this part to Partition selectors in Analyses tab
	$.each($('select[name^="Partition\\."]'), function(i,v){
		$(v).append($("<option value='part-"+next_part+"'>part-"+next_part+"</option>"));
	});
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
	analysisprofiles = $.parseJSON($("#AnalysisProfiles").attr('value'));
	// clear existing selection
	$('input[id^=analyses_cb_]').filter(":checked").attr("checked", false);
	$.each($("select[name^=Partition]"), function(i,element){
		$(element).after(
			"<input type='hidden' name='"+$(element).attr('name')+"' value=''/>"
		);
		$(element).remove();
	});

	// select individual services
	profile_uid = $(this).val();
	service_uids = analysisprofiles[profile_uid];
	if (service_uids != undefined && service_uids != null) {
		$.each(service_uids, function(i,service_uid){
			check_service(service_uid);
			$('input[id^=analyses_cb_'+service_uid+']').attr("checked", true);
		});
	}
	// calculate automatic partitions
	parts = calculate_parts();
	// reset partition table
	$.each($('#partitions td.part_id'), function(i,v){
		partid = $($(v).children()[1]).text();
		if (partid != 'part-1'){
			// remove part TR from partition table
			$("tr[uid="+partid+"]").remove();
			// remove part from Partition selectors
			$.each($('select[name^="Partition\\."]'), function(i,v){
				$(v).find("option[value='"+partid+"']").remove();
			});
		}
	});

	// set container and preservation of first part
	if (parts.length > 0){
		first_tr = $($('#partitions td.part_id')[0]).parent();
		if(parts[0]['container'] != undefined
		   && parts[0]['container'] != null){
			container = parts[0]['container'][0];

			// if container is defined, but not in bika_utils.data, then it's
			// a container type.
			if (!(container in window.bika_utils.data['containers'])){
				for(c in window.bika_utils.data['containers']){
					c_obj = window.bika_utils.data['containers'][c];
					if(c_obj['containertype'] == container){
						container = c_obj['uid'];
						break
					}
				}
			}
			if (!(container in window.bika_utils.data['containers'])){
				// no match
				container = '';
			}
		} else {
			container = '';
		}
		$(first_tr).find("select[field='container_uid']").val(container);

		if(parts[0]['preservation'] != undefined
		    && parts[0]['preservation'] != null){
			preservation = parts[0]['preservation'][0];
		} else {
			preservation = '';
		}
		$(first_tr).find("select[field='preservation_uid']").val(preservation);
	}

	// set container and preservation of part-2 and up
	nr_parts = parts.length;
	for(i=1;i<parts.length;i++){
		part = parts[i];
		addPart(part['container'], part['preservation']);
	}
	// Set new part numbers
	$.each(parts, function(p,part){
		$.each(part['services'], function(s,service_uid){
			partnr = p+1;
			$("[name=Partition."+service_uid+":records]").val('part-'+partnr);
		});
	});
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
	$("#AnalysisProfile\\:list").val('');
}

$(document).ready(function(){
	_ = window.jsi18n_bika;
	PMF = window.jsi18n_plone;

	$("[name='uids:list']").live('click', click_uid_checkbox);

	$("#AnalysisProfile\\:list").change(setAnalysisProfile);

});
}(jQuery));
