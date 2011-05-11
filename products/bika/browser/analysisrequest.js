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

/* 
When a user selects a new AnalysisRequest profile,
the changes on the rest of the form are applied 
*/
function setProfile(control_id, col){
/* Isolate the profile */
profiles = document.getElementById(control_id);
profile_id =  "arprofiles." + profiles.selectedIndex;
profile = document.getElementById(profile_id);

if (document.getElementById(profile_id) == undefined) {
    return
    }

/* Get the AnalysisServices, and update the object(s) */

expand = profile.getAttribute('expand');
if (expand.length > 0) {
    alert('expand the following categories: ' + expand);
    return;
}
services = profile.value;
var ServiceArray = services.split(";");
var analysis_prefix = col + ".analysis.";
var prefix = 'ar.' + col;
var subtotal = 0;
var vat = 0;
var total = 0;
var idx = 0;

var selectedservices = document.getElementById(prefix + ".selectedservices");
var selectedArray = selectedservices.value.split(",");

for (idx = 0;idx < selectedArray.length;idx++)
{
    s_idx = parseInt(selectedArray[idx]);
    analysisid = analysis_prefix + s_idx;
    analysis = document.getElementById(analysisid);
    if (analysis) 
        { analysis.checked = false } 
}

var sel_list = ""
var list_splitter = "";
for (idx = 0;idx < ServiceArray.length;idx++)
{
    a_idx = parseInt(ServiceArray[idx]);
    analysisid = analysis_prefix + a_idx;
    analysis = document.getElementById(analysisid);
    analysis.checked = true; 

    price_elem = getElem("id", "Prices." + a_idx, null)
    price = parseFloat(price_elem.value);
    vat_amount = parseFloat(price_elem.getAttribute('vat_amount'));
    total_price = parseFloat(price_elem.getAttribute('total_price'));
    subtotal = subtotal + price;
    vat = vat + vat_amount;
    total = total + total_price;

    sel_list = sel_list + list_splitter + a_idx;
    list_splitter = ",";
} 
selectedservices.value = sel_list;

subtotal_fld = getElem("id", prefix + ".Subtotal", null)
subtotal_fld.value = subtotal.toFixed(2)
subtotal_h_fld = getElem("id", prefix + ".Subtotal_hidden", null)
subtotal_h_fld.value = subtotal.toFixed(2)

vat_fld = getElem("id", prefix + ".VAT" , null)
vat_fld.value = vat.toFixed(2)
vat_h_fld = getElem("id", prefix + ".VAT_hidden", null)
vat_h_fld.value = vat.toFixed(2)

total_fld = getElem("id", prefix + ".Total", null)
total_fld.value = total.toFixed(2)
total_h_fld = getElem("id", prefix + ".Total_hidden", null)
total_h_fld.value = total.toFixed(2)

}

