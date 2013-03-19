(function( $ ) {

// Configure the widgets that archetypes built:
// set id and name to ar-col-fieldName fornats
// un-set the readonly attribute on the fields (so that we can search).
function ar_rename_elements(){
	elements = $('td[ar_add_column_widget]').find('input[type!=hidden]').not('[disabled]');
	for (var i = elements.length - 1; i >= 0; i--) {
		e = elements[i];
		column = $($(e).parents('td')).attr('column');
		// not :ignore_empty, widgets each get submitted to their own form handlers
		$(e).attr('name', 'ar.'+column+'.'+$(e).attr('name')+":record");
		e.id = 'ar_'+column+'_'+e.id;
		$(e).removeAttr('required');
	};
	elements = $('td[ar_add_column_widget]').find('input[type=hidden]');
	for (var i = elements.length - 1; i >= 0; i--) {
		e = elements[i];
		column = $($(e).parents('td')).attr('column');
		e.id = 'ar_'+column+'_'+e.id;
		// not :ignore_empty, widgets each get submitted to their own form handlers
		$(e).attr('name', 'ar.'+column+'.'+$(e).attr('name')+":record");
	};
}

// we do the referencewidget_lookups differently to the widget default.
// We also include a bunch of ar_add specific on-change stuff, since the
// popup widget takes over the .change event completely.
function ar_referencewidget_lookups(elements){
	_ = jarn.i18n.MessageFactory('bika');
	PMF = jarn.i18n.MessageFactory('plone');
    if(elements == undefined){
        var inputs = $("input.referencewidget").not('.has_combogrid_widget');
    } else {
        var inputs = elements;
    }
    for (var i = inputs.length - 1; i >= 0; i--) {
        var element = inputs[i];
        var options = $.parseJSON($(element).attr('combogrid_options'));
        if(options == '' || options == undefined || options == null){
            continue;
        }
        options.select = function(event, ui){
            event.preventDefault();

            // Set form valuesvalue in activated element (must exist in colModel!)
			var column = this.id.split("_")[1]; //"ar.0.fieldName"
            var fieldName = $(this).attr('name').split(".")[2];
            $(this).val(ui.item[$(this).attr('ui_item')]);
            $(this).attr('uid', ui.item['UID']);

            // split out the :ignore_empty:etc
            var bits = fieldName.split(':');
            $('input[name*=ar\\.'+column+'\\.'+bits[0]+'_uid]').val(ui.item['UID']);

			// samplepoint <> sampletype relations
			if(this.id.split('_')[2] == 'SampleType'){
				element = $('#ar_'+column+'_SamplePoint');
				element
					.removeClass( "cg-autocomplete-input" )
					.removeAttr( "autocomplete" )
					.removeAttr( "role" )
					.removeAttr( "aria-autocomplete" )
					.removeAttr( "aria-haspopup" );
				new_element = $(element[0]).clone();
				parent = $(element).parent();
				$(element).remove();
				$(parent).append(new_element);
				element = $('#ar_'+column+'_SamplePoint');
		        // cut kwargs into the base_query
		        base_query = $(element).attr('base_query');
		    	base_query = $.parseJSON(base_query);
		    	base_query = $.toJSON(base_query);
			    search_query = {'getSampleTypeTitle': ui.item[$(this).attr('ui_item')]};
		    	search_query = $.toJSON(search_query);
		    	element.attr('search_query', search_query);
				ar_referencewidget_lookups(element);
			}
			if(this.id.split('_')[2] == 'SamplePoint'){
				element = $('#ar_'+column+'_SampleType');
				element
					.removeClass( "cg-autocomplete-input" )
					.removeAttr( "autocomplete" )
					.removeAttr( "role" )
					.removeAttr( "aria-autocomplete" )
					.removeAttr( "aria-haspopup" );
				new_element = $(element[0]).clone();
				parent = $(element).parent();
				$(element).remove();
				$(parent).append(new_element);
				element = $('#ar_'+column+'_SampleType');
		        // cut kwargs into the base_query
		        base_query = $(element).attr('base_query');
		    	base_query = $.parseJSON(base_query);
		    	base_query = $.toJSON(base_query);
			    search_query = {'getSamplePointTitle': ui.item[$(this).attr('ui_item')]};
		    	search_query = $.toJSON(search_query);
		    	element.attr('search_query', search_query);
				ar_referencewidget_lookups(element);
			}

			// Selected a Profile
		    if(this.id.split('_')[2] == 'Profile'){
				unsetTemplate(column);
				setAnalysisProfile(column, $(this).val());
				calculate_parts(column);
			}

			// Selected a Template
		    if(this.id.split('_')[2] == 'Template'){
		    	setTemplate(column, $(this).val());
		    }

			// $("input[id*=_Template]").change(setTemplate);
			// 	var curDate = new Date();
			// 	var y = curDate.getFullYear();
			// 	var limitString = '1900:' + y;
			// 	var dateFormat = _("date_format_short_datepicker");
			// 	column = $(this).attr('column');
			// 	$("#ar_"+column+"_SampleID_button").val($("#ar_"+column+"_SampleID_default").val());
			// 	$("#ar_"+column+"_SampleID").val('');
			// 	$("#ar_"+column+"_ClientReference").val('').removeAttr("readonly");
			// 	$("#ar_"+column+"_SamplingDate")
			// 		.datepicker({
			// 			showOn:'focus',
			// 			showAnim:'',
			// 			changeMonth:true,
			// 			changeYear:true,
			// 			dateFormat: dateFormat,
			// 			yearRange: limitString
			// 		})
			// 		.click(function(){$(this).attr('value', '');})
			// 		.attr('value', '');
			// 	$("#ar_"+column+"_ClientSampleID").val('').removeAttr("readonly");
			// 	$("#ar_"+column+"_SamplePoint").val('').removeAttr("readonly");
			// 	$("#ar_"+column+"_SampleType").val('').removeAttr("readonly");
			// 	$("#ar_"+column+"_SamplingDeviation").val('').removeAttr("disabled");
			// 	$("#ar_"+column+"_Composite").attr('checked', false).removeAttr("disabled");
			// 	$("#ar_"+column+"_AdHoc").attr('checked', false).removeAttr("disabled");
			// 	$("#ar_"+column+"_DefaultContainerType").removeAttr("disabled");
			// 	$("#deleteSampleButton_" + column).toggle(false);
			// 	// uncheck and enable all visible service checkboxes
			// 	$("input[id*='_"+column+"_']").filter(".cb").removeAttr('disabled').attr('checked', false);
			// 	uncheck_partnrs(column);
			// 	recalc_prices();

			// Selected a SampleType
		    if(this.id.split('_')[2] == 'SampleType'){
				unsetTemplate(column);
				unsetAnalysisProfile(column, $(this).val());
				calculate_parts(column);
		    }


        }
        if(window.location.href.search("ar_add") > -1){
            options.url = window.location.href.split("/ar_add")[0] + "/" + options.url;
        }
        options.url = options.url + '?_authenticator=' + $('input[name="_authenticator"]').val();
        options.url = options.url + '&catalog_name=' + $(element).attr('catalog_name');
        options.url = options.url + '&base_query=' + $(element).attr('base_query');
        options.url = options.url + '&search_query=' + $(element).attr('search_query');
        $(element).combogrid(options);
        $(element).addClass("has_combogrid_widget");
        $(element).attr('search_query', '{}');
    };
};

function recalc_prices(column){
	if(column){
		// recalculate just this column
		subtotal = 0.00;
		discount_amount = 0.00;
		vat = 0.00;
		total = 0.00;
		discount = parseFloat($("#member_discount").val());
		$.each($('input[name="ar.'+column+'.Analyses:list:ignore_empty:record"]'), function(){
			disabled = $(this).attr('disabled');
			// For some browsers, `attr` is undefined; for others, its false.  Check for both.
			if (typeof disabled !== 'undefined' && disabled !== false) {
				disabled = true;
			} else {
				disabled = false;
			}
			if(!(disabled) && $(this).attr("checked")){
				serviceUID = this.id;
				form_price = parseFloat($("#"+serviceUID+"_price").val());
				vat_amount = parseFloat($("#"+serviceUID+"_price").attr("vat_amount"));
				if(discount){
					price = form_price - ((form_price / 100) * discount);
				} else {
					price = form_price;
				}
				subtotal += price;
				discount_amount += ((form_price / 100) * discount);
				vat += ((price / 100) * vat_amount);
				total += price + ((price / 100) * vat_amount);
			}
		});
		$('#ar_'+column+'_subtotal').val(subtotal.toFixed(2));
		$('#ar_'+column+'_subtotal_display').val(subtotal.toFixed(2));
		$('#ar_'+column+'_discount').val(discount_amount.toFixed(2));
		$('#ar_'+column+'_vat').val(vat.toFixed(2));
		$('#ar_'+column+'_vat_display').val(vat.toFixed(2));
		$('#ar_'+column+'_total').val(total.toFixed(2));
		$('#ar_'+column+'_total_display').val(total.toFixed(2));
	} else {
		// recalculate the entire form
		for (col=0; col<parseInt($("#col_count").val()); col++) {
			recalc_prices(String(col));
		}
	}
};

function changeReportDryMatter(){
	dm = $("#getDryMatterService")
	uid = $(dm).val();
	cat = $(dm).attr("cat");
	poc = $(dm).attr("poc");
	column = $(this).attr('column');
	if ($(this).attr("checked")){
		// only play with service checkboxes when enabling dry matter
		unsetAnalysisProfile(column);
		jQuery.ajaxSetup({async:false});
		toggleCat(poc, cat, $(this).attr("column"), selectedservices=[uid], force_expand=true);
		jQuery.ajaxSetup({async:true});
		dryservice_cb = $("input[column="+$(this).parents('td').attr("column")+"]:checkbox").filter("#"+uid);
		$(dryservice_cb).attr("checked", true);
		calcdependencies([$(dryservice_cb)], auto_yes = true);
		calculate_parts(column);
	}
	recalc_prices();
}


function showSelectCC(){
	contact_uid = $('#primary_contact').val();
	cc_uids = $('#cc_uids').attr('value');
	url = window.location.href.split("?")[0].split("/ar_add")[0].replace("/analysisrequests","")
	window.open(url+'/ar_select_cc?hide_uids=' + contact_uid + '&selected_uids=' + cc_uids,
		'ar_select_cc','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=600,height=550');
}

function changePrimaryContact(){
	contact_uid = $(this).val();
	elem = $("[uid="+contact_uid+"]");
	cc_data = $.parseJSON($(elem).attr("ccs"));
	$('#cc_uids').attr('value', $(elem).attr("cc_uids"));
	$('#cc_titles').val($(elem).attr("cc_titles"));
}

function copyButton(){
	field_name = $(this).attr("name");
	if ($(this).parent().attr('class') == 'service'){ // Analysis Service checkbox
		first_val = $('input[column="0"]').filter('#'+this.id).attr("checked");
		affected_elements = [];
		// 0 is the first column; we only want to change cols 1 onward.
		for (col=1; col<parseInt($("#col_count").val()); col++) {
			other_elem = $('input[column="'+col+'"]').filter('#'+this.id);
			disabled = other_elem.attr('disabled');
			// For some browsers, `attr` is undefined; for others, its false.  Check for both.
			if (typeof disabled !== 'undefined' && disabled !== false) {
				disabled = true;
			} else {
				disabled = false;
			}
			if (!disabled && !(other_elem.attr("checked")==first_val)) {
				other_elem.attr("checked", first_val?true:false);
				affected_elements.push(other_elem);
			}
			calculate_parts(col);
		}
		calcdependencies(affected_elements, true);
		recalc_prices();
	}
	else if ($('input[name^="ar\\.0\\.'+field_name+'"]').attr("type") == "checkbox") {
		// other checkboxes
		first_val = $('input[name^="ar\\.0\\.'+field_name+'"]').attr("checked");
		// col starts at 1 here; we don't copy into the the first row
		for (col=1; col<parseInt($("#col_count").val()); col++) {
			other_elem = $('#ar_' + col + '_' + field_name);
			if (!(other_elem.attr("checked")==first_val)) {
				other_elem.attr("checked", first_val?true:false);
			}
		}
		$('[id*=_' + field_name + "]").change();
	}
	else{
		first_val = $('input[name^="ar\\.0\\.'+field_name+'"]').val();
		// col starts at 1 here; we don't copy into the the first row
		for (col=1; col<parseInt($("#col_count").val()); col++) {
			other_elem = $('#ar_' + col + '_' + field_name);
			if (!(other_elem.attr("disabled"))) {
				if(field_name == 'SampleType'){ calculate_parts(col); }
				other_elem.val(first_val);
			}
		}
		$('[id*=_' + field_name + "]").change();
	}
}

function toggleCat(poc, category_uid, column, selectedservices,
                   force_expand, disable){
	// selectedservices and column are optional.
	// disable is used for field analyses - secondary ARs should not be able
	// to select these
	if(force_expand == undefined){ force_expand = false ; }
	if(disable == undefined){ disable = -1 ; }
	if(!column && column != 0) { column = ""; }

	tbody = $("#"+poc+"_"+category_uid);

	if($(tbody).hasClass("expanded")){
		// displaying an already expanded category
		if(selectedservices){
			for(service in tbody.children){
				service_uid = service.id;
				if(selectedservices.indexOf(service_uid) > -1){
					$(this).attr("checked", "checked");
				}
			}
			recalc_prices(column);
			$(tbody).toggle(true);
		} else {
			if (force_expand){ $(tbody).toggle(true); }
			else { $(tbody).toggle(); }
		}
	} else {
		if(!selectedservices) selectedservices = [];
		$(tbody).addClass("expanded");
		var options = {
			'selectedservices': selectedservices.join(","),
			'categoryUID': category_uid,
			'column': column,
			'disable': disable > -1 ? column : -1,
			'col_count': $("#col_count").attr('value'),
			'poc': poc
		};
        // possibly remove the fake ar context
        var url = window.location.href.split("/ar_add")[0] + "/analysisrequest_analysisservices";
		$(tbody).load(url, options,
			function(){
				// analysis service checkboxes
				$('input[name*="Analyses"]').unbind();
				$('input[name*="Analyses"]').bind('change', service_checkbox_change);
				if(selectedservices!=[]){
					recalc_prices(column);
				}
			}
		);
	}
}

function calcdependencies(elements, auto_yes) {
	// elements is a list of jquery checkbox objects
	// it's got one element in it when a single checkbox was changed,
	// and one from each column when a copy button was clicked.
	var element = elements.shift();
	if(auto_yes == undefined){ auto_yes = false ; }
	var column = $(element).attr('column');
	if (column == undefined || column == null) {
		column = '0';
	}
	var remaining_columns = [];
	for(var i = 0; i<elements.length; i++){
		remaining_columns.push($(elements[i]).attr('column'));
	}

	service_uid = $(element).attr('id');
	service_data = window.bika_utils.data.services[service_uid];
	if (service_data == undefined || service_data == null){
		// if service_uid is not in bika_utils.data.services, there are no deps.
		return;
	}
	deps = service_data['deps'];
	backrefs = service_data['backrefs'];

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
					if (! $('input[column="'+column+'"]').filter('#'+service[0]).attr("checked") ){
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
					dep_args.push([poc[0], cat[0], column, services]);
				}
			});
		});

		if (affected_services.length > 0) {
			$("body").append(
				"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
				_("<p>${service} requires the following services to be selected:</p><br/><p>${deps}</p><br/><p>Do you want to apply these selections now?</p>",
					{service:$(element).attr('title'),
					 deps: affected_titles.join("<br/>")})+"</div>");
				function add_Yes(){
					$.each(dep_args, function(i,args){
						tbody = $("#"+args[0]+"_"+args[1]);
						if ($(tbody).hasClass("expanded")) {
							// if cat is already expanded, we toggle(true) it and manually select service checkboxes
							$(tbody).toggle(true);
							$.each(args[3], function(x,serviceUID){
								$('input[column="'+args[2]+'"]').filter('#'+serviceUID).attr("checked", true);
								// if elements from more than one column were passed, set all columns to be the same.
								for(col in remaining_columns){
									$('input[column="'+remaining_columns[col]+'"]').filter('#'+serviceUID).attr("checked", true);
								}
							});
						} else {
							// otherwise, toggleCat will take care of everything for us
							jQuery.ajaxSetup({async:false});
							toggleCat(args[0], args[1], args[2], args[3]);
							jQuery.ajaxSetup({async:true});
						}
					});
					recalc_prices();
					calculate_parts(column);
					for(col in remaining_columns){
						calculate_parts(column);
					}
					$(this).dialog("close");
					$('#messagebox').remove();
				}
				function add_No(){
					$(element).attr("checked", false);
					recalc_prices();
					for(col in remaining_columns){
						e = $('input[column="'+remaining_columns[col]+'"]')
								.filter('#'+serviceUID);
						$(e).attr("checked", false);
					}
					recalc_prices(column);
					calculate_parts(column);
					for(col in remaining_columns){
						calculate_parts(column);
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
				$("#messagebox").dialog({width:450, resizable:false, closeOnEscape: false, buttons:{
							yes: add_Yes,
							no: add_No
							}});
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
				cb = $('input[column="'+column+'"]').filter('#'+serviceUID);
				if (cb.attr("checked")){
					affected_services.push(serviceUID);
					affected_titles.push(cb.attr('title'));
				}
			});
			$("body").append(
				"<div id='messagebox' style='display:none' title='" + _("Service dependencies") + "'>"+
				_("<p>The following services depend on ${service}, and will be unselected if you continue:</p><br/><p>${deps}</p><br/><p>Do you want to remove these selections now?</p>",
					{service:$(element).attr('title'),
					 deps: affected_titles.join("<br/>")})+"</div>");
			yes = _("Yes");
			no = _("No");
			if (affected_services.length > 0) {
				$("#messagebox").dialog({width:450, resizable:false, closeOnEscape: false, buttons:{
					yes: function(){
						for(as=0;as<affected_services.length;as++){
							serviceUID = affected_services[as];
							cb = $('input[column="'+column+'"]')
								.filter('#'+serviceUID).attr('checked', false);
							$(".partnr_"+serviceUID).filter('[column=]'+column)
								.empty();
							if ($(cb).val() == $("#getDryMatterService").val()) {
								$("#ar_"+column+"_ReportDryMatter").attr("checked", false);
							}
							// if elements from more than one column were passed, set all columns to be the same.
							for(col in remaining_columns){
								cb = $('input[column="'+remaining_columns[col]+'"]')
									.filter('#'+serviceUID).attr("checked", false);
								$(".partnr_"+serviceUID).filter('[column=]'+col)
									.empty();
								if ($(cb).val() == $("#getDryMatterService").val()) {
									$("#ar_"+col+"_ReportDryMatter").attr("checked", false);
								}
							}
						};
						recalc_prices();
						calculate_parts(column);
						for(col in remaining_columns){
							calculate_parts(column);
						}
						$(this).dialog("close");
						$('#messagebox').remove();
					},
					no:function(){
						$(element).attr("checked", true);
						for(col in remaining_columns){
							$('input[column="'+remaining_columns[col]+'"]').filter('#'+serviceUID).attr("checked", true);
						}
						recalc_prices(column);
						$(this).dialog("close");
						calculate_parts(column);
						for(col in remaining_columns){
							calculate_parts(column);
						}
						$('#messagebox').remove();
					}
				}});
			} else {
				$('#messagebox').remove();
			}
		}
	}
}

