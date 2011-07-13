jQuery( function($) {
	function showMethod(path, service )
	{
	    window.open(path + '/bika_services/' + service + '/analysis_method','analysismethod', 'toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=400,height=400');
	}
	function showPopup(tagID) {
	    element=document.getElementById(tagID)
	    element.style.visibility = "visible";
	}
	function hidePopup(tagID) {
	    element=document.getElementById(tagID)
	    element.style.visibility = "hidden";
	}
	function toggleBoolean(visibleCheckbox, hiddenBoolean)
	{
	 // this function turns a checkbox into a radio button... sort of
	    vis = document.getElementById(visibleCheckbox);
	    hidden = document.getElementById(hiddenBoolean);
	    if (vis.checked) {
	    hidden.value = 1;
	    } else {
	    hidden.value = '';
	    }
	    return true;

	}
	function moveUp(number) {
	    thisElem =  document.getElementById('Pos.' + number);
	    old_value = parseInt(thisElem.value)
	    new_value = old_value - 1;
	    if (new_value == 0) {
	        return
	    }
	    for (var i=1;i<999;i++) {
	        otherName= 'Pos.' + i;
	        if (document.getElementById(otherName) == undefined) {
	            break
	        }
	        otherElem = document.getElementById(otherName);
	        item_value = parseInt(otherElem.value)
	        if (item_value == old_value) {
	            otherElem.value = new_value;
	        } else {
	            if (item_value == new_value) {
	                otherElem.value = new_value + 1;
	            }
	        }
	    }
	    return
	}
	function moveDown(number) {
	    thisElem =  document.getElementById('Pos.' + number);
	    old_value = parseInt(thisElem.value)
	    new_value = old_value + 1;
	    for (var i=1;i<999;i++) {
	        otherName= 'Pos.' + i;
	        if (document.getElementById(otherName) == undefined) {
	            break
	        }
	        otherElem = document.getElementById(otherName);
	        item_value = parseInt(otherElem.value)
	        if (item_value == old_value) {
	            otherElem.value = new_value;
	        } else {
	            if (item_value == new_value) {
	                otherElem.value = new_value - 1;
	            }
	        }
	    }
	    return
	}
	function CalcTotal(){
	    var total_qty = 0.00
	    var subtotal_amount = 0.00
	    var vat_amount = 0.00
	    var total_amount = 0.00

	    subtotal = document.getElementById('Subtotal')
	    totalqty = document.getElementById('Qty')
	    vat = document.getElementById('VAT')
	    total = document.getElementById('Total')

	    form_elements = document.order_form.elements
	    for (var idx=0; idx < form_elements.length; idx++){
	        e = form_elements[idx]
	        if (e.name.indexOf('labproducts') != -1){
	            if (e.value == '') {
	                quantity = 0.00;
	            } else {
	                quantity = parseFloat(e.value);
	            }
	            item_price = parseFloat(e.getAttribute('price')) * quantity;
	            item_total_price = parseFloat(e.getAttribute('totalprice')) * quantity;
	            item_total_id = e.id + '_total';
	            item_total = document.getElementById(item_total_id);
	            item_total.value = item_price.toFixed(2);

	            item_vat = item_total_price - item_price;
	            subtotal_amount = subtotal_amount + item_price;
	            total_amount = total_amount + item_total_price;
	            total_qty = total_qty + quantity;
	        }
	    }

	    vat_amount = total_amount - subtotal_amount
	    subtotal.value = 'R ' + subtotal_amount.toFixed(2)
	    totalqty.value = total_qty
	    vat.value = 'R ' + vat_amount.toFixed(2)
	    total.value = 'R '+ total_amount.toFixed(2)

	    return
	}

	function setStockData(){

	    sst_elem = document.getElementById('stdstock');
	    sst = sst_elem.value;
	    service_elements = document.getElementsByName('Service:list');
	    if (sst == 'None') {
	        today = document.getElementById('today');
	        created = today.value;
	        expiry = '0000/00/00';
	        /* NO stock selected - clear all and make available */
	        for (i=0;i<service_elements.length;i++) {
	            service_elements[i].style.visibility = "visible";
	            service_elements[i].checked = false;
	            uid = service_elements[i].getAttribute('id');
	            document.getElementById(uid + '.result').value = ''
	            document.getElementById(uid + '.result').style.visibility = 'visible';
	            document.getElementById(uid + '.error').value = '';
	            document.getElementById(uid + '.error').style.visibility = 'visible';
	            document.getElementById(uid + '.min').value = '';
	            document.getElementById(uid + '.min').style.visibility = 'visible';
	            document.getElementById(uid + '.max').value = '';
	            document.getElementById(uid + '.max').style.visibility = 'visible';
	        }
	    } else {
	        /* stock selected - unset all values and hide until selected */
	        sst_services = document.getElementById('stdstock.' + sst);
	        services = sst_services.getAttribute('services');
	        results = sst_services.getAttribute('results');
	        created = sst_services.getAttribute('created');
	        if (created == '') {
	            created = '0000/00/00';
	        }
	        expiry = sst_services.getAttribute('expiry');
	        if (expiry == '') {
	            expiry = '0000/00/00';
	        }

	        for (i=0;i<service_elements.length;i++) {
	            service_elements[i].style.visibility = "hidden";
	            service_elements[i].checked = false;
	            uid = service_elements[i].getAttribute('id');
	            document.getElementById(uid + '.result').value = ''
	            document.getElementById(uid + '.result').style.visibility = 'hidden'
	            document.getElementById(uid + '.error').value = ''
	            document.getElementById(uid + '.error').style.visibility = 'hidden'
	            document.getElementById(uid + '.min').value = ''
	            document.getElementById(uid + '.min').style.visibility = 'hidden'
	            document.getElementById(uid + '.max').value = ''
	            document.getElementById(uid + '.max').style.visibility = 'hidden'
	        }
	        var ServiceArray = results.split(":");
	        for ( var i=0;i<ServiceArray.length - 1;i++) {
	            ResultsArray = ServiceArray[i].split(";");
	            analysis_uid = ResultsArray[0];
	            if (document.getElementById(analysis_uid) == undefined){
	                alert('Analysis service not found - please expand categories');
	                continue
	            }
	            analysis = document.getElementById(analysis_uid);
	            analysis.style.visibility = "visible";
	            analysis.checked = true;
	            result = document.getElementById(analysis_uid + '.result');
	            result.value = ResultsArray[1];
	            result.style.visibility = "visible"
	            error = document.getElementById(analysis_uid + '.error');
	            error.value = '';
	            error.style.visibility = "visible"
	            min = document.getElementById(analysis_uid + '.min');
	            min.value = ResultsArray[2];
	            min.style.visibility = "visible"
	            max = document.getElementById(analysis_uid + '.max');
	            max.value = ResultsArray[3];
	            max.style.visibility = "visible"

	        }
	    }

	    var DateArray = created.split("/");
	    year = document.getElementById('search_DateSampled_0_year');
	    year.value = DateArray[0];
	    month = document.getElementById('search_DateSampled_0_month');
	    month.value = DateArray[1];
	    day = document.getElementById('search_DateSampled_0_day');
	    day.value = DateArray[2];
	    date = document.getElementById('search_DateSampled_0');
	    date.value = created;

	    var DateArray = expiry.split("/");
	    year = document.getElementById('search_ExpiryDate_None_year');
	    year.value = DateArray[0];
	    month = document.getElementById('search_ExpiryDate_None_month');
	    month.value = DateArray[1];
	    day = document.getElementById('search_ExpiryDate_None_day');
	    day.value = DateArray[2];
	    date = document.getElementById('search_ExpiryDate_None');
	    date.value = expiry;

	    return
	}
	function toggleResults(uid) {
	    service = document.getElementById(uid);
	    result = document.getElementById(uid + '.result');
	    error = document.getElementById(uid + '.error');
	    min = document.getElementById(uid + '.min');
	    max = document.getElementById(uid + '.max');
	    if (service.checked) {
	        result.style.visibility = "visible"
	        error.style.visibility = "visible"
	        min.style.visibility = "visible"
	        max.style.visibility = "visible"
	    } else {
	        result.style.visibility = "hidden"
	        result.value = ""
	        error.style.visibility = "hidden"
	        error.value = ""
	        min.style.visibility = "hidden"
	        min.value = ""
	        max.style.visibility = "hidden"
	        max.value = ""
	    }
	    return
	}
	function formatFloat(pFloat, pDp){
	    var m = Math.pow(10, pDp);
	    return parseInt(pFloat * m, 10) / m;
	}

	function calcMinMax(uid) {
	    valid = true
	    elem = document.getElementById(uid + '.result');
	    if (elem.value) {
	        if (isNaN(elem.value)) {
	            valid = false;
	        } else {
	            result = parseFloat(elem.value);
	        }
	    } else {
	        valid = false
	    }

	    elem = document.getElementById(uid + '.error');
	    if (elem.value) {
	        if (isNaN(elem.value)) {
	            valid = false;
	        } else {
	            error = parseFloat(elem.value);
	        }
	    } else {
	        valid = false
	    }


	    min = document.getElementById(uid + '.min');
	    max = document.getElementById(uid + '.max');
	    if (valid) {
	        value = result - (error / 100 * result);
	        formatted = formatFloat(value, 3);
	        min.value = formatted;
	        value = result + (error / 100 * result);
	        formatted = formatFloat(value, 3);
	        max.value = formatted;

	    } else {
	        min.value = '';
	        max.value = '';
	    }
	    return
	}

	function clearError(uid) {
	    error = document.getElementById(uid + '.error');
	    error.value = '';
	    return
	}
	function clearService() {
	    service = document.getElementById('getServiceUID');
	    service.value = '';
	    return
	}
	function enableAddAttachment(this_field) {
	    attachfile = document.getElementById('AttachFile').value
	    service = document.getElementById('Service').value
	    analysis = document.getElementById('Analysis').value

	    if (this_field == 'Analysis') {
	        document.getElementById('Service').value = '';
	    }
	    if (this_field == 'Service') {
	        document.getElementById('Analysis').value = '';
	    }

	    document.getElementById('addButton').disabled = false;
	    if (attachfile == '') {
	        document.getElementById('addButton').disabled = true
	    } else {
	        if ((service == '') && (analysis == '')) {
	            document.getElementById('addButton').disabled = true
	        }
	    }

	    return
	}


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

	$(document).ready(function(){

		// All jquery autocomplete widgets get a down-arrow keypress when clicked
	//	this is terrible
	//	$("input[class~='ui-autocomplete-input']").live('click', function(){
	//		$(this).trigger({type:'keydown', which:40});
	//		$(this).trigger({type:'keyup', which:40});
	//	});


	});

});


