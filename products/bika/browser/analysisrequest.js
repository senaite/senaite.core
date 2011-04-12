function recalc_prices(column){
	if(column){
		vat_amount = parseFloat(jq("#vat_amount").val());
		subtotal = 0.00;
		vat = 0.00;
		total = 0.00;
		jq.each(jq('input[name^="ar\\.'+column+'\\.Analyses"]'), function(){
			if(jq(this).attr("checked")){
				serviceUID = this.id.split("_")[4];
				price = parseFloat(jq("input[name^='Prices\\."+serviceUID+"']").val());
				subtotal += price;
				vat += ((price / 100) * vat_amount);
				total += (price + ((price / 100) * vat_amount));
			}
		});
		jq('#ar_'+column+'_subtotal').val(subtotal.toFixed(2));
		jq('#ar_'+column+'_subtotal_display').val(subtotal.toFixed(2));
		jq('#ar_'+column+'_vat').val(vat.toFixed(2));
		jq('#ar_'+column+'_vat_display').val(vat.toFixed(2));
		jq('#ar_'+column+'_total').val(total.toFixed(2));
		jq('#ar_'+column+'_total_display').val(total.toFixed(2));
	} else {
		for (col=0; col<parseInt(jq("#col_count").val()); col++) {
			recalc_prices(String(col));
		}
	}
};

function service_checkbox_click(){
	column = jq(this).attr("name").split(".")[1];
	if(jq("#ar_"+column+"_ARProfile").val() != ""){
		jq("#ar_"+column+"_ARProfile").val("");
	}
	recalc_prices(column);
};

function service_price_change(){
	//XXX entire recalc not necessary
	recalc_prices();
}

/*
 * 
 *function setARTemplate(thisid, col){

    Data = document.getElementById(ourvalue).value.split("__");
    SampleType    = Data[0];
    SamplePoint   = Data[1];
    ProfileUID    = Data[2];
    Preservations = Data[3].split(";");
    Containers    = Data[4].split(";");

    document.getElementById("ar." + col + ".SampleType").value = SampleType;
    document.getElementById("ar." + col + ".SamplePoint").value = SamplePoint;

    setComposite(col);

    Pselect = document.getElementById("ar." + col + ".Preservation");
    options = Pselect.options;
    for(o=0;o<options.length;o++){
        if(Index(Preservations, options[o].value)>-1){
            options[o].selected = true;
        } else {
            options[o].selected = false;
        }
    }
    Pselect.scrollTop = 0;

    Cselect = document.getElementById("ar." + col + ".Unpreserved");
    options = Cselect.options;
    for(o=0;o<options.length;o++){
        if(Index(Containers, options[o].value)>-1){
            options[o].selected = true;
        } else {
            options[o].selected = false;
        }
    }
    Cselect.scrollTop = 0;

}
*/

function toggleCat(header_element, selectedservices, column){
	// selectedservices and column are optional. They are used when AR Profile is selected.
	name = jq(header_element).attr("name");
	tbody = jq('#'+name+"_tbody");
	categoryUID = name.split("_")[0];
	poc = name.split("_")[1];
	if(jq(header_element).hasClass("expanded")){
		// displaying and completing an an already expanded category
		// for an ARProfile selection; price recalc happens in setARProfile()
		if(selectedservices){
			tbody.toggle(true);
			jq.each(jq('input[id^="ar_'+column+'_'+categoryUID+'_'+poc+'_"]'), function(){
				if(selectedservices.indexOf(jq(this).attr("id").split("_")[4]) > -1){
					jq(this).attr("checked", "checked");
				}
			});
			recalc_prices();
		} else { 
			tbody.toggle(); 
		}
	} else {
		if(!selectedservices) selectedservices = [];
		if(!column) { column = ""; }
		jq(header_element).addClass("expanded");
		tbody.load("analysisrequest_analysisservices", 
					{'selectedservices': String(selectedservices),
					'categoryUID': categoryUID,
					'column': column,
					'col_count': jq("#col_count").attr('value'),
					'poc': poc},
					function(){
						// changing the  price of a service
						jq("input[class='price']").unbind();
						jq("input[class='price']").bind('change', service_price_change);
						// analysis service checkboxes
						jq('input[name*="Analyses"]').unbind();
						jq('input[name*="Analyses"]').bind('change', service_checkbox_click);
						if(selectedservices!=[]){
							recalc_prices(column);
						}
					}
		);
	}
}