function calculate_parts(column){

//	console.log("===================================");

	// Template columns are not calculated
	if ($("#ar_"+column+"_Template").val() != ''){
		return;
	}

	// gather up SampleType UID
	var st_title = $("#ar_"+column+"_SampleType").val();
	sampletype = window.bika_utils.data.st_uids[st_title];
	if (sampletype != undefined && sampletype != null){
		st_uid = sampletype['uid'];
		st_minvol = sampletype['minvol'].split(" ")[0];
		if(st_minvol.length == 0){
			st_minvol = 0;
		} else {
			st_minvol = parseFloat(st_minvol, 10);
		}
	} else {
		// all unchecked services have their part numbers removed
		ep = $("[class^='partnr_']").filter("[column="+column+"]").not(":empty");
		for(i=0;i<ep.length;i++){
			em = ep[i];
			uid = $(ep[0]).attr('class').split("_")[1]
			cb = $("#"+uid);
			if ( ! $(cb).attr('checked') ){
				$(em).empty();
			}
		}
		return;
	}
//	console.log("Sampletype: "+st_uid);

	// gather up selected service uids
	var checked = $('[name^="ar\\.'+column+'\\.Analyses"]').filter(':checked');
	service_uids = []
	for(i=0;i<checked.length;i++){
		e = checked[i];
		var uid = $(e).attr('value');
		service_uids.push(uid);
	}

	// skip everything if no selected services in this column
	if (service_uids.length == 0){
		// all unchecked services have their part numbers removed
		ep = $("[class^='partnr_']").filter("[column="+column+"]").not(":empty");
		for(i=0;i<ep.length;i++){
			em = ep[i];
			uid = $(ep[0]).attr('class').split("_")[1]
			cb = $("#"+uid);
			if ( ! $(cb).attr('checked') ){
				$(em).empty();
			}
		}
		return;
	}

	parts = window.bika_utils.calculate_partitions(service_uids, st_uid, st_minvol);

	// Set new part numbers in hidden form field
	formparts = $.parseJSON($("#parts").val());
	formparts[column] = parts
	$("#parts").val($.toJSON(formparts));

	// write new part numbers next to checkboxes
	$.each(parts, function(p,part){
		$.each(part['services'], function(s,service_uid){
			$(".partnr_"+service_uid).filter("[column="+column+"]")
				.empty().append(p+1);
		});
	});

}

