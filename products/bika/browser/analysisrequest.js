jQuery( function($) {
	
	
// XXX price recalc is sometimes over agressive, does a few re-recalcs.
function recalc_prices(column){
	if(column){
		subtotal = 0.00;
		vat = 0.00;
		total = 0.00;
		discount = parseFloat($("#member_discount").val());
		$.each($('input[name^="ar\\.'+column+'\\.Analyses"]'), function(){
			if($(this).attr("checked")){
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

function toggleCat(header_ID, selectedservices, column){
	// selectedservices and column are optional. They are used when AR Profile is selected.
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
			tbody.toggle(); 
		}
	} else {
		if(!selectedservices) selectedservices = [];
		$('#'+header_ID).addClass("expanded");
		tbody.load("analysisrequest_analysisservices", 
			{'selectedservices': selectedservices.join(","),
			'categoryUID': categoryUID,
			'column': column,
			'col_count': $("#col_count").attr('value'),
			'poc': poc},
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

function copyButton(){
	field_name = $(this).attr("name");
	// analysis service checkboxes
	if (this.id.split("_").length == 4) { // ar_(catid)_(poc)_(serviceid)
		things = this.id.split("_");
		first_val = $('#ar_0_'+things[1]+'_'+things[2]+'_'+things[3]).attr("checked");
		affected_elements = [];
		// col starts at 1 here; we don't copy into the the first row
		for (col=1; col<parseInt($("#col_count").val()); col++) { 
			other_elem = $('#ar_'+col+'_'+things[1]+'_'+things[2]+'_'+things[3]);
			if (!(other_elem.disabled) && !(other_elem.attr("checked")==first_val)) {
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
			if (!(other_elem.disabled) && !(other_elem.attr("checked")==first_val)) {
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
};

// function to return a reference from the CC popup window back into the widget 
function select_cc(uids, titles){
	$("#cc_uids").val(uids);
	$("#cc_titles").val(titles);
}

// function to return a reference from the Sample popup window back into the widget 
function select_sample(column, sampleID){
	$("#ar_"+column+"_SampleID").val(SampleID);
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
	$('input[id$="_DateSampled"]').datepicker({'dateFormat': 'yy-mm-dd'});
	$(".copyButton").live('click', copyButton);
    $(".sampletype").autocomplete({ minLength: 0, source: autocomplete_sampletype});
    $(".samplepoint").autocomplete({ minLength: 0, source: autocomplete_samplepoint});
	$("select[class='ARProfile']").change(setARProfile);

	// service category expanding rows for all AR forms
	$('tr[class^="analysiscategory"]').click(function(){
		toggleCat($(this).attr("id"));
	});

	// service category pre-expanded rows
	// These are in AR Edit only
    selected_elements = []
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
		window.open('analysisrequest_select_cc?contact_uid=' + contact_uid + '&cc_uids=' + cc_uids, 
			'analysisrequest_select_cc','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');
	});

	// analysisrequest_select_cc.pt submit button invokes this
	$('#cc_browser_submit').click(function(){
		var uids = [];
		var titles = [];
		$.each($('input[id^="Contact\\."]'), function() {
			if($(this).attr("checked")){
				uids.push($(this).attr("selected_uid"));
				titles.push($(this).attr("selected_title"));
			}
		});
		// we pass comma seperated strings with uids and titles
		window.opener.select_cc(uids.join(','), titles.join(','));
		window.close();
	});

	// button to display Sample browser window
	$('input[id$="_SampleID"]').click(function(){
		column = this.id.split("_")[1];
		window.open('analysisrequest_select_sample?column=' + column, 
			'sanalysisrequest_select_sample','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');
	});

	// analysisrequest_select_cc.pt submit button invokes this
	$('#sample_browser_submit').click(function(){
		var uids = [];
		var titles = [];
		$.each($('input[id^="Contact\\."]'), function() {
			if($(this).attr("checked")){
				uids.push($(this).attr("selected_uid"));
				titles.push($(this).attr("selected_title"));
			}
		});
		// we pass comma seperated strings with uids and titles
		window.opener.select_cc(uids.join(','), titles.join(','));
		window.close();
	});

});




});