function copyButton(){
	field_name = jq(this).attr("name");
	// analysis service checkboxes
	if (this.id.split("_").length == 4) {
		things = this.id.split("_");
		first_val = jq('#ar_0_'+things[1]+'_'+things[2]+'_'+things[3]).attr("checked");
		for (col=1; col<parseInt(jq("#col_count").val()); col++) {
			other_elem = jq('#ar_'+col+'_'+things[1]+'_'+things[2]+'_'+things[3]);
			if (!(other_elem.disabled)) {
				other_elem.attr("checked", first_val?true:false);
				other_elem.change();
			}
		}
	}
	// other checkboxes
	else if (jq('input[name^="ar\\.0\\.'+field_name+'"]').attr("type") == "checkbox") { 
		first_val = jq('input[name^="ar\\.0\\.'+field_name+'"]').attr("checked");
		for (col=0; col<parseInt(jq("#col_count").val()); col++) {
			other_elem = jq('#ar_' + col + '_' + field_name);
			if (!(other_elem.attr("disabled"))) {
				other_elem.attr("checked", first_val?true:false);
				other_elem.change();
			}
		}
	}
	else{
		first_val = jq('input[name^="ar\\.0\\.'+field_name+'"]').val();
		for (col=0; col<parseInt(jq("#col_count").val()); col++) {
			other_elem = jq('#ar_' + col + '_' + field_name);
			if (!(other_elem.attr("disabled"))) {
				other_elem.val(first_val);
				other_elem.change();
			}
		}
	}
};

// function to return a reference from the CC popup window back into the widget 
function select_cc(uids, titles){
	jq("#cc_uids").val(uids);
	jq("#cc_titles").val(titles);
}

// function to return a reference from the Sample popup window back into the widget 
function select_sample(column, sampleID){
	jq("#ar_"+column+"_SampleID").val(SampleID);
}

function unsetARProfile(column){
	jq.each(jq('input[name^="ar.'+column+'.Analyses"]'), function(){
		if(jq(this).attr("checked")) jq(this).attr("checked", "");
	});
}

function setARProfile(){
	profileUID = jq(this).val();
	column = jq(this).attr("id").split("_")[1];
	// if "None" profile is selected, do nothing
	if(profileUID == "") return;
	// uncheck all checks in this column
	unsetARProfile(column);
	jq.getJSON('analysisrequest_profileservices', {'profileUID':profileUID}, function(data,textStatus){
		jq.each(data, function(categoryUID_poc, selectedservices){
			toggleCat(jq('#'+categoryUID_poc), selectedservices, column);
		});
	}, "json");
	recalc_prices(column);
}

function autocomplete_sampletype(request,callback){
	jq.getJSON('analysisrequest_sampletypes', {'term':request.term}, function(data,textStatus){
		callback(data);
	});
}

function autocomplete_samplepoint(request,callback){
	jq.getJSON('analysisrequest_samplepoints', {'term':request.term}, function(data,textStatus){
		callback(data);
	});
}

jq(document).ready(function(){
	// jquery-ui date picker
	jq('input[id$="_DateSampled"]').datepicker();

	// copy buttons
	jq(".copyButton").live('click', copyButton);

	// any changes to ARProfile dropdown
	jq("select[class='ARProfile']").change(setARProfile);

	// service category expanding rows
	jq('th[class^="analysiscategory"]').click(function(){
		toggleCat(this);
	});

	// service category pre-expanded rows
	prefill = jq('tr[class$="prefill"]');
	for(i=0;i<prefill.length;i++){
		toggleCat(this);
		if(i==prefill.length-1){ 
			recalc_prices();
		}
	}

	// A button in the AR form displays the CC browser window (select_cc.pt)
	jq('#open_cc_browser').click(function(){
		contact_uid = jq('#contact').attr('value');
		cc_uids = jq('#cc_uids').attr('value');
		window.open('analysisrequest_select_cc?contact_uid=' + contact_uid + '&cc_uids=' + cc_uids, 'analysisrequest_select_cc','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');
	});

	// analysisrequest_select_cc.pt submit button invokes this
	jq('#cc_browser_submit').click(function(){
		var uids = [];
		var titles = [];
		jq.each(jq('input[id^="Contact\\."]'), function() {
			if(jq(this).attr("checked")){
				uids.push(jq(this).attr("selected_uid"));
				titles.push(jq(this).attr("selected_title"));
			}
		});
		// we pass comma seperated strings with uids and titles
		window.opener.select_cc(uids.join(','), titles.join(','));
		window.close();
	});

	// button to display Sample browser window
	jq('input[id$="_SampleID"]').click(function(){
		column = this.id.split("_")[1];
		window.open('analysisrequest_select_sample?column=' + column, 'sanalysisrequest_select_sample','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');
	});

	// analysisrequest_select_cc.pt submit button invokes this
	jq('#sample_browser_submit').click(function(){
		var uids = [];
		var titles = [];
		jq.each(jq('input[id^="Contact\\."]'), function() {
			if(jq(this).attr("checked")){
				uids.push(jq(this).attr("selected_uid"));
				titles.push(jq(this).attr("selected_title"));
			}
		});
		// we pass comma seperated strings with uids and titles
		window.opener.select_cc(uids.join(','), titles.join(','));
		window.close();
	});

	jq(".sampletype").autocomplete({ minLength: 0,
		                source: autocomplete_sampletype});
	jq(".samplepoint").autocomplete({ minLength: 0,
		                source: autocomplete_samplepoint});

});
 