function uncheck_partnrs(column){
	// all unchecked services have their part numbers removed
	ep = $("[class^='partnr_']").filter("[column="+column+"]").not(":empty");
	for(i=0;i<ep.length;i++){
		em = ep[i];
		uid = $(ep[0]).attr('class').split("_")[1]
		cb = $("#"+uid);
		if ( ! $(cb).attr('checked') ){
			$(em).empty();
		}
	}
}

function unsetTemplate(column){
	if($("#ar_"+column+"_Template").val() != ""){
		$("#ar_"+column+"_Template").val("");
	}
}

function unsetAnalysisProfile(column){
	if($("#ar_"+column+"_Profile").val() != ""){
		$("#ar_"+column+"_Profile").val("");
	}
}

function unsetAnalyses(column){
	$.each($('input[name^="ar.'+column+'.Analyses"]'), function(){
		if($(this).attr("checked")) $(this).attr("checked", "");
		$(".partnr_"+this.id).filter("[column="+column+"]")
			.empty();
	});
}

function resolve_uid(catalog, query){
	var UID = '';
	query = $.toJSON(query);
	jQuery.ajaxSetup({async:false});
	$.get(window.location.href.split("/ar_add")[0] + '/referencewidget_search?',
		{'_authenticator': $('input[name="_authenticator"]').val(),
	     'base_query': query,
	     'catalog_name': catalog,
	     'searchTerm':'',
	     'page':1,
	     'rows':10,
	     'sidx':'',
	     'sord':''
	    },
		function(data){
			UID = data['rows'][0]['UID'];
		},
		dataType='json'
	);
	jQuery.ajaxSetup({async:true});
	return UID;
}

