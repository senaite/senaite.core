
jQuery( function($) {
	
	function autofill(analysisService)
	{
		fieldName = '';
		if (document.getElementById('copyTF').checked) {
			analysisType = analysisService.split('.')[0];
			initValue=document.getElementById(analysisService).value;
			for (var i=1;i<999;i++) {
				otherElem=analysisType + '.' + i;
				if (document.getElementById(otherElem) == undefined) {
					break
				}
				document.getElementById(otherElem).value = initValue;
				/* need to calculate result, as the value changed */
				fieldName = getFieldName(otherElem);
				calcT(fieldName);
			}
		}
		else {
			/* still need to calculate result, as the value changed */
			fieldName = getFieldName(analysisService);
			calcT(fieldName);
		}
	}

	function getFieldName(fieldID)
	{
		changedField = document.getElementById(fieldID);
		fieldName = changedField.attributes.getNamedItem("name").value;
		fieldName = fieldName.split('.')[1];
		return fieldName;
		
	}

	function calcResult(id)
	{
		ct_id = id + '.CalcType';
		ct_field = document.getElementById(ct_id);
		calc_type = ct_field.value;
		if (calc_type == 't') {
			calcT(id)
		}
		if (calc_type == 'rw') {
			calcRW_WL(id, 'rw')
		}
		if (calc_type == 'rwt') {
			calcRWT_WLT(id, 'rwt')
		}
		if (calc_type == 'wl') {
			calcRW_WL(id, 'wl')
		}
		if (calc_type == 'wlt') {
			calcRWT_WLT(id, 'wlt')
		}
	}

	function calcT(id)
	{
		/* using element name, as element ID is used by autofill() in worksheets */
		tVolFieldName= 'results.' + id + '.TitrationVolume:record';
		tVolField = document.getElementsByName(tVolFieldName)[0];
		tVol = tVolField.value; 
		tFacFieldName = 'results.' + id + '.TitrationFactor:record';
		tFacField = document.getElementsByName(tFacFieldName)[0];
		tFac = tFacField.value; 
		if ((tVol == '') || (tFac == '' )) {  
			result = '';
		} else {
			result =  tVol* tFac;
			if (isNaN(result)) {
				result = '';
			} else {
				result =  Math.round(result*Math.pow(10,2))/Math.pow(10,2);
			}
		}
		resFieldName = 'results.' + id + '.Result:record';
		resultField = document.getElementsByName(resFieldName)[0];
		resultField.value = result;
	}
	function calcRW_WL(id, calctype)
	{
		/* using element name, as element ID is used by autofill() in worksheets */
		resFieldName = 'results.' + id + '.Result:record';
		resultField = document.getElementsByName(resFieldName)[0];

		grossFieldName= 'results.' + id + '.GrossMass:record';
		grossField = document.getElementsByName(grossFieldName)[0];
		gross = grossField.value
		if ((gross == '') || (isNaN(gross)) || (gross == 0)) {
			returnResult('', resultField)
			return
		} else {
			gross = parseFloat(grossField.value); 
		}
		netFieldName= 'results.' + id + '.NetMass:record';
		netField = document.getElementsByName(netFieldName)[0];
		net = netField.value
		if ((net == '') || (isNaN(net)) || (net == 0)) {
			returnResult('', resultField)
			return
		} else {
			net= parseFloat(netField.value); 
		}
		vesselFieldName= 'results.' + id + '.VesselMass:record';
		vesselField = document.getElementsByName(vesselFieldName)[0];
		vessel = vesselField.value
		if ((vessel == '')  || (isNaN(vessel)) || (vessel == 0)) {
			returnResult('', resultField)
			return
		} else {
			vessel = parseFloat(vesselField.value); 
		}

		if ((gross < net) || (net < vessel) || (gross == vessel)) {
			result = ''
		} else {
			if (calctype == 'wl') {
				result = ((gross - net) / (gross - vessel)) * 100
			} else {
				result = ((net - vessel) / (gross - vessel)) * 100
			}
			result =  Math.round(result*Math.pow(10,2))/Math.pow(10,2);
		}
		returnResult(result, resultField)
	}

	function calcRWT_WLT(id, calctype)
	{
		/* using element name, as element ID is used by autofill() in worksheets */
		resFieldName = 'results.' + id + '.Result:record';
		resultField = document.getElementsByName(resFieldName)[0];

		sampleFieldName= 'results.' + id + '.SampleMass:record';
		sampleField = document.getElementsByName(sampleFieldName)[0];
		sample = sampleField.value
		if ((sample == '') || (isNaN(sample)) || (sample == 0)) {
			returnResult('', resultField)
			return
		} else {
			sample = parseFloat(sampleField.value); 
		}
		netFieldName= 'results.' + id + '.NetMass:record';
		netField = document.getElementsByName(netFieldName)[0];
		net = netField.value
		if ((net == '') || (isNaN(net)) || (net == 0)) {
			returnResult('', resultField)
			return
		} else {
			net= parseFloat(netField.value); 
		}
		vesselFieldName= 'results.' + id + '.VesselMass:record';
		vesselField = document.getElementsByName(vesselFieldName)[0];
		vessel = vesselField.value
		if ((vessel == '')  || (isNaN(vessel)) || (vessel == 0)) {
			returnResult('', resultField)
			return
		} else {
			vessel = parseFloat(vesselField.value); 
		}

		if (net < vessel)  {
			result = ''
		} else {
			if (calctype == 'wlt') {
				result = ((vessel + sample - net) / sample) * 100
			} else {
				result = ((net - vessel) / sample) * 100
			}
			result =  Math.round(result*Math.pow(10,2))/Math.pow(10,2);
		}
		returnResult(result, resultField)
	}

	function returnResult(result, resultField) {
		resultField.value = result;
	}

	// XXX price recalc is sometimes over agressive, does a few re-recalcs.
	function recalc_prices(column){
		if(column){
			subtotal = 0.00;
			vat = 0.00;
			total = 0.00;
			discount = parseFloat($("#member_discount").val());
			$.each($('input[name^="ar\\.'+column+'\\.Analyses"]'), function(){
				disabled = $(this).attr('disabled');
				// For some browsers, `attr` is undefined; for others, its false.  Check for both.
				if (typeof disabled !== 'undefined' && disabled !== false) {
					disabled = true;
				} else {
					disabled = false;
				}
				if(!(disabled) && $(this).attr("checked")){
					serviceUID = this.id.split("_")[4];
					price = parseFloat($("input[name^='Prices\\."+serviceUID+"']").val());
					vat_amount = parseFloat($("input[name^='VAT\\."+serviceUID+"']").val());
					if(discount){
						price = price - ((price / 100) * discount);
					}
					subtotal += price;
					vat += ((price / 100) * vat_amount);
					total += price + ((price / 100) * vat_amount);
				}
			});
			$('#ar_'+column+'_subtotal').val(subtotal.toFixed(2));
			$('#ar_'+column+'_subtotal_display').val(subtotal.toFixed(2));
			$('#ar_'+column+'_vat').val(vat.toFixed(2));
			$('#ar_'+column+'_vat_display').val(vat.toFixed(2));
			$('#ar_'+column+'_total').val(total.toFixed(2));
			$('#ar_'+column+'_total_display').val(total.toFixed(2));
		} else {
			for (col=0; col<parseInt($("#col_count").val()); col++) {
				recalc_prices(String(col));
			}
		}
	};

	function toggleCat(header_ID, selectedservices, column, force_expand, disable){
		// selectedservices and column are optional.
		// force_expand and disable are for secondary ARs
		// They are used when selecting an AR Profile or making a secondary AR
		
		if(force_expand == undefined){ force_expand = false ; } 
		if(disable == undefined){ disable = -1 ; } 

		name = $('#'+header_ID).attr("name");
		tbody = $('#'+name+"_tbody");
		categoryUID = name.split("_")[0];
		poc = name.split("_")[1];
		if(!column && column != 0) { column = ""; }
		if($('#'+header_ID).hasClass("expanded")){
			// displaying and completing an an already expanded category
			// for an ARProfile selection; price recalc happens in setARProfile()
			if(selectedservices){
				$.each($('input[id^="ar_'+column+'_'+categoryUID+'_'+poc+'_"]'), function(){
					if(selectedservices.indexOf($(this).attr("id").split("_")[4]) > -1){
						$(this).attr("checked", "checked");
					}
				});
				recalc_prices(column);
				tbody.toggle(true); 
			} else { 
				if (force_expand){ tbody.toggle(true); }
				else { tbody.toggle(); }
			}
		} else {
			if(!selectedservices) selectedservices = [];
			$('#'+header_ID).addClass("expanded");
			var options ={
					'selectedservices': selectedservices.join(","),
					'categoryUID': categoryUID,
					'column': column,
					'disable': disable > -1 ? column : -1,
					'col_count': $("#col_count").attr('value'),
					'poc': poc
			};
			tbody.load("analysisrequest_analysisservices", options,
				function(){
					// changing the  price of a service
					$("input[class='price']").unbind();
					$("input[class='price']").bind('change', service_price_change);
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
	
	function calcdependencies(elements){
		unexpanded_cats_ = [];
		expanded_cats_ = [];
		unchecked_depIDs_ = [];
		unchecked_depUIDs_ = []
	
		antes = [];
	
		$.each(elements, function(e,element){
			column = element.attr("id").split("_")[1];
			if (element.attr("checked") == true){
				// selecting a service; discover services it depends on.
				depcatIDs_ = element.attr("depcatids").split(",");
				depUIDs_ = element.attr("depuids").split(",");
	
				if(depcatIDs_[0] != ''){
					$.each(depcatIDs_, function(c,depcatID){
						if($('#'+depcatID).attr('class').indexOf("expanded") > -1){
							expanded_cats_.push(depcatID);
						} else{
							unexpanded_cats_.push(depcatID);
						}
						$.each(depUIDs_, function(u,depUID){
							e = $('#ar_'+column+"_"+depcatID+"_"+depUID);
							if((e.attr('id')==undefined) || !(e.attr("checked"))){
								unchecked_depIDs_.push('ar_'+column+"_"+depcatID+"_"+depUID);
								unchecked_depUIDs_.push(depUID);
							}
						});
					});
				}
			} else {
				// unselecting a service; discover checked antecedents
				things = element.attr("id").split("_");
				UID = things[4];
				$.each($('input[id*="ar_'+things[1]+'"]'), function(i,v){
					if(($(v).attr("depuids") != undefined) && ($(v).attr("depuids").indexOf(UID) > -1)){
						if($(v).attr("checked")){
							antes.push($(v).attr("id"));
						}
					}
				});
			}
		});
	
		// unique lists
		unexpanded_cats = [];
		expanded_cats = [];
		unchecked_depIDs = [];
		unchecked_depUIDs = [];
		$.each(unexpanded_cats_, function(i,v){ if(unexpanded_cats.indexOf(v) == -1) unexpanded_cats.push(v); });
		$.each(expanded_cats_, function(i,v){ if(expanded_cats.indexOf(v) == -1) expanded_cats.push(v); });
		$.each(unchecked_depIDs_, function(i,v){ if(unchecked_depIDs.indexOf(v) == -1) unchecked_depIDs.push(v); });
		$.each(unchecked_depUIDs_, function(i,v){ if(unchecked_depUIDs.indexOf(v) == -1) unchecked_depUIDs.push(v); });
	
		if (unchecked_depIDs.length > 0){
			$("#confirm_add_deps").dialog({width:450, resizable:false, closeOnEscape: false, buttons:{
				'Yes': function(){
					$.each(elements, function(i,element){
						$.each(unexpanded_cats, function(i,e){
							// expand untouched categories.  This is done async, so the checkbox values
							// are set in the toggle function.  Toggle is called once for each affected column
							col = element.attr("id").split("_")[1];
							toggleCat(e,unchecked_depUIDs, col);
						});
					});
					$.each(expanded_cats, function(i,e){
						// make sure all expanded categories are visible
						name = $('#'+e).attr("name");
						tbody = $('#'+name+"_tbody");
						tbody.toggle(true);
					});
					$.each(unchecked_depIDs, function(i,e){
						// check all dependent checkbox IDs that exist and are unchecked
						if( !($('#'+e).attr("checked")==true) ){
							$('#'+e).attr("checked", true);
						}
					});
					recalc_prices();
					$(this).dialog("close");
				},
				'No':function(){
					$.each(elements, function(i,element){
						element.attr("checked", false);
						column = element.attr("id").split("_")[1];
						recalc_prices(column);
					});
					$(this).dialog("close");
				}
			}});
		}
	
		if (antes.length > 0){
			$("#confirm_remove_antes").dialog({width:450, resizable:false, closeOnEscape: false, buttons:{
				'Yes': function(){
					$.each(antes, function(i,e){
						// check all dependent checkbox IDs that exist and are unchecked
						if( ($('#'+e).attr("checked")==true) ){
							$('#'+e).attr("checked", false);
						}
					});
					recalc_prices();
					$(this).dialog("close");
				},
				'No':function(){
					$.each(elements, function(i,element){
						element.attr("checked", true);
						column = element.attr("id").split("_")[1];
						recalc_prices(column);
					});
					$(this).dialog("close");
				}
			}});
		}
	}
	
	function service_checkbox_change(){
		column = $(this).attr("name").split(".")[1];
		element = $(this);
		if($("#ar_"+column+"_ARProfile").val() != ""){
			$("#ar_"+column+"_ARProfile").val("");
		}
		calcdependencies([element]);
		recalc_prices(column);
	};
	
	function service_price_change(){
		recalc_prices();
	}
	
	function unsetARProfile(column){
		$.each($('input[name^="ar.'+column+'.Analyses"]'), function(){
			if($(this).attr("checked")) $(this).attr("checked", "");
		});
	}

	function setARProfile(){
		profileUID = $(this).val();
		column = $(this).attr("id").split("_")[1];
		if(profileUID == "") return;
		unsetARProfile(column);
		selected_elements = []
		$.getJSON('analysisrequest_profileservices', {'profileUID':profileUID}, function(data,textStatus){
			$.each(data, function(categoryUID_poc, selectedservices){
				toggleCat(categoryUID_poc, selectedservices, column);
				$.each(selectedservices, function(i,uid){
					selected_elements.push($("#ar_"+column+"_"+categoryUID_poc+"_"+uid));
				});
			});
		}, "json");
		calcdependencies(selected_elements);
		recalc_prices(column);
	}
	
	function autocomplete_sampletype(request,callback){
		$.getJSON('analysisrequest_sampletypes', {'term':request.term}, function(data,textStatus){
			callback(data);
		});
	}
	
	function autocomplete_samplepoint(request,callback){
		$.getJSON('analysisrequest_samplepoints', {'term':request.term}, function(data,textStatus){
			callback(data);
		});
	}
	
	$(document).ready(function(){
		$('input[id$="_DateSampled"]').datepicker({'dateFormat': 'yy-mm-dd', showAnim: ''});
		$(".sampletype").autocomplete({ minLength: 0, source: autocomplete_sampletype});
		$(".samplepoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});
		$("select[class='ARProfile']").change(setARProfile);

		// clicking on the td will select the checkbox within
		$(".cb").click(function(){
		});

		// 
		$(".copyButton").live('click',  function (){
			field_name = $(this).attr("name");
			// analysis service checkboxes
			if (this.id.split("_").length == 4) { // ar_(catid)_(poc)_(serviceid)
				things = this.id.split("_");
				first_val = $('#ar_0_'+things[1]+'_'+things[2]+'_'+things[3]).attr("checked");
				affected_elements = [];
				// col starts at 1 here; row 0 is reference value
				for (col=1; col<parseInt($("#col_count").val()); col++) { 
					other_elem = $('#ar_'+col+'_'+things[1]+'_'+things[2]+'_'+things[3]);
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
				calcdependencies(affected_elements);
				recalc_prices();
			}
			// other checkboxes
			else if ($('input[name^="ar\\.0\\.'+field_name+'"]').attr("type") == "checkbox") { 
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

		// service category expanding rows for all AR forms
		$('tr[class^="analysiscategory"]').click(function(){
			toggleCat($(this).attr("id"));
		});

		// service category pre-expanded rows
		// These are in AR Edit only
		selected_elements = [];
		prefilled = false;
		selected_services = $("#selectedservices").val();
		if(selected_services == undefined){
			selected_services = "";
		} else {
			selected_services = selected_services.split(",");
		}
		$.each($('tr[class$="prefill"]'), function(i,e){
			prefilled = true;
			toggleCat($(e).attr("id"), selected_services, 0); // AR Edit has only column 0
			selected_elements.push($(e));
		});
		if (prefilled){
			calcdependencies(selected_elements);
			recalc_prices();
		}

		// Contact dropdown changes
		$("#contact").live('change', function(){
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
		$("#contact").change();
 
		// recalculate when price elements' values are changed
		$("input[name^='Price']").live('change', function(){
			recalc_prices();
		});
	
		// A button in the AR form displays the CC browser window (select_cc.pt)
		$('#open_cc_browser').click(function(){
			contact_uid = $('#contact').attr('value');
			cc_uids = $('#cc_uids').attr('value');
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

		// return a reference from the Sample popup window back into the widget 
		// and populate the form with this sample's data 
		$('.select_sample_select').click(function(){
			item_data = $.parseJSON($(this.parentNode).attr("item_data"));
			column = item_data['column'];
			window.opener.$("#ar_"+column+"_SampleID_button").val(item_data['SampleID']);
			window.opener.$("#ar_"+column+"_SampleID").val(item_data['SampleID']);
			window.opener.$("#deleteSampleButton_" + column).toggle(true);
			window.opener.$("#ar_"+column+"_DateSampled").val(item_data['DateSampled']).attr('readonly', true);
			window.opener.$("#ar_"+column+"_DateSampled").unbind();
			window.opener.$("#ar_"+column+"_ClientReference").val(item_data['ClientReference']).attr('readonly', true);
			window.opener.$("#ar_"+column+"_ClientSampleID").val(item_data['ClientSampleID']).attr('readonly', true);
			window.opener.$("#ar_"+column+"_SampleType").val(item_data['SampleType']).attr('readonly', true);
			window.opener.$("#ar_"+column+"_SamplePoint").val(item_data['SamplePoint']).attr('readonly', true);
			// handle samples that do have field analyses
			// field_analyses is a dict of lists: { catuid: [serviceuid,serviceuid], ... }
			if(item_data['field_analyses'] != null){
				$.each(item_data['field_analyses'], function(catuid,serviceuids){
					window.opener.toggleCat(catuid + "_field", serviceuids, column, true, true);
				});
			}
			// explicitly check that field categories are expanded
			// and disabled even if eg there are no field analyses for this sample
			$.each(window.opener.$("tr[id*='_field']").filter(".analysiscategory"), function(){
				window.opener.toggleCat(this.id, false, column, true, true);
			});

			$.each(window.opener.$('input[id*="_field_"]').filter(".cb"), function(i,e){
				if ($(e).attr('id').indexOf('_'+column+'_') > -1){
					$(e).attr('disabled', true);
				}
			});
			window.opener.recalc_prices();
			window.close();
		});
		
		$(".deleteSampleButton").click(function(){
			column = $(this).attr('column');
			$("#ar_"+column+"_SampleID_button").val($("#ar_"+column+"_SampleID_default").val());
			$("#ar_"+column+"_SampleID").val('');
			$("#ar_"+column+"_ClientReference").val('').removeAttr("readonly");
			$("#ar_"+column+"_DateSampled").val('').removeAttr("readonly");
			$("#ar_"+column+"_DateSampled").datepicker({'dateFormat': 'yy-mm-dd'});
			$("#ar_"+column+"_ClientSampleID").val('').removeAttr("readonly");
			$("#ar_"+column+"_SamplePoint").val('').removeAttr("readonly");
			$("#ar_"+column+"_SampleType").val('').removeAttr("readonly");
			$("#deleteSampleButton_" + column).toggle(false);
			// uncheck and enable all visible service checkboxes
			$("input[id*='_"+column+"_']").filter(".cb").removeAttr('disabled').attr('checked', false);
			recalc_prices();
		});

		function portalMessage(message){
			str = "<dl class='portalMessage error'>"+
					"<dt i18n:translate='error'>Error</dt>"+
					"<dd><ul>" + message +
					"</ul></dd></dl>";
					$('.portalMessage').remove();
					$(str).appendTo('#viewlet-above-content');
		}

		// AR Add/Edit ajax form submits
		var options = { 
			url: window.location.href,
			dataType:  'json', 
			data: $(this).formToArray(),
			beforeSubmit: function(formData, jqForm, options) {
				$("input[class~='context']").attr('disabled',true);
				$("#spinner").toggle(true);
			},
			complete: function(XMLHttpRequest, textStatus) {
				$("input[class~='context']").removeAttr('disabled');
				$("#spinner").toggle(false);
			},
			success: function(responseText, statusText, xhr, $form)  {  
				if(responseText['success'] != undefined){
					window.location.replace(window.location.href.replace("/analysisrequest_add",""));
				}
				msg = ""
				if(responseText['errors'] != undefined){
					for(error in responseText['errors']){
						x = error.split(".");
						if (x.length == 2){
							e = x[1] + " (Column " + x[0] + "): ";
						} else {
							e = "";
						}
						msg = msg + e + responseText['errors'][error] + "<br/>";
					};
					portalMessage(msg);
				}
				window.scroll(0,0);
			},
			error: function(XMLHttpRequest, statusText, errorThrown) {
				portalMessage(statusText);
			},
		};
		$('#analysisrequest_edit_form').ajaxForm(options);

		// these go here so that popup windows can access them in our context
		window.recalc_prices = recalc_prices;
		window.toggleCat = toggleCat;

	});

});