function selectService(column, as_no) {
/* first reset the selected profile */
profile_elem=document.getElementById('ar.' + column + '.arprofiles')
profile_elem.options.selectedIndex = 0

subtotal = getElem("id", "ar." + column + ".Subtotal", null)
subtotal_h = getElem("id", "ar." + column + ".Subtotal_hidden", null)
subtot_price = parseFloat(subtotal.value)

vat = getElem("id", "ar." + column + ".VAT", null)
vat_h = getElem("id", "ar." + column + ".VAT_hidden", null)
vat_price = parseFloat(vat.value)

total = getElem("id", "ar." + column + ".Total", null)
total_h = getElem("id", "ar." + column + ".Total_hidden", null)
tot_price = parseFloat(total.value)

analysis = getElem("id", column + ".analysis." + as_no, null)
price_elem = getElem("id", "Prices." + as_no, null)

item_price = parseFloat(price_elem.value);
item_vatamount = parseFloat(price_elem.getAttribute('vat_amount'));
item_total_price = parseFloat(price_elem.getAttribute('total_price'));

var selectedservices = document.getElementById("ar." + column + ".selectedservices");
var sel_list = selectedservices.value;

if (analysis.checked) {
    subtot_price = subtot_price + item_price;
    vat_price = vat_price + item_vatamount;
    tot_price = tot_price + item_total_price;
    if (sel_list == '')
      { sel_list = as_no }
    else
      { sel_list = sel_list + "," + as_no }
    selectedservices.value = sel_list;
}
else {
    subtot_price = subtot_price - item_price;
    vat_price = vat_price - item_vatamount;
    tot_price = tot_price - item_total_price;
    var list_splitter = "";
    var selectedArray = sel_list.split(",");
    sel_list = "";
    for (idx = 0;idx < selectedArray.length;idx++)
    {
        if (parseInt(selectedArray[idx]) != parseInt(as_no))
        {
            sel_list = sel_list + list_splitter + selectedArray[idx];
            list_splitter = ",";
        }
    }
    selectedservices.value = sel_list;
}

subtotal.value = subtot_price.toFixed(2)
subtotal_h.value = subtot_price.toFixed(2)
vat.value = vat_price.toFixed(2)
vat_h.value = vat_price.toFixed(2)
total.value = tot_price.toFixed(2)
total_h.value = tot_price.toFixed(2)

return
}
function recalcPrice(as_no) {
price_elem = getElem("id", "Prices." + as_no, null)

old_price = parseFloat(price_elem.getAttribute('old_price'));
old_vatamount = parseFloat(price_elem.getAttribute('vat_amount'));
old_totalprice = parseFloat(price_elem.getAttribute('total_price'));

item_price = parseFloat(price_elem.value);
item_vatperc = parseFloat(price_elem.getAttribute('vat')); 
item_vatamount = item_price * item_vatperc / 100;
item_totalprice = item_price + item_vatamount;

price_elem.value = item_price.toFixed(2);
price_elem.setAttribute('vat_amount', item_vatamount.toFixed(2));
price_elem.setAttribute('total_price', item_totalprice.toFixed(2));
price_elem.setAttribute('old_price', item_price.toFixed(2));
price_elem.setAttribute('old_vatamount', item_vatamount.toFixed(2));

req = 0;
ser = 0;

for (req=0;req<999;req++) {
    elem = req + ".analysis." + as_no;
    if (document.getElementById(elem) == undefined) {
        break;
    }
    analysis = getElem("id", elem, null)
    if (analysis.checked) {
        subtotal_id = "ar." + req + ".Subtotal"
        subtotal_elem = getElem("id", subtotal_id, null)
        subtotal_h_elem = getElem("id", subtotal_id+"_hidden", null)
        vat_id = "ar." + req + ".VAT"
        vat_elem = getElem("id", vat_id, null)
        vat_h_elem = getElem("id", vat_id+"_hidden", null)
        total_id = "ar." + req + ".Total"
        total_elem = getElem("id", total_id, null)
        total_h_elem = getElem("id", total_id+"_hidden", null)

        subtotal = subtotal_elem.value;
        subtotal = subtotal - old_price + item_price;  
        vat = vat_elem.value;
        vat = vat - old_vatamount + item_vatamount;
        total = total_elem.value;
        total = total - old_totalprice + item_totalprice;  

        subtotal_elem.value = subtotal.toFixed(2)
        subtotal_h_elem.value = subtotal.toFixed(2)
        vat_elem.value = vat.toFixed(2)
        vat_h_elem.value = vat.toFixed(2)
        total_elem.value = total.toFixed(2)
        total_h_elem.value = total.toFixed(2)
    }
}
return
}

//function to open the client contacts popup window
function open_cc_browser(path)
{
contact_element=document.getElementById('contact');
contact_uid = contact_element.value;
cc_element=document.getElementById('cc_uids');
cc_uids = cc_element.value;
window.open(path + '/select_cc?contact_uid=' + contact_uid + '&cc_uids=' + cc_uids, 'select_cc','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');                 
}


//function to return a reference from the popup window back into the widget
function select_cc( uids, titles)
{
contact_element=document.getElementById('contact');
contact = contact_element.value;

source_id = 'ccu' + contact;
source_element=document.getElementById(source_id);
source=source_element.value;
uids_element=document.getElementById('cc_uids');
uids_element.value=uids;
titles_element=document.getElementById('cc_titles');
titles_element.value=titles;

}

var which_col;
//function to open the samples popup window
function open_sample_browser(path, column)
{
which_col = column;
window.open(path + '/select_sample', 'select_sample','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');                 
}

//function to return a reference from the popup window back into the widget
function select_sample( sampleuid, sampleid, sampletype, samplepoint, clientreference, clientsampleid)
{
incol = which_col;
fieldid='ar.' + incol + '.SampleUID';
s_uid=document.getElementById(fieldid);
s_uid.value=sampleuid;
fieldid='ar.' + incol + '.SampleID';
s_id=document.getElementById(fieldid);
s_id.value=sampleid;
fieldid='SampleIDButton.' + incol;
s_button=document.getElementById(fieldid);
s_button.value=sampleid;
fieldid='ar.' + incol + '.SampleType';
s_type=document.getElementById(fieldid);
s_type.value=sampletype;
s_type.readOnly=true;
fieldid='ar.' + incol + '.SamplePoint';
s_point=document.getElementById(fieldid);
s_point.value=samplepoint;
s_point.readOnly=true;
fieldid='ar.' + incol + '.ClientReference';
c_ref=document.getElementById(fieldid);
c_ref.value=clientreference;
c_ref.readOnly=true;
fieldid='ar.' + incol + '.ClientSampleID';
c_ref=document.getElementById(fieldid);
c_ref.value=clientsampleid;
c_ref.readOnly=true;
fieldid='SampleIDRemoveButton' ;
remove_button=document.getElementById(fieldid);
remove_button.style.visibility="visible";
}

