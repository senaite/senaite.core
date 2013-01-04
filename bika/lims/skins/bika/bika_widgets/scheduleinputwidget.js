jQuery( function($) {
$(document).ready(function(){

    _ = jarn.i18n.MessageFactory('bika');
    PMF = jarn.i18n.MessageFactory('plone');
    
    fieldName = $('#fieldName').val();
    fromEnabled = $('#'+fieldName+"_fromenabled");
	fromDate = $('#'+fieldName+"_fromdate");
	repeatEnabled = $('#'+fieldName+"_repeatenabled");
	repeatunit = $('#'+fieldName+"_repeatunit");
	repeatperiod = $('#'+fieldName+"_repeatperiod");
	untilEnabled = $('#'+fieldName+"_repeatuntilenabled");
	repeatUntil = $('#'+fieldName+"_repeatuntil");
	
    
	dateFormat = _('date_format_short_datepicker');
	
    fromDate.datepicker({
		dateFormat: dateFormat,
		changeMonth:true,
		changeYear:true,
		yearRange: "-100:+1"
	});
	   
	repeatUntil.datepicker({
		dateFormat: dateFormat,
		changeMonth:true,
		changeYear:true,
		yearRange: "-100:+1"
	});
	
	fromEnabled.click( function(){
	   evaluateFromEnabled();
	});
	
	untilEnabled.click( function(){
		evaluateUntilEnabled();
	});
	
	repeatEnabled.click( function(){
		evaluateRepeatEnabled();
	});
	
	function evaluateFromEnabled() {
		if (fromEnabled.is(':checked')) {
			fromDate.datepicker('enable');	
			fromDate.attr('readonly', false);
			fromDate.focus();
		} else {
			fromDate.datepicker('disable');
			fromDate.attr('readonly', true);
		}
	}	
	
	function evaluateUntilEnabled() {
		if (untilEnabled.is(':checked')) {
			repeatUntil.datepicker('enable');	
			repeatUntil.attr('readonly', false);
			repeatUntil.focus();
		} else {
			repeatUntil.datepicker('disable');
			repeatUntil.attr('readonly', true);
		}
	}	
	
	function evaluateRepeatEnabled() {
		if (repeatEnabled.is(':checked')) {
			repeatunit.attr('readonly', false);
			repeatperiod.attr('disabled', false);
			repeatunit.focus();
		} else {
			repeatunit.attr('readonly', true);
			repeatperiod.attr('disabled', true);
		}
	}
	
	evaluateFromEnabled();
	evaluateRepeatEnabled();
	evaluateUntilEnabled();
});
});