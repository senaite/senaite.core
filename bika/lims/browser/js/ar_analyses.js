(function( $ ) {
////////////////////////////////////////
function check_service(service_uid){
	// Add partition dropdown
	element = $("[name=Partition."+service_uid+":records]");
	select = '<select class="listing_select_entry" '+
		'name="Partition.'+service_uid+':records" '+
		'field="Partition" uid="'+service_uid+'" '+
		'style="font-size: 100%">';
	$.each($('#partitions td.PartTitle'), function(i,v){
		partid = $($(v).children()[1]).text();
		select = select + '<option value="'+partid+'">'+partid+
			'</option>';
	});
	select = select + "</select>";
	$(element).after(select);

	// remove hidden field
	$(element).remove();

	// Add price field
	element = $("[name=Price."+service_uid+":records]");
	price = '<input class="listing_string_entry numeric" '+
		'name="Price.'+service_uid+':records" '+
		'field="Price" type="text" uid="'+service_uid+'" '+
		'autocomplete="off" style="font-size: 100%" size="5" '+
		'value="'+$(element).val()+'">';
	$(element).after(price);
	// remove hidden field and price label
	$($(element).siblings()[1]).remove();
	$(element).remove();
}

////////////////////////////////////////
function uncheck_service(service_uid){
	element = $("[name=Partition."+service_uid+":records]");
	$(element).after(
		"<input type='hidden' name='Partition."+service_uid+":records'"+
		"value=''/>"
	);
	$(element).remove();

	element = $("[name=Price."+service_uid+":records]");
	$($(element).siblings()[0]).after(' <span class="state-active state-active ">'+$(element).val()+'</span>')
	$(element).after(
		"<input type='hidden' name='Price."+service_uid+":records'"+
		"value='"+$(element).val()+"'/>"
	);
	$(element).remove();
}

////////////////////////////////////////
function calcdependencies(elements, auto_yes) {
	// elements is a list of jquery checkbox objects
	var element = elements.shift();
	if(auto_yes == undefined){ auto_yes = false ; }

	service_uid = $(element).attr('id').split("_cb_")[1];
	service_data = window.bsc.data.services[service_uid];

	if (service_data == undefined || service_data == null){
		// if service_uid is not in bsc.services, there are no deps.
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
					if (! $('#list_cb_'+service[0]).attr("checked") ){
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
							if(! $('#list_cb_'+serviceUID).attr("checked") ){
								check_service(serviceUID);
								$('#list_cb_'+serviceUID).attr("checked", true);
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
				cb = $('#list_cb_' + serviceUID);
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
							se = $('#list_cb_'+serviceUID);
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

function portalMessage(message){
	str = "<dl class='portalMessage error'>"+
		"<dt>Error</dt>"+
		"<dd><ul>" + message +
		"</ul></dd></dl>";
	$('.portalMessage').remove();
	$(str).appendTo('#viewlet-above-content');
}

$(document).ready(function(){
	_ = window.jsi18n;

	////////////////////////////////////////
	// disable checkboxes for eg verified analyses.
	$.each($("[name='uids:list']"), function(i,cb){
		uid = $(cb).val();
		row_data = $.parseJSON($('#'+uid+'_row_data').val());
		if (row_data['disabled'] == true){
			$(cb).attr('disabled', true);
			// disabled checkboxes must be shadowed by hidden fields,
			// or they don't appear in the submitted form.
			cbname = $(cb).attr('name');
			cbid = $(cb).attr('id');
			$(cb).removeAttr('name').removeAttr('id');
			$(cb).after("<input type='hidden' name='"+cbname+"' "+
			            "value='"+uid+"' id='"+cbid+"'/>");
		}
	})

	////////////////////////////////////////
	$(".ar_analyses_add_part").click(function(event){
		event.preventDefault();

		highest_part = '';
		from_tr = '';
		$.each($('#partitions td.PartTitle'), function(i,v){
			partid = $($(v).children()[1]).text();
			if (partid > highest_part){
				from_tr = $(v).parent();
				highest_part = partid;
			}
		});
		highest_part = highest_part.split("-")[1];
		next_part = parseInt(highest_part,10) + 1;

		// copy and re-format new partition table row
		part_trs = $("#partitions tbody tr")[0];
		uid	= $(from_tr).attr('uid');
		to_tr = $(from_tr).clone();
		$(to_tr).attr('id', 'folder-contents-item-part-'+next_part);
		$(to_tr).attr('uid', 'part-'+next_part);
		$(to_tr).find("#"+uid+"_row_data").attr('id', "part-"+next_part+"_row_data").attr('name', "row_data."+next_part+":records");
		$(to_tr).find("#"+uid).attr('id', 'part-'+next_part);
		$(to_tr).find("input[value='"+uid+"']").attr('value', 'part-'+next_part);
		$(to_tr).find("[uid='"+uid+"']").attr('uid', 'part-'+next_part);
		$(to_tr).find("span[uid='"+uid+"']").attr('uid', 'part-'+next_part);
		$(to_tr).find("input[name^='PartTitle']").attr('name', "PartTitle.part-"+next_part+":records").attr('value', 'part-'+next_part);
		$(to_tr).find("select[field='getContainer']").attr('name', "getContainer.part-"+next_part+":records");
		$(to_tr).find("select[field='getPreservation']").attr('name', "getPreservation.part-"+next_part+":records");
		$($($(to_tr).children('td')[0]).children()[1]).empty().append('part-'+next_part);
		$($("#partitions tbody")[0]).append($(to_tr));

		// add this part to Partition selectors
		$.each($('select[name^="Partition\\."]'), function(i,v){
			$(v).append($("<option value='part-"+next_part+"'>part-"+next_part+"</option>"));
		});
	});

	////////////////////////////////////////
	$(".ar_analyses_delete_part").click(function(event){
		event.preventDefault();

		//find and remove highest numbered part
		hp = '';
		tr = '';
		$.each($('#partitions td.PartTitle'), function(i,v){
			partid = $($(v).children()[1]).text();
			if (partid > hp){
				tr = $(v).parent();
				hp = partid;
			}
		});
		if (hp == 'part-1'){
			return;
		}
		$(tr).remove();

		// remove this part from Partition selectors
		$.each($('select[name^="Partition\\."]'), function(i,v){
			$(v).find("option[value='"+hp+"']").remove();
		});
	});

	////////////////////////////////////////
	// checkboxes in services list
	$("[name='uids:list']").live('click', function(){
		calcdependencies([this]);

		service_uid = $(this).val();
		if ($(this).attr("checked")){
			check_service(service_uid);
		}
		else {
			uncheck_service(service_uid);
		}
	});

});
}(jQuery));