function remove_sample(no_cols)
{
for (i=0; i < no_cols; i++) {
    fieldid='ar.' + i + '.SampleUID';
    s_uid=document.getElementById(fieldid);
    if (s_uid.value == '') {
        continue;
    }
    s_uid.value='';
    fieldid='ar.' + i + '.SampleID';
    s_id=document.getElementById(fieldid);
    s_id.value='';
    fieldid='SampleIDButton.' + i;
    s_button=document.getElementById(fieldid);
    s_button.value='Link...';
    fieldid='ar.' + i + '.SampleType';
    s_type=document.getElementById(fieldid);
    s_type.value='';
    s_type.readOnly=false;
    fieldid='ar.' + i + '.SamplePoint';
    s_point=document.getElementById(fieldid);
    s_point.value='';
    s_point.readOnly=false;
    fieldid='ar.' + i + '.ClientReference';
    c_ref=document.getElementById(fieldid);
    c_ref.value='';
    c_ref.readOnly=false;
    fieldid='ar.' + i + '.ClientSampleID';
    c_ref=document.getElementById(fieldid);
    c_ref.value='';
    c_ref.readOnly=false;
}
fieldid='SampleIDRemoveButton';
remove_button=document.getElementById(fieldid);
remove_button.style.visibility="hidden";
}
function getCC() {
contact_element=document.getElementById('contact');
contact = contact_element.value;

source_id = 'ccu' + contact;
source_element=document.getElementById(source_id);
source=source_element.value;
uids_element=document.getElementById('cc_uids');
uids_element.value=source;
source_id = 'ccn' + contact;
source_element=document.getElementById(source_id);
source=source_element.value;
titles_element=document.getElementById('cc_titles');
titles_element.value=source;

}
function copyValue(field_id, col_count) {

elem=document.getElementById('ar.0.' + field_id);
first_value = elem.value;

for (i=1;i<col_count;i++) {
    other_elem_id = 'ar.' + i + '.' + field_id;
    other_elem=document.getElementById(other_elem_id);
    other_elem.value = first_value;
}
}
function copyChecks(field_id, col_count) {
first_elem=document.getElementById('ar.0.' + field_id);
for (i=1;i<col_count;i++) {
    other_elem_id = 'ar.' + i + '.' + field_id;
    other_elem=document.getElementById(other_elem_id);
    if (first_elem.checked) {
        other_elem.checked = true;
    } else {
        other_elem.checked = false;
    }
}
}
function copyDateSelection(field_id, col_count) {
/* Do year, month and day seperately */
elem=document.getElementById('ar.0.' + field_id + 'Year');
first_index = elem.options.selectedIndex;
for (i=1;i<col_count;i++) {
    other_elem_id = 'ar.' + i + '.' + field_id + 'Year';
    other_elem=document.getElementById(other_elem_id);
    other_elem.options.selectedIndex = first_index
}

elem=document.getElementById('ar.0.' + field_id + 'Month');
first_index = elem.options.selectedIndex;

for (i=1;i<col_count;i++) {
    other_elem_id = 'ar.' + i + '.' + field_id + 'Month';
    other_elem=document.getElementById(other_elem_id);
    other_elem.options.selectedIndex = first_index
}

elem=document.getElementById('ar.0.' + field_id + 'Day');
first_index = elem.options.selectedIndex;
for (i=1;i<col_count;i++) {
    other_elem_id = 'ar.' + i + '.' + field_id + 'Day';
    other_elem=document.getElementById(other_elem_id);
    other_elem.options.selectedIndex = first_index
}
}

function copyProfile(field_id, col_count) {

elem=document.getElementById('ar.0.' + field_id);
first_index = elem.options.selectedIndex;

for (i=1;i<col_count;i++) {
    other_elem_id = 'ar.' + i + '.' + field_id;
    other_elem=document.getElementById(other_elem_id);
    other_elem.options.selectedIndex = first_index;
    setProfile(other_elem_id, i)
}
}

function checkAll(field_id, as_no, col_count) {
all = document.getElementById("all." + as_no);
prefix = 'ar.';

for (i=0;i<col_count;i++) {
/* first reset the selected profiles */
    profile_elem=document.getElementById('ar.' + i + '.arprofiles');
    profile_elem.options.selectedIndex = 0;
    elem=document.getElementById(i + "." + field_id + "." + as_no);
    if (all.checked) {
        if (elem.checked) {
            continue;
        } else {
            elem.checked = true;
            subtotalID   = prefix + i +  ".Subtotal";
            vatID        = prefix +  i + ".VAT";
            totalID      = prefix +  i + ".Total";
            selectService(i, as_no, subtotalID, vatID, totalID);
        }
    } else {
        if (elem.checked) {
            elem.checked = false;
            subtotalID   = prefix + i +  ".Subtotal";
            vatID        = prefix +  i + ".VAT";
            totalID      = prefix +  i + ".Total";
            selectService(i, as_no, subtotalID, vatID, totalID);
        } else {
            continue;
        }
    }
}
}
sampletypearray = new Array(<dtml-in "portal_catalog(portal_type='SampleType', sort_on='sortable_title')">'<dtml-var Title>'<dtml-unless sequence-end>,</dtml-unless></dtml-in>);

samplepointarray = new Array(<dtml-in "portal_catalog(portal_type='SamplePoint', sort_on='sortable_title')">'<dtml-var Title>'<dtml-unless sequence-end>,</dtml-unless></dtml-in>);



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

    // bind 'manage_results submit form 
    $('#manage_results_form').ajaxForm(function() { 
        alert("Success!"); 
    }); 

	
});






});