function setTemplate(column,template_title){
	var templateUID = resolve_uid('bika_setup_catalog',
		                          {'portal_type': 'ARTemplate',
	                               'title': template_title});
	if(templateUID == "") return;

	template_data = $.parseJSON($("#template_data").val())[templateUID];
	analyses = template_data['Analyses'];

	// always remove DryMatter - the Template can put it back.
	$("#ar_"+column+"_ReportDryMatter").attr("checked", false);

	// set our template fields
	// SampleType and SamplePoint are strings - the item's Title.
	unsetAnalyses(column);

	st_title = template_data['SampleType'];
	st_uid = template_data['SampleType_uid'];
	sp_title = template_data['SamplePoint'];
	sp_uid = template_data['SamplePoint_uid'];
	$('#ar_'+column+'_SampleType').val(st_title);
	$('#ar_'+column+'_SampleType_uid').val(st_uid);
	$('#ar_'+column+'_SamplePoint').val(sp_title);
	$('#ar_'+column+'_SamplePoint_uid').val(sp_uid);

	dm = template_data['ReportDryMatter'];
	$('#ar_'+column+'_ReportDryMatter').attr('checked', dm);

	$('#ar_'+column+'_Profile').val(template_data['Profile']);
	$('#ar_'+column+'_Profile_uid').val(template_data['Profile_uid']);

	// Apply Template analyses/parts
	parts = []; // #parts[column] will contain this dictionary
	for(pi=0;pi<template_data['Partitions'].length;pi++){
		P = template_data['Partitions'][pi];
		partnr = parseInt(P['part_id'].split("-")[1], 10);
		cu = P['container_uid'];
		if(cu != null && cu != undefined && cu.length > 1 && cu[0] != ""){ cu = [cu]; }
		else { cu = []; }
		pu = P['preservation_uid'];
		if(pu != null && pu != undefined && pu.length > 1 && pu[0] != ""){
			pu = [pu];
		}
		else {
			pu = [];
		}
		parts[partnr-1] = {'container':cu,
							'preservation':pu,
							'services':[]}
	}

	template_services = {};
	template_parts = {};
	analyses = template_data['Analyses'];
	for(i=0;i<analyses.length;i++){
		key = analyses[i]['service_poc'] + "_" + analyses[i]['category_uid'];
		if (template_services[key] == undefined){
			template_services[key] = [];
		}
		service_uid = analyses[i]['service_uid'];
		template_services[key].push(service_uid);
		template_parts[service_uid] = analyses[i]['partition'];
	}

	$.each(template_services, function(poc_categoryUID, selectedservices){
		if( $("tbody[class*='expanded']").filter("#"+poc_categoryUID).length > 0 ){
			$.each(selectedservices, function(i,uid){
				$.each($("input[column='"+column+"']").filter("#"+uid), function(x, e){
					$(e).attr('checked', true);
					partnr = template_parts[uid].split("-")[1];
					$(".partnr_"+uid).filter("[column="+column+"]")
						.empty().append(partnr);
					partnr = parseInt(partnr,10);
					parts[partnr-1]['services'].push(uid);
				});
			});
		} else {
			p_c = poc_categoryUID.split("_");
			jQuery.ajaxSetup({async:false});
			toggleCat(p_c[0], p_c[1], column, selectedservices);
			jQuery.ajaxSetup({async:true});
			$.each(selectedservices, function(i,uid){
				partnr = template_parts[uid].split("-")[1];
				$(".partnr_"+uid).filter("[column="+column+"]")
					.empty().append(partnr);
				partnr = parseInt(partnr,10);
				parts[partnr-1]['services'].push(uid);
			});
		}
	});

	// Set new part numbers in hidden form field
	formparts = $.parseJSON($("#parts").val());
	formparts[column] = parts
	$("#parts").val($.toJSON(formparts));

	recalc_prices(column);
}

