
jQuery( function($) {

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

	function toggleCat(poc, category_uid, column, selectedservices, force_expand, disable){
		// selectedservices and column are optional.
		// force_expand and disable are for secondary ARs
		// They are used when selecting an AR Profile or making a secondary AR
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
			$(tbody).load("analysisrequest_analysisservices", options,
				function(){
					// analysis service checkboxes
					$('input[name*="Analyses"]').unbind();
					$('input[name*="Analyses"]').bind('change', service_checkbox_change);
					if(selectedservices!=[]){
						recalc_prices(column);
						// XXX template should do this one for us
						calculate_parts();
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
		var remaining_columns = [];
		for(var i = 0; i<elements.length; i++){
			remaining_columns.push($(elements[i]).attr('column'));
		}

		service_uid = $(element).attr('id');
		formdata = $("body").data()['ar_formdata'];
		service_data = formdata['services'][service_uid];
		if (service_data == undefined || service_data == null){
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
								toggleCat(args[0], args[1], args[2], args[3]);
							}
						});
						recalc_prices();
						$(this).dialog("close");
						$('#messagebox').remove();
						calculate_parts();
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
						$(this).dialog("close");
						$('#messagebox').remove();
						calculate_parts();
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
							$.each(affected_services, function(i,serviceUID){
								cb = $('input[column="'+column+'"]').filter('#'+serviceUID).attr('checked', false);
								if ($(cb).val() == $("#getDryMatterService").val()) {
									$("#ar_"+column+"_ReportDryMatter").attr("checked", false);
								}
								// if elements from more than one column were passed, set all columns to be the same.
								for(col in remaining_columns){
									cb = $('input[column="'+remaining_columns[col]+'"]').filter('#'+serviceUID).attr("checked", false);
									if ($(cb).val() == $("#getDryMatterService").val()) {
										$("#ar_"+col+"_ReportDryMatter").attr("checked", false);
									}
								}
							});
							recalc_prices();
							$(this).dialog("close");
							$('#messagebox').remove();
							calculate_parts();
						},
						no:function(){
							$(element).attr("checked", true);
							for(col in remaining_columns){
								$('input[column="'+remaining_columns[col]+'"]').filter('#'+serviceUID).attr("checked", true);
							}
							recalc_prices(column);
							$(this).dialog("close");
							$('#messagebox').remove();
							calculate_parts();
						}
					}});
				} else {
					$('#messagebox').remove();
				}
			}
		}
	}

	function calculate_parts(){
		var formvalues = {};
		var partitionable = 0;
		var partitioned_services = $.parseJSON($("#partitioned_services").val());
		// gather up SampleType and all selected service checkboxes by column
		for (var col=0; col<parseInt($("#col_count").val()); col++) {
			var st_title = $("#ar_"+col+"_SampleType").val();
			formvalues[parseInt(col)] = {'st_title':st_title, 'services': []};
			var checkboxes_checked = $('[name^="ar\\.'+col+'\\.Analyses"]').filter(':checked');
			for(i=0;i<checkboxes_checked.length;i++){
				e = checkboxes_checked[i];
				var uid = $(e).attr('value');
				if(partitioned_services != null
				   && partitioned_services.indexOf(uid) > -1){
					partitionable++;
				}
				formvalues[parseInt(col)]['services'].push(uid);
			}
		}

		// all unchecked services have their part numbers removed
		ep = $("[class^='partnr_']").not(":empty");
		for(i=0;i<ep.length;i++){
			em = ep[i];
			uid = $(ep[0]).attr('class').split("_")[1]
			cb = $("#"+uid);
			if ( ! $(cb).attr('checked') ){
				$(em).empty();
			}
		}

		// remove all and skip everything if no selected
		// services have partition setup info
		if (partitionable == 0){
			$.each($('[name$="\\.Analyses"]').filter(':checked'), function(i,e){
				$(".partnr_"+$(e).attr('value')).filter("[column="+col+"]").empty();
			});
			return;
		}

		formdata = $("body").data()['ar_formdata'];

		// parts is where we will store the table of which services
		// belong to which partition, for each column.
		// a 'partition' is a slice of this dictionary:
		parts = [];

		// formvalues looks like this:
		// formvalues[col] = {services: [uid,uid], st_title: sampletype title}

		for (col=0; col<parseInt($("#col_count").val()); col++) {
			// blank entry for each column
            parts.push([]);

			// get column field values
			st_title = formvalues[col]['st_title'];
			st_uid = formdata['st_uids'][st_title];
			if (st_uid != undefined && st_uid != null){
				st_uid = st_uid['uid'];
			} else {
				st_uid = '';
			}
			service_uids = formvalues[col]['services']

			// loop through each selected service, assigning or creating
			// partitions as we go.
            for(i=0;i<service_uids.length;i++){
				service_uid = service_uids[i];

				// part_setup is filled with defaults here, if it is not
				// already defined
				z = formdata['services'][service_uid];
				if(z == undefined || z == null) {
					formdata['services'][service_uid] = {
						'Separate': false,
						'Container': [],
						'Preservation': [],
						'PartitionSetup': ''
					}
					continue;
				}

				// set service default partition setup field values
				separate = formdata['services'][service_uid]['Separate'];
				container = formdata['services'][service_uid]['Container'];
				preservation = formdata['services'][service_uid]['Preservation'];
				// discover if a more specific part_setup exists for this
				// sample_type and service_uid
				part_setup = '';
				$.each(formdata['services'][service_uid]['PartitionSetup'],
					function(x, ps){
						if(ps['sampletype'] == st_uid){
							part_setup = ps;
							return false;
						}
					}
				);
				// if it does, we use it instead of defaults.
				if (part_setup != '') {
					separate = part_setup['separate'];
					container = part_setup['container'];
					preservation = part_setup['preservation'];
				}

				if (separate) {

                    // create a separate partition for this analysis.
					// partition container and preservation remain plural.
                    part = {'services': [service_uid],
                            'separate': true,
                            'container': container,
                            'preservation': preservation};
                    parts[col].push(part);

				} else {

					// So now we either need to find an existing partition
					// which permits us to add this analysis to it, or
					// create a new one.
					found_part = '';

					for(x=0; x<parts[col].length;x++){
						part = parts[col][x];
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
								return (part['container'].indexOf(container) > -1);
							});
							if (c_intersection.length == 0){
								// no match
								continue;
							}
						}
						// if no preservation info is provided by either the
						// partition OR the service, this partition is available
						var p_intersection = [];
						if (part['preservation'].length > 0 || preservation.length > 0) {
							// check our preservation against this partition's
							p_intersection = $.grep(preservation, function(c, y){
								return (part['preservation'].indexOf(preservation) > -1);
							});
							if (p_intersection.length == 0){
								// no match
								continue;
							}
						}

						// other conditions

						// all the conditions passed:
						found_part = x;
						parts[col][x]['services'].push(service_uid);
						parts[col][x]['container'] = c_intersection;
						parts[col][x]['preservation'] = p_intersection;
						break;
					}

					if (found_part === ''){
						// No home found - make a new part for this analysis
						part = {'services': [service_uid],
								'separate': false,
								'container': container,
								'preservation': preservation};
						parts[col].push(part);
					}
				}
			}
			// unset all this column's part numbers if 0 or 1 partitions
			if(parts[col].length < 2){
				$.each($('[name^="ar\\.'+col+'\\.Analyses"]').filter(':checked'), function(i,e){
					$(".partnr_"+$(e).attr('value')).filter("[column="+col+"]").empty();
				});
			} else {
				$.each(parts[col], function(p,part){
					$.each(part['services'], function(s,service_uid){
						$(".partnr_"+service_uid).filter("[column="+col+"]").empty().append(p+1);
					});
				});
			}
		}
		$("#parts").val($.toJSON(parts));
	}

	function service_checkbox_change(){
		var column = $(this).attr("column");
		var element = $(this);
		if($("#ar_"+column+"_ARProfile").val() != ""){
			$("#ar_"+column+"_ARProfile").val("");
		}
		if ($(this).val() == $("#getDryMatterService").val() && $(this).attr("checked") == false) {
			$("#ar_"+column+"_ReportDryMatter").attr("checked", false);
		}
		calcdependencies([element]);
		recalc_prices();
		calculate_parts();
	};

	function unsetARTemplate(column){
		$('input[name^="ar.'+column+'.SampleType"]').val('');
		$('input[name^="ar.'+column+'.SamplePoint"]').val('');
		$('input[name^="ar.'+column+'.Composite"]').attr("checked", false);
		$('input[name^="ar.'+column+'.InvoiceExclude"]').attr("checked", false);
		$('input[name^="ar.'+column+'.ReportDryMatter"]').attr("checked", false);
	}

	function unsetARProfile(column){
		$.each($('input[name^="ar.'+column+'.Analyses"]'), function(){
			if($(this).attr("checked")) $(this).attr("checked", "");
		});
	}

	function setARTemplate(){
		templateUID = $(this).val();
		column = $(this).attr("column");
		unsetARTemplate(column);
		if(templateUID == "") return;

		formdata = $("body").data()['ar_formdata'];
		template_data = formdata['templates'][templateUID];

		// set ARProfile
		$('#ar_'+column+'_ARProfile').val(template_data['ARProfile']);
		$('#ar_'+column+'_ARProfile').change();

		// set our template fields
		// SampleType and SamplePoint are strings - the item's Title.
		$('#ar_'+column+'_SampleType').val(template_data['SampleType']);
		$('#ar_'+column+'_SamplePoint').val(template_data['SamplePoint']);

		$('#ar_'+column+'_Composite').attr('checked', template_data['Composite']);
		$('#ar_'+column+'_ReportDryMatter').attr('checked', template_data['ReportDryMatter']);
		$('#ar_'+column+'_InvoiceExclude').attr('checked', template_data['InvoiceExclude']);

	}

	function setARProfile(){
		profileUID = $(this).val();
		column = $(this).attr("column");
		unsetARProfile(column);
		if(profileUID == "") return;

		formdata = $("body").data()['ar_formdata'];
		profile_data = formdata['profiles'][profileUID];
		profile_services = profile_data['Services'];

		// Why is ReportDryMatter getting turned off explicity here
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
		calculate_parts();
	}


	$(document).ready(function(){

		_ = window.jsi18n;

//  change url to prevent caching
//		$.getJSON('ar_formdata?' + new Date().getTime(), function(data) {
		$.getJSON('ar_formdata',
			{'_authenticator': $('input[name="_authenticator"]').val()},
			function(data) {
				$('body').data('ar_formdata', data);

				// Contact dropdown is set in TAL to a default value.
				// we force change it to run the primary_contact .change()
				// code - but the ajax for ar_formdata must complete first.
				// So it goes here, in the ajax complete handler.
				contact_element = $("#primary_contact");
				if(contact_element.length > 0) {
					contact_element.change();
				}

			}
		);

		// If any required fields are missing, then we hide the Plone UI
		// transitions for Sampled and Preserved, and use our own buttons instead
		// (Save)
		if ($("#DateSampled").val() == "" || $("#Sampler").val() == "") {
			$("#workflow-transition-sampled").parent().toggle(false);
		}
		$("#workflow-transition-preserved").parent().toggle(false);

		// Sampling Date field is readonly to prevent invalid data entry, so
		// clicking SamplingDate field clears existing values.
		// clear date widget values if the page is reloaded.
		e = $('input[id$="_SamplingDate"]');
		if(e.length > 0){
			// XXX Datepicker format is not i18n aware (dd Oct 2011)
			if($($(e).parents('form').children('[name=came_from]')).val() == 'add'){
				$(e)
				.datepicker({'dateFormat': 'dd M yy', showAnim: ''})
				.click(function(){$(this).attr('value', '');})
			} else {
				$(e)
				.datepicker({'dateFormat': 'dd M yy', showAnim: ''})
			}
		}

		// define these for each autocomplete dropdown individually
		// this is done like this so that they can depend on each other's
		// values
		for (col=0; col<parseInt($("#col_count").val()); col++) {
			$("#ar_"+col+"_SamplePoint").autocomplete({
				minLength: 0,
				source: function(request,callback){
					$.getJSON('ajax_samplepoints',
						{'term':request.term,
						 'sampletype':$("#ar_"+window._ac_focus.id.split("_")[1]+"_SampleType").val(),
						 '_authenticator': $('input[name="_authenticator"]').val()},
						function(data,textStatus){
							callback(data);
						}
					);
				}
			});
			$("#ar_"+col+"_SampleType").autocomplete({
				minLength: 0,
				source: function(request,callback){
					$.getJSON('ajax_sampletypes',
						{'term':request.term,
						 'samplepoint':$("#ar_"+window._ac_focus.id.split("_")[1]+"_SamplePoint").val(),
						 '_authenticator': $('input[name="_authenticator"]').val()},
						function(data,textStatus){
							callback(data);
						}
					);
				}
			});
		}
		$("select[class='ARTemplate']").change(setARTemplate);
		$("select[class='ARProfile']").change(setARProfile);

		// when SamplePoint is selected, reset Composite flag to SP value
		$(".samplepoint").focus(function(){
			window._ac_focus = this;
		});
		function set_sp(e){
			col = e.id.split("_")[1];
			sp = formdata['sp_uids'][$(e).val()];
			if (sp != undefined && sp != null){
				$("#ar_"+col+"+Composite").attr("checked", sp['composite']);
			}
		}
		$(".samplepoint").change(function(){
			set_sp(this);
		});
		$(".samplepoint").blur(function(){
			set_sp(this);
		});

		// changing sampletype sets partition numbers.
		// it's done funny, because autocomplete didn't like .change()
		// and autocomplete's callback fires at the wrong time.
		$(".sampletype").focus(function(){
			window._ac_focus = this;
		});
		$(".sampletype").blur(function(){
			if ($(this).val() != $(window._ac_focus).val()){
				calculate_parts();
			}
		})
		// also set on .change() though,
		// because sometimes we set these fields manually.
		$(".sampletype").change(function(){
			calculate_parts()
		});

		$(".copyButton").live('click',  function (){
			field_name = $(this).attr("name");
			if ($(this).hasClass('ARTemplateCopyButton')){ // Template selector
				first_val = $('#ar_0_ARTemplate').val();
				for (col=1; col<parseInt($("#col_count").val()); col++) {
					$("#ar_"+col+"_ARTemplate").val(first_val);
					$("#ar_"+col+"_ARTemplate").change();
				}
			}
			else if ($(this).hasClass('ARProfileCopyButton')){ // Profile selector
				first_val = $('#ar_0_ARProfile').val();
				for (col=1; col<parseInt($("#col_count").val()); col++) {
					$("#ar_"+col+"_ARProfile").val(first_val);
					$("#ar_"+col+"_ARProfile").change();
				}
			}
			else if ($(this).parent().attr('class') == 'service'){ // Analysis Service checkbox
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
				}
				calcdependencies(affected_elements, true);
				recalc_prices();
				calculate_parts();
			}
			else if ($('input[name^="ar\\.0\\.'+field_name+'"]').attr("type") == "checkbox") {
				// other checkboxes
				first_val = $('input[name^="ar\\.0\\.'+field_name+'"]').attr("checked");
				// col starts at 1 here; we don't copy into the the first row
				for (col=1; col<parseInt($("#col_count").val()); col++) {
					other_elem = $('#ar_' + col + '_' + field_name);
					if (!(other_elem.attr("checked")==first_val)) {
						other_elem.attr("checked", first_val?true:false);
						other_elem.change();
					}
				}
			}
			else{
				first_val = $('input[name^="ar\\.0\\.'+field_name+'"]').val();
				// col starts at 1 here; we don't copy into the the first row
				for (col=1; col<parseInt($("#col_count").val()); col++) {
					other_elem = $('#ar_' + col + '_' + field_name);
					if (!(other_elem.attr("disabled"))) {
						other_elem.val(first_val);
						other_elem.change();
					}
				}
			}
		});

		// Clicking the category name will expand the services list for that category
		$('th[class^="analysiscategory"]').click(function(){
			toggleCat($(this).attr("poc"), $(this).attr("cat")); // cat is a category uid
			if($(this).hasClass('expanded')){
				$(this).addClass('collapsed');
				$(this).removeClass('expanded');
			} else {
				$(this).removeClass('collapsed');
				$(this).addClass('expanded');
			}
		});

		// service category pre-expanded rows
		// These are in AR Edit only
		selected_elements = [];
		prefilled = false;
		$.each($('th[class$="prefill"]'), function(i,e){
			prefilled = true;
			selectedservices = $(e).attr("selectedservices").split(",");
			toggleCat($(e).attr("poc"), $(e).attr("cat"), 0, selectedservices); // AR Edit has only column 0
			selected_elements.push($(e));
		});
		if (prefilled){
			calcdependencies(selected_elements);
			recalc_prices();
		}

		// Contact dropdown changes
		$("#primary_contact").live('change', function(){
			formdata = $("body").data()['ar_formdata'];
			cc_data = formdata['contact_ccs'][$(this).val()];
			// This comma-separated value is used as part of the URL to the
			// cc_selector popup, when that changes to a proper lookup field,
			// this can go away.
			$('#cc_uids').attr("value", cc_data['cc_uids']);
			$('#cc_titles').val(cc_data['cc_titles']);
		});

		// recalculate when price elements' values are changed
		$("input[name^='Price']").live('change', function(){
			recalc_prices();
		});

		// A button in the AR form displays the CC browser window (select_cc.pt)
		$('#open_cc_browser').click(function(){
			contact_uid = $('#primary_contact').val();
			cc_uids = $('#cc_uids').val();
			window.open('analysisrequest_select_cc?hide_uids=' + contact_uid + '&selected_uids=' + cc_uids,
				'analysisrequest_select_cc','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=600,height=550');
		});

		// analysisrequest select CC submit button invokes this
		$('.select_cc_select').click(function(){
			var uids = [];
			var titles = [];
			$.each($('input[name="paths:list"]'), function() {
				if($(this).attr("checked")){
					uids.push($(this).attr("uid"));
					titles.push($(this).attr("title"));
				}
			});
			window.opener.$("#cc_uids").val(uids.join(","));
			window.opener.$("#cc_titles").val(titles.join(","));
			window.close();
		});

		// button in each column to display Sample browser window
		$('input[id$="_SampleID_button"]').click(function(){
			column = this.id.split("_")[1];
			window.open('analysisrequest_select_sample?column=' + column,
				'analysisrequest_select_sample','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=600,height=550');
		});

		$(".deleteSampleButton").click(function(){
			column = $(this).attr('column');
			$("#ar_"+column+"_SampleID_button").val($("#ar_"+column+"_SampleID_default").val());
			$("#ar_"+column+"_SampleID").val('');
			$("#ar_"+column+"_ClientReference").val('').removeAttr("readonly");
			// XXX Datepicker format is not i18n aware (dd Oct 2011)
			$("#ar_"+column+"_SamplingDate")
				.datepicker({'dateFormat': 'dd M yy', showAnim: ''})
				.click(function(){$(this).attr('value', '');})
				.attr('value', '');
			$("#ar_"+column+"_ClientSampleID").val('').removeAttr("readonly");
			$("#ar_"+column+"_SamplePoint").val('').removeAttr("readonly");
			$("#ar_"+column+"_SampleType").val('').removeAttr("readonly");
			$("#ar_"+column+"_Composite").attr('checked', false).removeAttr("disabled");
			$("#deleteSampleButton_" + column).toggle(false);
			// uncheck and enable all visible service checkboxes
			$("input[id*='_"+column+"_']").filter(".cb").removeAttr('disabled').attr('checked', false);
			recalc_prices();
		});

		// ReportDryMatter
		$(".ReportDryMatter").change(function(){
			dm = $("#getDryMatterService")
		    uid = $(dm).val();
			cat = $(dm).attr("cat");
			poc = $(dm).attr("poc");
			if ($(this).attr("checked")){
				// only play with service checkboxes when enabling dry matter
				jQuery.ajaxSetup({async:false});
				toggleCat(poc, cat, $(this).attr("column"), selectedservices=[uid], force_expand=true);
				jQuery.ajaxSetup({async:true});
				dryservice_cb = $("input[column="+$(this).attr("column")+"]:checkbox").filter("#"+uid);
				$(dryservice_cb).attr("checked", true);
				calcdependencies([$(dryservice_cb)], auto_yes = true);
			}
			recalc_prices();
		});

		function portalMessage(message){
			str = "<dl class='portalMessage error'>"+
				"<dt>Error</dt>"+
				"<dd><ul>" + message +
				"</ul></dd></dl>";
			$('.portalMessage').remove();
			$(str).appendTo('#viewlet-above-content');
		}

		// AR Add/Edit ajax form submits
		ar_edit_form = $('#analysisrequest_edit_form');
		if (ar_edit_form.ajaxForm != undefined){
			var options = {
				url: window.location.href.replace("/analysisrequest_add","/analysisrequest_submit").
					 replace("/base_edit","/analysisrequest_submit"),
				dataType: 'json',
				data: {'_authenticator': $('input[name="_authenticator"]').val()},
				beforeSubmit: function(formData, jqForm, options) {
					$("input[class~='context']").attr('disabled',true);
				},
				success: function(responseText, statusText, xhr, $form)  {
					if(responseText['success'] != undefined){
						if(responseText['labels'] != undefined){
							destination = window.location.href.replace("/analysisrequest_add","");
							destination = destination.replace("/base_edit", "");
							ars = responseText['labels'];
							labelsize = responseText['labelsize'];
							if (labelsize == "small"){
								q = "/sticker?size=small&items=";
							} else {
								q = "/sticker?items=";
							}
							q = q + ars.join(",");
							window.location.replace(destination+q);
						} else {
							destination = window.location.href.replace("/analysisrequest_add","");
							destination = destination.replace("/base_edit", "/base_view");
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
						portalMessage(msg);
						window.scroll(0,0);
						$("input[class~='context']").removeAttr('disabled');
					}
				},
				error: function(XMLHttpRequest, statusText, errorThrown) {
					portalMessage(statusText);
					window.scroll(0,0);
					$("input[class~='context']").removeAttr('disabled');
				},
			};
			$('#analysisrequest_edit_form').ajaxForm(options);
		}

		// these go here so that popup windows can access them in our context
		window.recalc_prices = recalc_prices;
		window.toggleCat = toggleCat;

	});
});
