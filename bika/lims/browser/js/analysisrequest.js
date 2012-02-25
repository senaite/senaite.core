
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
		var options = {
			type: 'POST',
			async: false,
			beforeSubmit: function(formData, jqForm, options) {
				$("input[class~='context']").attr('disabled',true);
			},
			success: function(responseText, statusText, xhr, $form) {
				$("input[class~='context']").removeAttr('disabled');
			},
			data: {
				'uid': $(element).attr('id'),
				'_authenticator': $('input[name="_authenticator"]').val()},
			error: function(XMLHttpRequest, statusText, errorThrown) {
				portalMessage(statusText);
				window.scroll(0,0);
				$("input[class~='context']").removeAttr('disabled');
			},
			dataType: "json"
		}
		if ($(element).attr("checked") == true){
			// selecting a service; discover services it depends on.
			var affected_services = [];
			var affected_titles = [];
			// actions are discovered and stored in dep_args, until confirmation dialog->Yes.
			var dep_args = [];
			options.url = 'get_service_dependencies';
			options.success = function(pocdata,textStatus,$XHR){
				if (pocdata == null) { return; }
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
			},
			$.ajax(options);
		}
		else {
			// unselecting a service; discover back dependencies
			var affected_titles = [];
			var affected_services = [];
			options.url = 'get_back_references';
			options.success = function(s_uids,textStatus,$XHR){
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
			},
			$.ajax(options);
		}
	}

	function calculate_parts(){
		// Set the little partition number next to service checkboxes

		var uids = [];
		var formvalues = {};
		var partitionable = 0;
		var partitioned_services = $.parseJSON($("#partitioned_services").val());
		// gather up SampleType and all selected service checkboxes by column
		for (var col=0; col<parseInt($("#col_count").val()); col++) {
			var st_title = $("#ar_"+col+"_SampleType").val();
			formvalues[parseInt(col)] = {'st_title':st_title,
										'services': []};
			var checkboxes_checked = $('[name^="ar\\.'+col+'\\.Analyses"]').filter(':checked');
			$.each(checkboxes_checked, function(i,e){
				var uid = $(e).attr('value');
				if(partitioned_services != null
				   && partitioned_services.indexOf(uid) > -1){
					partitionable++;
				}
				formvalues[parseInt(col)]['services'].push(uid);
				uids.push(uid);
			});
		}
		// skip everything if no selected services have partition setup info
		if (partitionable == 0){
			return;
		}
		// all unchecked services have their part numbers removed
		var checkboxes_unchecked = $('[name*="\\.Analyses"]').not(':checked');
		$.each(checkboxes_unchecked, function(i,e){
			pe = $(".partnr_"+$(e).attr('value')).filter("[column="+$(e).attr('column')+"]");
			$(pe).empty();
		});

		// send form values to python
		$.ajax({
			type: 'POST',
			url: $('base').attr('href') + 'getparts',
			data: {'formvalues': $.toJSON(formvalues),
					'_authenticator': $('input[name="_authenticator"]').val()
				},
			success: function(data,textStatus,$XHR){

				// parts[col][ {'services':,'seperate':}, ]
				var colparts = data['parts'];// [{uid:, part:}...]
				for (var col=0; col<parseInt($("#col_count").val()); col++) {
					var parts = colparts[col];
					// unset all checkboxes on columns with less than 2 parts
					// and leave them off
					if(parts.length < 2){
						$.each($('[name^="ar\\.'+col+'\\.Analyses"]').filter(':checked'), function(i,e){
							$(".partnr_"+$(e).attr('value')).filter("[column="+col+"]").empty();
						});
					} else {
						$.each(parts, function(p,part){
							$.each(part['services'], function(s,service_uid){
								$(".partnr_"+service_uid).filter("[column="+col+"]").empty().append(p+1);
							});
						});
					}
				}

			},
			dataType: "json"
		});
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

	function unsetARProfile(column){
		$.each($('input[name^="ar.'+column+'.Analyses"]'), function(){
			if($(this).attr("checked")) $(this).attr("checked", "");
		});
	}

	function setARProfile(){
		profileUID = $(this).val();
		column = $(this).attr("column");
		unsetARProfile(column);
		if(profileUID == "") return;
		selected_elements = [];
		$(".ARProfileCopyButton").toggle(false);
		function success(profile_data){
			// ReportDryMatter gets turned off explicity here
			$("#ar_"+column+"_ReportDryMatter").attr("checked", false);
			$.each(profile_data, function(poc_categoryUID, selectedservices){
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
			$(".ARProfileCopyButton").toggle(true);
			calculate_parts();
		}
		// cached value in #profileUID
		if($("#"+profileUID).length > 0){
			success($.parseJSON($("#"+profileUID).attr('data')));
		} else {
			options = {
				url: 'analysisrequest_profileservices',
				type: 'POST',
				async: false,
				data: {
					'profileUID':profileUID,
					'_authenticator': $('input[name="_authenticator"]').val()
				},
				success: function(data,textStatus,xhr){
					$(".ARProfile").append("<div style='display:none' id='"+profileUID+"' data='"+data+"'>")
					success($.parseJSON(data));
				},
			}
			$.ajax(options);
		}
	}

	function autocomplete_sampletype(request,callback){
		$.getJSON('ajax_sampletypes', {'term':request.term}, function(data,textStatus){
			callback(data);
		});
	}
	// changing sampletype sets partition numbers.
	// it's done funny, because autocomplete didn't like .change()
	// and autocomplete's callback fires at the wrong time.
	$(".sampletype").focus(function(){
		window.sampletype_focus = $(this).val();
	});
	$(".sampletype").blur(function(){
		if ($(this).val() != window.sampletype_focus){
			calculate_parts();
		}
		window.sampletype_focus = '';
	})
	// also set on .change() though,
	// because sometimes we set these fields manually.
	$(".sampletype").change(function(){
		calculate_parts()
	});

	function autocomplete_samplepoint(request,callback){
		$.getJSON('ajax_samplepoints', {'term':request.term}, function(data,textStatus){
			callback(data);
		});
	}

	$(document).ready(function(){

		_ = window.jsi18n;

		// DateSampled field is readonly to prevent invalid data entry, so
		// clicking date_sampled field clears existing values.
		// clear date widget values if the page is reloaded.
		e = $('input[id$="_DateSampled"]');
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
		$(".sampletype").autocomplete({ minLength: 0, source: autocomplete_sampletype});
		$(".samplepoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});
		$("select[class='ARProfile']").change(setARProfile);

		$(".copyButton").live('click',  function (){
			field_name = $(this).attr("name");
			if ($(this).hasClass('ARProfileCopyButton')){ // Profile selector
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
			$.ajax({
				type: 'POST',
				url: 'analysisrequest_contact_ccs',
				data: $(this).val(),
				success: function(data,textStatus,$XHR){
					if (data == null)
						return;
					$('#cc_uids').attr("value", data[0]);
					$('#cc_titles').val(data[1]);
				},
				dataType: "json"
			});
		});
		contact_element = $("#primary_contact");
		if(contact_element.length > 0) {
			contact_element.change();
		}

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
			$("#ar_"+column+"_DateSampled")
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