function setAnalysisProfile(column, profile_title){
	var profileUID = resolve_uid('bika_setup_catalog',
		                          {'portal_type': 'AnalysisProfile',
	                               'title': profile_title});
	if(profileUID == "") return;
	unsetAnalyses(column);

	profile_data = $.parseJSON($("#profile_data").val())[profileUID];
	profile_services = profile_data['Services'];

	// always remove DryMatter - the Template can put it back.
	$("#ar_"+column+"_ReportDryMatter").attr("checked", false);

	$.each(profile_services, function(poc_categoryUID, selectedservices){
		if( $("tbody[class*='expanded']").filter("#"+poc_categoryUID).length > 0 ){
			$.each(selectedservices, function(i,uid){
				$.each($("input[column='"+column+"']").filter("#"+uid), function(x, e){
					$(e).attr('checked', true);
				});
				recalc_prices(column);
			});
		} else {
			p_c = poc_categoryUID.split("_");
			jQuery.ajaxSetup({async:false});
			toggleCat(p_c[0], p_c[1], column, selectedservices);
			jQuery.ajaxSetup({async:true});
		}
	});

	calculate_parts(column);
}

function service_checkbox_change(){
	var column = $(this).attr("column");
	var element = $(this);
	unsetAnalysisProfile(column);
	unsetTemplate(column);

	// Unselecting Dry Matter Service unsets 'Report Dry Matter'
	if ($(this).val() == $("#getDryMatterService").val()
	    && $(this).attr("checked") == false) {
		$("#ar_"+column+"_ReportDryMatter").attr("checked", false);
	}

	// unselecting service: remove part number.
	if (!$(this).attr('checked')){
		$(".partnr_"+this.id).filter("[column="+column+"]")
			.empty();
	}

	calcdependencies([element]);
	recalc_prices();
	calculate_parts(column);
};


function clickAnalysisCategory(){
	toggleCat($(this).attr("poc"), $(this).attr("cat")); // cat is a category uid
	if($(this).hasClass('expanded')){
		$(this).addClass('collapsed');
		$(this).removeClass('expanded');
	} else {
		$(this).removeClass('collapsed');
		$(this).addClass('expanded');
	}
}

$(document).ready(function(){

	_ = jarn.i18n.MessageFactory('bika');
	PMF = jarn.i18n.MessageFactory('plone');

	var curDate = new Date();
	var y = curDate.getFullYear();
	var limitString = '1900:' + y;
	var dateFormat = _("date_format_short_datepicker");

	ar_rename_elements();
	ar_referencewidget_lookups();

	// Sampling Date field is readonly to prevent invalid data entry, so
	// clicking SamplingDate field clears existing values.
	// clear date widget values if the page is reloaded.
	e = $('input[id$="_SamplingDate"]');
	if(e.length > 0){
		if($($(e).parents('form').children('[name=came_from]')).val() == 'add'){
			$(e)
			.datepicker({
				showOn:'focus',
				showAnim:'',
				changeMonth:true,
				changeYear:true,
				dateFormat: dateFormat,
				yearRange: limitString
			})
			.click(function(){$(this).attr('value', '');})
		} else {
			$(e)
			.datepicker({
				showOn:'focus',
				showAnim:'',
				changeMonth:true,
				changeYear:true,
				dateFormat: dateFormat,
				yearRange: limitString
			})
		}
	}

	$("input[id*=_Template]").live('change', function(){
		column = this.id.split('_')[1];
		unsetAnalysisProfile(column);
		setTemplate(column, $(this).val());
	});

	$("input[id*=_Profile").live('change', function(){
		column = $(this).attr("column");
		unsetTemplate(column,$(this).val());
		setAnalysisProfile(column);
		calculate_parts(column);
	});

	$(".copyButton").live('click',  copyButton );

	$('th[class^="analysiscategory"]').click(clickAnalysisCategory);

	$("#primary_contact").live('change', changePrimaryContact );

	$("input[name^='Price']").live('change', recalc_prices );

	$('#open_cc_browser').click(showSelectCC);

	$("input[id*=_ReportDryMatter]").change(changeReportDryMatter);

    // AR Add/Edit ajax form submits
	ar_edit_form = $('#analysisrequest_edit_form');
	if (ar_edit_form.ajaxForm != undefined){
		var options = {
			url: window.location.href
				.split("?")[0]
				.split("/ar_add")[0]
				.split("/base_edit")[0]
				.replace("analysisrequests", "") + "/analysisrequest_submit",
			dataType: 'json',
			data: {'_authenticator': $('input[name="_authenticator"]').val()},
			beforeSubmit: function(formData, jqForm, options) {
				$("input[class~='context']").attr('disabled',true);
			},
			success: function(responseText, statusText, xhr, $form) {
				if(responseText['success'] != undefined){
					if(responseText['labels'] != undefined){
						destination = window.location.href
							.split("?")[0]
							.replace("/ar_add","")
							.replace("/analysisrequests", "")
							.replace("/base_edit", "");
						ars = responseText['labels'];
						labelsize = responseText['labelsize'];
						q = "/sticker?size="+labelsize+"&items=";
						q = q + ars.join(",");
						window.location.replace(destination+q);
					} else {
						destination = window.location.href
							.split("?")[0]
							.split("/ar_add")[0]
							.replace("/analysisrequests","")
							.replace("/base_edit", "/base_view");
						window.location.replace(destination);
					}
				} else {
					msg = ""
					for(error in responseText['errors']){
						x = error.split(".");
						if (x.length == 2){
							e = x[1] + ", Column " + (+x[0]) + ": ";
						} else {
							e = "";
						}
						msg = msg + e + responseText['errors'][error] + "<br/>";
					};
					window.bika_utils.portalMessage(msg);
					window.scroll(0,0);
					$("input[class~='context']").removeAttr('disabled');
				}
			},
			error: function(XMLHttpRequest, statusText, errorThrown) {
				window.bika_utils.portalMessage(statusText);
				window.scroll(0,0);
				$("input[class~='context']").removeAttr('disabled');
			},
		};
		$('#analysisrequest_edit_form').ajaxForm(options);
	}

	// these go here so that popup windows can access them in our context
	window.recalc_prices = recalc_prices;
	window.calculate_parts = calculate_parts;
	window.toggleCat = toggleCat;

});
}(jQuery));
